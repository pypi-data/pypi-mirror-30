#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, sys

input_json = json.load(sys.stdin)


child_env = os.environ.copy()
child_env.update(input_json.get("envs"))

var_fmts=input_json.get("fmts")

output=dict((var, subprocess.check_output(["bash", "-c", "printf " + fmt], env=child_env))
            for (var, fmt) in var_fmts.items())

json.dump(output, sys.stdout, indent = 2)

# Local Variables:
# compile-command: "./printf.py < test.json"
# End:
