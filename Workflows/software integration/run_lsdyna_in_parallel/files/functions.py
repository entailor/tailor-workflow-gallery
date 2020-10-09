import glob
import subprocess
import numpy as np
import dynapack.LSwrite as LSw
from fnmatch import filter as fltr

from dynapack.LSpost import readrcforc, readnodout
import matplotlib.pyplot as plt


""" Functions for post-processing of LS-DYNA files """

def readrcforc( Inputfilename):
    """ Function to read rcforc files from LS-DYNA

     Run as
       rc = readrcforc('rcforc')
     Plot as
      plt.plot(rc[contactID,forcedir,:])
    """

    ncontacts=0
    contactnames = []

    f = open(Inputfilename,'r')
    for i in range(0,5):  dummy = f.readline()

    # Read to find number of contacts
    temp=0
    while temp>-1:
        line = f.readline()
        if 'END' in line:
            temp =  -5
            line = f.readline()
        else:
            ncontacts = ncontacts + 1
            s=' '
            seq = line.strip().split()[1:]
            contactnames.append(s.join(seq))

    # Create 2d list for data storage
    rcforc= [[] for i in range(ncontacts)]

    # Read reaction forces for each contact
    temp=0
    while temp>-1:
        for i in range(0,ncontacts*2):
            line = f.readline()
            if 'master' in line:
                #print line
                contactID = int(float(line.strip().split()[1]))
                time = float(line.strip().split()[3])
                Fx = float(line.strip().split()[5])
                Fy = float(line.strip().split()[7])
                Fz = float(line.strip().split()[9])
                Mx = float(line.strip().split()[13])
                My = float(line.strip().split()[15])
                Mz = float(line.strip().split()[17])
                Fres = np.sqrt(Fx**2 + Fy**2 + Fz**2)
                rcforc[contactID-1].append([Fx, Fy, Fz, Mx, My, Mz, time, Fres])
            if len(line)==0:
                temp=-5
    f.close()

    # Sort into better array
    def column(matrix, i): #Extract column from array
        return [row[i] for row in matrix]
    def rclen(rc): # Find length of rcforc file
        rclengths = np.zeros(len(rcforc))
        for i in range(0,len(rcforc)):
            rclengths[i] = len(column(rcforc[i],0))
        return int(np.max(rclengths))
    temp = np.zeros((ncontacts, 8, rclen(rcforc)))
    for i in range(0,ncontacts):
        if len(rcforc[i])>0:
            for j in range(0,8):
                temp[i,j,:] = column(rcforc[i],j)
    return temp


def readnodout( Inputfilename, stringname = ''):
    """
     Script to read nodout-files from LS-DYNA
     Run as
       nodout = readnodout('nodout')
       nodoutID = readnodout('nodout', 'stringname')
     Plot as
       plt.plot(nodout[:,nodeID,variableID])
     Variables :
        0 : time
        1 : nodal_point
        2 : x-disp
        3 : y-disp
        4 : z-disp
        5 : x-vel
        6 : y-vel
        7 : z-vel
        8 : x-accl
        9 : y-accl
        10 : z-accl
        11 : x-coor
        12 : y-coor
        13 : z-coor
    """
    import numpy as np


    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]


    # Read file to get node index heading
    f = open(Inputfilename,'r')
    temp = 0
    val = []
    while temp==0:
        line = f.readline()
        if '{BEGIN LEGEND}' in line:
            temp=2
            line = f.readline() # heading
            while temp==2:
                line = f.readline()
                if '{END LEGEND}' in line:
                    temp=3
                else:
                    val.append(line.strip())
        elif 'n o d a l   p r i n t   o u t   f o r' in line: # abort if no names
            temp=1

    # Read file to get number of elements
    f = open(Inputfilename,'r')
    temp = 0
    nodes = []
    while temp==0:
        line = f.readline()
        if 'nodal point' in line:
            temp=2
            nnode = 0
            while temp==2:
                line = f.readline()

                if len(line.split()) == 0:
                    temp=3
                else:
                    nnode += 1
                    nodes.append(int(line.split()[0]))
    nodes = np.array(nodes)
    f.close()


    # Find match between element ID and index
    selval = []
    if len(val) == nnode: # Then all elements have title
        for ID, v in enumerate(val):
            if stringname in v:
                selval.append(ID)
    else:
        for ID, v in enumerate(val): # Then we find matching node index
            if stringname in v:
                selval.append(np.where(nodes == int(v.split()[0]))[0][0])

    if stringname == '':
        values = []
        # Read data
        f = open(Inputfilename,'r')
        temp = 0
        while temp==0:
            line = f.readline()
            if 'n o d a l' in line: # Then we have a new time step
                time = line.split()[-2]
                vval = []
                for i in range(0,2): dummy = f.readline()
                for i in range(0,nnode):
                    line = f.readline()
                    nodeID = line.split()[0]
                    templist = list(chunks(line[10:],12))[:-1]
                    templist =  [float(i) for i in np.concatenate(([float(time), nodeID], templist))]
                    vval.append(templist)
                teststop = 0
                for i in range(0,5):
                    dummy = f.readline()
                    teststop += len(dummy)
                if teststop == 0:
                    temp=3 #end of file

                values.append(vval)
            if len(line) == 0:
                temp=3
        f.close()

    if stringname  == '': #then return nodout values
        ret = np.array(values)
    else:
        ret = np.array(selval)
    return ret

