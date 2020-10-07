from typing import List
import pandas as pd
import numpy as np
import OrcFxAPI as of
from pyreportlib import make_latex_document


def make_tables(res_files: List[str], post_proc_data: List[dict]):
    for post_proc_def in post_proc_data:
        for result_name in post_proc_def['Result names']:
            with pd.ExcelWriter(f'{result_name}.xlsx') as writer:
                for hs, res_file in zip([4, 5, 6, 7, 8], res_files):
                    model = of.Model(res_file)
                    obj = model[post_proc_def['Object name']]
                    z = obj.RangeGraph('Z')
                    x = obj.RangeGraph('X')
                    y = obj.RangeGraph('Y')
                    r = np.sqrt(y.Mean ** 2 + x.Mean ** 2)
                    data = obj.RangeGraph(result_name)
                    df = pd.DataFrame(index=r, columns=['Z', result_name], data=np.array([z.Max, data.Max[:-1]]).T)
                    df = df.rename_axis(index='R')
                    df.to_excel(writer, sheet_name=f'Hs {int(hs)}')


def make_content(plot_files, table_files, report_data):
    report_data["content"] = [
        {
            "title": "Summary",
            "content": [
                {
                    "text": "Summary comes here"
                }
            ]
        },
        {
            "title": "Plots",
            "content": [
                {
                    "image": {
                        "filename": plot_files
                    }
                }]
        },
        {
            "title": "Tables",
            "content": [
                {
                    "table": {
                        "filename": table_files,
                        "kwargs": {
                            "index_col": 0
                        }
                    }
                }]
        }
    ]
    return report_data


def make_report(report_data):
    make_latex_document(**report_data)


