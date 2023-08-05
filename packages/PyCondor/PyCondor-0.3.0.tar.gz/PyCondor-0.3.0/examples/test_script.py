#!/usr/bin/env python

import pycondor

if __name__ == "__main__":

    # Declare the error, output, log, and submit directories for Condor Job
    error = 'condor/error'
    output = 'condor/output'
    log = 'condor/log'
    submit = 'condor/submit'

    # Setting up a PyCondor Dagman
    dagman = pycondor.Dagman('exampledagman', submit=submit, verbose=2)

    job_child = pycondor.Job('examplejob_child', 'savelist.py',
                   error=error, output=output,
                   log=log, submit=submit, verbose=2,
                   dag=dagman)
    job_child.add_arg('--length 200', name='200jobname')
    job_child.add_arg('--length 400', retry=3)

    for i in range(100, 200, 10):
        job_parent = pycondor.Job('examplejob_{}'.format(i), 'savelist.py',
                           error=error, output=output,
                           log=log, submit=submit, verbose=2)
        job_parent.add_arg('--length {}'.format(i), retry=7)
        dagman.add_job(job_parent)
        job_parent.add_child(job_child)

    subdag = pycondor.Dagman('examplesubdag', submit=submit, verbose=2)
    dagman.add_subdag(subdag)
    job_subdag = pycondor.Job('subdag_job', 'savelist.py',
                   error=error, output=output,
                   log=log, submit=submit, verbose=2)
    job_subdag.add_arg('--length 1000', name='1000jobname')
    job_subdag.add_arg('--length 4000', retry=3)
    subdag.add_job(job_subdag)

    # Write all necessary submit files and submit job to Condor
    # dagman.build(fancyname=True)
    dagman.build_submit(fancyname=True, maxjobs=0, submit_options='-maxjobs 2')