""" Functions for post-processing of beerpong simulation """

def did_I_hit(*args,**kwargs):
    import matplotlib.pyplot as plt
    import numpy as np
    from .functions import readrcforc, readnodout
    from subprocess import Popen, call
    import glob


    rcforc = readrcforc('rcforc')
    nodout = readnodout('nodout')


    n1_init = [-0.9993365, 0.0, 0.2729799]
    cup = np.array([[.763, 0.1],
                    [0.772, 0.],
                    [0.841, 0.],
                    [0.85, 0.1]])

    nodehist =  [list(nodout[:, 0, 0]),
                 list(nodout[:, 0, 2]),
                 list(nodout[:, 0, 3] + n1_init[1]),
                 list(nodout[:, 0, 4] + n1_init[2])]


    trigger = np.count_nonzero(rcforc[2,-1,:]) + np.count_nonzero(rcforc[1,-1,:])

    if trigger > 1:
        print(f'Yay, you hit with a maximum force of {np.max(rcforc[2,-1,:]):.1f} N!')

        # Create a figure with the trajectory
        plt.figure(figsize=(10,4))
        plt.plot(nodehist[1], nodehist[3])
        plt.plot(1+cup[:,0], cup[:,1], color = 'black')
        plt.plot([0, 2], [0,0], color='black')
        plt.xlim([0, 2])
        plt.ylim([0, np.ceil(np.max(nodehist[3]) * 10) / 10])
        plt.xlabel('Longitudinal [m]')
        plt.ylabel('Vertical [m]')
        plt.axis('equal')
        plt.savefig('Trajectory.png')
        plt.close()

        # Get screen dumps from the simulation


        contactstepsOutside = np.nonzero(rcforc[1,-1,:])
        contactstepsInside  = np.nonzero(rcforc[2, -1, :])
        temp = []
        if len(contactstepsOutside[0])>0:
            temp.extend(list(contactstepsOutside[0]))
        if len(contactstepsInside[0])>0:
            temp.extend(list(contactstepsInside[0]))

        if len(temp)>0:
            temp = np.sort(np.array(temp))
        else:
            temp=[0.]

        steps = list(np.linspace(0,temp[0]/2.,4).astype(int)) # Add a few steps leading up to impact
        if len(contactstepsInside[0])>0: # Add last contact step inside cup
            steps.append(contactstepsInside[0][-1])

        f = open('inp_plot.cfile', 'w')
        f.write('open d3plot "d3plot"\n')
        f.write('ac\n')
        f.write('quat 0.576596 -0.125669 -0.185182 0.785782;\n')
        f.write('pan -0.002301 0.012653;\n')
        f.write('zoom 0.451711;\n')
        for i, step in enumerate(steps):
            f.write(f'state {step:d};\n')
            f.write(f'print png "image_{str(i).zfill(3):s}.png" enlisted "OGL1x1" \n')
        f.close()
        call(f'"C:\Program Files\LSTC\LS-PrePost 4.8\lsprepost4.8_x64.exe" c=inp_plot.cfile -nographics', shell=True)

    else:
        print('Sorry, no hit, try again')

    return nodehist, trigger


def makeplot(timehist, trigger, *args,**kwargs):
    import matplotlib.pyplot as plt
    import numpy as np

    keys = timehist.keys()
    cup = np.array([[.763, 0.1],
                    [0.772, 0.],
                    [0.841, 0.],
                    [0.85, 0.1]])

    plt.figure()
    for k in keys:
        hist = timehist[k]
        trig = trigger[k]
        if trig>5: # Then we count a hit
            plt.plot(hist[1], hist[3], label = f'run {k}')
        elif trig > 1:  # Then we count a near hit
            plt.plot(hist[1], hist[3], color = 'grey', label=f'run {k}')
        else:
            plt.plot(hist[1], hist[3], color = 'lightgrey')
    plt.plot(1 + cup[:, 0], cup[:, 1], color='black')
    plt.plot([0, 2], [0, 0], color='black')
    plt.xlim([0, 2])
    plt.ylim([0, 2])
    plt.xlabel('Longitudinal [m]')
    plt.ylabel('Vertical [m]')
    plt.legend()
    plt.axis('equal')
    plt.savefig('allTrajectories2D.png')
    plt.close()
    return


""" Functions to run LS-DYNA simulations in pytailor """

