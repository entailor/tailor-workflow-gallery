from pyreportlib import make_latex_document
import orcah5post
import glob
import pandas as pd
from make_tables import make_tables

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

make_tables(glob.glob('*.sim'), indict)