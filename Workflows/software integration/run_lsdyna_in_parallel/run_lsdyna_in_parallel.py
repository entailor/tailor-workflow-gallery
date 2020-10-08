import glob
import numpy as np
from pytailor import PythonTask, BranchTask, DAG, Workflow, Project, FileSet, Files, Outputs
from files.functions import populate_runfiles, rundyna, did_I_hit, makeplot



vel = 3.1 # Velocity in m/s
# angles = np.linspace(5,70,40); endtime = 2.0
angles = [50]; endtime = 0.02

inputs = {
        'wf_run_name' : 'Branch duplicate LS-DYNA',
        'populate_dyna' : {
            # 'input_master' : 'inp_master_duplicate.key',  # File name of file with basic setup (parameters not to be duplicated).
            #                                     #   (all inputs below are ammended to this file)
            #                                     #  If not given, a clean file will be written
            'populate' : { # All items to be populated in the file. key = function name in LSwrite. Value = input to function
                    'include' : {'files' : [['beerpong_v2.key', 'inp_output.key', 'inp_control.key']]
                    },
                    'controlTermination' : {'endtime' : 2.00,
                    },
                    'termination_node' : {'nID' : [[1,1,1]],
                                          'stop' : [[1,2,3]],
                                          'maxc' : [[1., .2, 5.]],
                                          'minc' : [[-1.2, -.2, -0.05]],
                    },
                    'initialVelocity' : { 'nsID' : 1,
                                           'vx' : [np.round(vel*np.cos(np.radians(angle)),4) for angle in angles] ,
                                           'vy' : 0.,
                                           'vz' : [np.round(vel*np.sin(np.radians(angle)),4) for angle in angles] ,
                    },
                    'loadBodyZ' : {'lcID' : 1,
                                   'sf' : 1.0,
                    },
                    'defineCurve': {'lcID': 1,
                                    'name': 'gravity',
                                    'a1': [[0, 1e8]],
                                    'o1': [[9.81, 9.81]],
                    },
            },
        },
        'rundyna' : {
              'runparams' :{ # All parameters required to run LS-DYNA in the appropriate manner
                          'NCPU' : 1,
                          'memory' : 20000000
              },
              'solver'  : 'C:\Program Files\LSTC\LS-DYNA\R12\lsdyna.exe', #Solver name, accessible on worker
        },
}








files = Files()
outputs = Outputs()


with DAG(name="dag") as dag:
    task0 = PythonTask(
        function=populate_runfiles,
        name='populate_runfiles',
        kwargs = inputs,
        upload = {files.LSDYNA_runfiles: '*run*.k*'},
        download = [files.functions],
        use_storage_dirs=False,
    )
    with BranchTask(
        name="branch",
        branch_files=[files.LSDYNA_runfiles],
        parents=task0
        ) as branch:
        with DAG(name="subdag") as subdag:
            task1 = PythonTask(
                function= rundyna,
                name='run LS-DYNA sim',
                args = files.LSDYNA_runfiles,
                kwargs=inputs,
                download=[files.LSDYNA_inputfiles, files.LSDYNA_runfiles, files.functions],
                upload={files.LSDYNA_outputfiles: ['*']},
                use_storage_dirs=False,
            )
            task2 = PythonTask(
                function=did_I_hit,
                name='postproc',
                kwargs=inputs,
                download=[files.LSDYNA_inputfiles,
                          files.LSDYNA_runfiles,
                          files.LSDYNA_outputfiles,
                          files.functions,
                          files.cfile],
                upload={files.LSDYNA_postfiles: '*.png'},
                output_extraction = {outputs.timehist : "<% $[0] %>", outputs.trigger : "<% $[1] %>"},
                use_storage_dirs=False,
                parents = task1,
            )
    task3 = PythonTask(
        function=makeplot,
        name='plot',
        args=[outputs.timehist, outputs.trigger],
        kwargs = inputs,
        download = [files.functions],
        use_storage_dirs=False,
        parents = branch,
        upload={files.allTrajectories: '*.png'},
    )



prj = Project.from_name('Test')

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(LSDYNA_inputfiles = glob.glob('files/*.k*'),
               functions = glob.glob('files/*.py'),
               cfile = glob.glob('files/*.cfile') )

# create a workflow:
wf = Workflow(project=prj, dag=dag, fileset=fileset, name='runDyna')

# run the workflow
wf_run = wf.run(worker_name='martin')

# check the status of the workflow run
print(wf_run)