def rundyna(inputfile = '', **kwargs):
    """
    Runs LS DYNA

    config['rundyna'] = {
                    # Parameters for file control

                    'solver' : 'C:\Program Files\LSTC\LS-DYNA\ls-dyna_smp_s_R910_winx64_ifort131_lib.exe',
                    'inpfile' : 'inp_master.key', # File name for master input file to be called by LS-DYNA

                    # Parameters used when calling the executable
                    'runparams' :{'NCPU' : 1, 'memory' : 20000000}

                    }
    """
    import subprocess
    import glob

    print(f'Starting LS-DYNA simulation with {inputfile}')

    # dyna_config = kwargs.get('rundyna')
    runparams = kwargs.get('runparams')
    if inputfile == '': # If not given as args, find in kwargs
        inputfile = kwargs.get('inpfile','foundnone')
    if 'foundnone' in inputfile: # Then no input file is given, check if a run file is present in the folder (from populate)
        keyfiles = glob.glob('*run*.k*')
        if len(keyfiles)==1:
            inputfile = keyfiles[0]
        else:
            raise Exception('Did not find master input file for LS-DYNA simulation')

    solveargs = [kwargs.get('solver')] + [f'i={inputfile}'] + [f'{k}={v}' for k,v in runparams.items()]
    out = subprocess.check_output(solveargs)
    fo = open('console_printout.txt', "w")
    fo.write(out.decode("utf-8"))
    fo.close()
    return



def populate_runfiles(**kwargs):
    """
    Populate the master run file with kwargs argument
    Uses separate functions to write each key word

    """
    from .functions import include, controlTermination, termination_node, defineCurve, initialVelocity, loadBodyZ



    inpMaster = kwargs.get('input_master','')
    populate = kwargs.get('populate')

    if inpMaster == '': # If no master files is given, start with clean sheets
        orglines = ['*KEYWORD \n']
    else:
        f = open(inpMaster, 'r')
        orglines = f.readlines()
        f.close()
        orglines = [line for line in orglines if 'END' not in line]

    listlengths = []
    for k,v in populate.items():
        listlength = 1
        for kk,vv in v.items():
            if isinstance(vv,list) and len(vv)>1:
                listlength = len(vv)
        listlengths.append(listlength)


    outfiles = []
    for j in range(0,max(listlengths)):
        outfile = f'inp_Master_run{j:03d}.key'
        outfiles.append(outfile)

        fo = open(outfile, 'w')
        fo.writelines(orglines)
        fo.writelines(LSw.title(outfile.replace('.key','').replace('_', ' ')))
        for k,v in populate.items():

            tempdict = {}
            for kk,vv in v.items():
                if isinstance(vv,list):
                    if len(vv)==1:
                        tempdict[kk] = vv[0]
                    else:
                        tempdict[kk] = vv[j]
                else:
                    tempdict[kk] = vv
            fo.writelines(LSw.__dict__.get(k)(**tempdict))
        fo.write('*END\n')
        fo.close()

    return outfiles


"""Functions to write input cards to LS-DYNA"""

def include(files):
    lines = []
    lines.append('*INCLUDE\n')
    if isinstance(files, str):
        files = [files]
    for file in files:
        lines.append(f'{file}\n')
    return lines

def termination_node(nID, stop, maxc,minc):
    lines = []
    lines.append('*TERMINATION_NODE\n')
    lines.append('$#     nid      stop      maxc      minc\n')
    if isinstance(nID,int):
        nID = [nID]
        stop = [stop]
        maxc = [maxc]
        minc = [minc]
    for n, s, ma, mi in zip(nID, stop, maxc, minc):
        lines.append(f' {n:d}, {s:d}, {ma:.4g}, {mi:.4g}\n')
    return lines

def controlTermination(endtime):
    lines = ['*CONTROL_TERMINATION\n']
    lines.append('$#  endtim    endcyc     dtmin    endeng    endmas\n')
    lines.append(f'{endtime:.3e},  0,  0.0,  0.0, 1.0E8\n')
    return lines

def initialVelocity(nsID, vx, vy, vz, vxr = 0, vyr = 0, vzr = 0):
    lines = []
    lines.append('*INITIAL_VELOCITY\n')
    lines.append('$#    nsid    nsidex     boxid    irigid      icid\n')
    lines.append(f' {nsID:d}, 0, 0, 0, 0\n')
    lines.append('$#      vx        vy        vz       vxr       vyr       vzr\n')
    lines.append(f' {vx:.4g}, {vy:.4g}, {vz:.4g}, {vxr:.4g}, {vyr:.4g}, {vzr:.4g} \n')
    return lines

def loadBodyZ(lcID, sf, cid=0, lciddr=0):
    lines = []
    lines.append('*LOAD_BODY_Z\n')
    lines.append('$#    lcid        sf    lciddr        xc        yc        zc       cid\n')
    lines.append(' %i, %.3g, %i, 0.0, 0.0, 0.0, %i\n' %(lcID, sf,  lciddr, cid))
    return lines

def defineCurve(lcID, name, a1, o1, sidr=0):
    lines  = []
    lines.append('*DEFINE_CURVE_TITLE\n')
    lines.append('%s\n' %(name))
    lines.append('$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint\n')
    lines.append('  %i, %i, 1.0,  1.0, 0.0, 0.0, 0, 0\n' %(lcID, sidr))
    lines.append('$#                a1                  o1  \n')
    for i in range(0,len(a1)):
        lines.append(' %.5g, %.5g\n' %(a1[i], o1[i]))
    return lines
