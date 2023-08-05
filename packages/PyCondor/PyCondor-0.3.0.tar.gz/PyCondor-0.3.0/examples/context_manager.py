#!/usr/bin/env python

import pycondor


# Declare the error, output, log, and submit directories for Condor Job
error = 'condor/error'
output = 'condor/output'
log = 'condor/log'
submit = 'condor/submit'

with pycondor.Dagman('exampledagman', submit=submit) as dag:
    global PYCONDOR_DAGMAN_CM
    print('PYCONDOR_DAGMAN_CM = {}'.format(PYCONDOR_DAGMAN_CM))
    job = pycondor.Job('examplejob', 'savelist.py',
                       error=error, output=output,
                       log=log, submit=submit,dag=dag)
    job.add_arg('--length 50')
    job.add_arg('--length 100')
    job.add_arg('--length 200')

print('WOO!')
