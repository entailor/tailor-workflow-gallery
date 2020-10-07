
# run orcaflex in parallel - a tailor workflow
------------

## Prerequisites

Requires python 3, pip, pytailor, orcapack and an orcaflex license with python api installed. 

Pytailor is installed with the following in the terminal.

```
pip install pytailor
```

Orcapack is installed with the following in the terminal.

```
pip install orcapack
```

The orcaflex python api is installed with the following in the terminal. 
The 11.0 version may need to be replaced by your version:
```
cd C:\Program Files (x86)\Orcina\OrcaFlex\11.0\OrcFxAPI\Python>
pip install .
```
and test that it works by importing in python
```
import OrcFxAPI
```

## running the workflow

First run the file run_orcaflex_in_parallel.py. 
This sets up and adds the workflow to your project.

Then, start a worker.
In terminal:

```
tailor worker
```

Now you can go to www.tailor.wf, log in and monitor the workflow progress.
