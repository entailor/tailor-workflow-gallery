from pyreportlib.utils import excel_to_latex
import pandas as pd
import matplotlib.pyplot as plt
from pyreportlib import make_latex_document


def make_plots(excel_files):
    for excel_file in excel_files:
        plt.figure()
        df = pd.read_excel(excel_file, None)
        for sheet_name in df.keys():
            plt.fill_between(df[sheet_name].index,
                             df[sheet_name]['maxZ'],
                             df[sheet_name]['minZ'], color='#D3D3D3', alpha=0.5)
            plt.scatter(df[sheet_name].index, df[sheet_name]['meanZ'],
                        c=df[sheet_name][excel_file], cmap='jet', alpha=0.5)


def make_tables(excel_files):
    content = [{'title': 'Test',
                'content': excel_to_latex(testfile, header=header, index_col=0)}]

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


