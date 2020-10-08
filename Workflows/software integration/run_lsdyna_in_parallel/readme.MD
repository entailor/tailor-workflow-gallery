
# run lsdyna in parallel - a tailor workflow
------------

## Prerequisites

Requires python 3, pip, pytailor, LS-DYNA and a valid LS-DYNA license

Pytailor is installed with the following in the terminal.

```
pip install pytailor
```


## running the workflow

First run the file run_lsdyna_in_parallel.py. 
This sets up and adds the workflow to your project.

Then, start a worker.
In terminal:

```
tailor worker
```

Now you can go to www.tailor.wf, log in and monitor the workflow progress.
