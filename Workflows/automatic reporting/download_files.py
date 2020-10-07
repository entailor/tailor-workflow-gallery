from pytailor import Project, Workflow

prj = Project.from_name("Test")
wf = Workflow.from_project_and_id(prj, 676)

wf.fileset.list_files()
wf.fileset.download(tags=['sim_file'], use_storage_dirs=False)