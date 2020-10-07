from pytailor import PythonTask, BranchTask, DAG, Inputs, Outputs, Files, Project, FileSet, Workflow
import orcapack

inputs = Inputs()
outputs = Outputs()
files = Files()

with DAG(name="Advanced orcaflex simulation dag") as dag:
    t1 = PythonTask(
        name="Pre-processing",
        function=orcapack.modelsetup.populate_orcaflex,
        kwargs={"datfile": files.base_file,
                "orcaflex_def": inputs.pre_proc_data},
        download=files.base_file,
        upload={"inp_file": "*orcaflex_run*.dat"}
    )
    with BranchTask(name="Parallel simulations",
                    branch_files=["inp_file"], parents=[t1]) as branch:
        with DAG(name="sub-dag for branching") as sub_dag:
            sim_core = PythonTask(
                name="Simulation",
                function=orcapack.run.run_simulation,
                args=files.inp_file,
                kwargs=inputs.run_simulation,
                download=files.inp_file,
                upload={files.sim_file: "*.sim"}
            )
            extract_results = PythonTask(
                name="Data extraction",
                function=orcapack.res2hdf5.sim2hdf5,
                args=[files.sim_file, inputs.extract_data],
                download=files.sim_file,
                upload={files.h5_file: "*.h5"},
                parents=sim_core
            )

### run workflow ###

# open a project
prj = Project.from_name("Test")

# define inputs
workflow_inputs = {
    "pre_proc_data": [
        {"Object type": "Environment",
         "Data name": "WaveHs",
         "Value": [4.0, 5.0, 6.0, 7.0, 8.0]},
        {"Object type": "Environment",
         "Data name": "WaveTp",
         "Value": 10}
    ],
    "run_simulation": {
        "calculate_statics": False
    },
    "extract_data": [
        {
            "Object type": "Line",
            "Object name": "Catenary Hose",
            "Object extra": 0,
            "Result names": [
                "Effective tension",
                "x bend moment",
                "y bend moment"
            ]
        }
    ]
}

# prepare inputs files
# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(base_file=["testfiles/A01_Catenary_riser.dat"])


# create a workflow:
wf = Workflow(project=prj,
              dag=dag,
              name="Orcaflex simulation workflow",
              inputs=workflow_inputs,
              fileset=fileset)

# run the workflow
wf.run(distributed=True, worker_name='bernt')

# optional: download h5 files when workflow is finished

# wf.fileset.download(use_storage_dirs=False)
