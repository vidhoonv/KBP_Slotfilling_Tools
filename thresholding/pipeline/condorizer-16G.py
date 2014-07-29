#!/usr/local/bin/python


"""
Author of this file is Yinon Bentor
Credits: Many Thanks to Yinon for sharing this condor script. Reusing it for running relationfactory
         system on UT CS condor setup.

A very simple wrapper for a function call, making a corresponding condor script
and submitting it.
"""

import os, sys

CondorScript = """
universe = vanilla
requirements = InMastodon && Precise && Memory >= 10000

getenv = true

Initialdir = %s
Executable = %s

%s

+Group   = "GRAD"
+Project = "AI_ROBOTICS"
+ProjectDescription = "nlp tests"

Arguments = %s
Queue 
"""

OutputLine = """
Error = err.%s
Output = %s
"""

RawExecutable = sys.argv[1]
Arguments = ' '.join(sys.argv[2:-1])
OutputFile = sys.argv[-1]

Executable = os.popen('/bin/which %s' % RawExecutable).read()
CurrentDir = os.popen('/bin/pwd').read()

# remove path information
SafeOutputFile = '-'.join(OutputFile.split('/'))

if OutputFile == "/dev/null":
  outputlines = ""
else:
  outputlines = OutputLine % (SafeOutputFile, OutputFile)

condor_file = '/tmp/%s.condor' % (SafeOutputFile)
f = open(condor_file, 'w')
f.write(CondorScript % (CurrentDir, Executable, outputlines, Arguments))
f.close()   

os.popen('/lusr/opt/condor/bin/condor_submit %s' % condor_file)
