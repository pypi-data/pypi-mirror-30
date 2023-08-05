from pycondor import Job

# Declare the error, output, log, and submit directories for Condor Job
error = 'condor/error'
output = 'condor/output'
log = 'condor/log'
submit = 'condor/submit'

job = Job('add_to_file_job',
          executable='python add_to_file.py',
          submit=submit,
          log=log,
          output=output,
          error=error)

job.build_submit()
