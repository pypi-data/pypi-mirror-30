#!/usr/bin/env python

import pycondor

if __name__ == "__main__":

    # Setting up first PyCondor Job
    job1 = pycondor.Job('examplejob1', 'savelist.py', verbose=2)
    # Adding arguments to job1
    for i in range(100, 200, 10):
        job1.add_arg('--length {}'.format(i), retry=7)
    # Setting up second PyCondor Job
    job2a = pycondor.Job('examplejob2a', 'savelist.py', verbose=2)
    job2b = pycondor.Job('examplejob2b', 'savelist.py', verbose=2)
    # Adding arguments to job1
    job2b.add_arg('--length 200', name='200jobname')
    job2b.add_arg('--length 400', name='400jobname', retry=3)

    job3 = pycondor.Job('examplejob3', 'savelist.py', verbose=2)
    job3.add_arg('--length 13')

    # Add interjob reltionship.
    # Ensure that job1 is complete before job2 starts
    job1.add_children([job2a, job2b])
    job3.add_parents([job2a, job2b])

    # Setting up a PyCondor Dagman
    dagman = pycondor.Dagman('exampledagman', verbose=2)
    # Add jobs to dagman
    dagman.add_job(job1)
    dagman.add_job(job2a)
    dagman.add_job(job2b)
    dagman.add_job(job3)
    # Write all necessary submit files and submit job to Condor
    dagman.build_submit()
