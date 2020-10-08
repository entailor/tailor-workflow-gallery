from pytailor import PythonTask, DAG, Inputs, Outputs, Files
import from_excel_tables
import glob

inputs = Inputs()
outputs = Outputs()
files = Files()

with DAG(name="Automatic reporting dag") as dag:
    plot_task = PythonTask(
        name="Make plots",
        function=from_excel_tables.create_content.make_plots,
        args=files.excel_files,
        download=files.excel_files,
        upload={files.plots: "*.pdf"},
        use_storage_dirs=False,
    )
    make_content_task = PythonTask(
        name="Make report content",
        function=from_excel_tables.create_content.make_conten,
        args=[files.plots, files.ecel_files, inputs.report_data],
        download=[files.plots, files.excel_files],
        output_to=outputs.report_content,
        use_storage_dirs=False,
        parents=[plot_task, table_task]
    )
    PythonTask(
        name="Make pdf report",
        function=from_excel_tables.create_content.make_report,
        args=[outputs.report_content],
        download=[files.plots, files.tables],
        upload={files.report: "*report.pdf"},
        use_storage_dirs=False,
        parents=[make_content_task]
    )

### run workflow ###

from pytailor import Project, FileSet, Workflow

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
    ],
    "report_data": {
        "document_title": "A01 Catenary riser simulation results report",
        "document_filename": "A01_Catenary_riser_report",
        "author": "Tailor examples",
        "fig_ext": ".pdf",
        "header_logofilename": "entail.pdf",
        "logo_image_option_header": "width=250px"
    }
}

# prepare inputs files
# create a fileset and upload files
fileset = FileSet(prj)
testfiles = glob.glob('./testfiles/*.xlsx')
fileset.upload(excel_files=testfiles)

#
# # create a workflow:
# wf = Workflow(project=prj,
#               dag=dag,
#               name="Orcaflex simulation workflow",
#               inputs=workflow_inputs,
#               fileset=fileset)

# run the workflow
# wf.run(distributed=True)
# wf.run(distributed=True, worker_name='bernt')
