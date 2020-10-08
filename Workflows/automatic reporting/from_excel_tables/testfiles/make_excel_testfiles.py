import glob
import numpy as np
import OrcFxAPI as of
import pandas as pd
from pytailor import Project, Workflow

prj = Project.from_name("Test")
wf = Workflow.from_project_and_id(prj, 676)

wf.fileset.list_files()
wf.fileset.download(tags=['sim_file'], use_storage_dirs=False)

indict = [
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


def make_tables(res_files, post_proc_data):
    for post_proc_def in post_proc_data:
        for result_name in post_proc_def['Result names']:
            filename = result_name.replace(' ', '_')
            with pd.ExcelWriter(f'{filename}.xlsx') as writer:
                for hs, res_file in zip([4, 5, 6, 7, 8], res_files):
                    model = of.Model(res_file)
                    obj = model[post_proc_def['Object name']]
                    z = obj.RangeGraph('Z')
                    x = obj.RangeGraph('X')
                    y = obj.RangeGraph('Y')
                    r = np.sqrt(y.Mean ** 2 + x.Mean ** 2)
                    data = obj.RangeGraph(result_name)
                    df = pd.DataFrame(index=r, columns=['maxZ', 'minZ', 'meanZ', result_name.replace(' ', '_')],
                                      data=np.array([z.Max, z.Min, z.Mean, data.Max[:-1]]).T)
                    df = df.rename_axis(index='R')
                    df.to_excel(writer, sheet_name=f'Hs {int(hs)}')


make_tables(glob.glob('*.sim'), indict)

