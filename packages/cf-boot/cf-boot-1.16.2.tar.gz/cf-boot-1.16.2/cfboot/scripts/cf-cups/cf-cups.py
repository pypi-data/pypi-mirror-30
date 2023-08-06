#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, random, sys
from subprocess import Popen, check_output

DEVNULL = open(os.devnull, 'wb')

input_json = json.load(sys.stdin)

required_input = ["instance_name",
				  "credentials"]

missing = filter(lambda key: key not in input_json, required_input)
if missing:
    raise Exception("missing input argument(s) {}"
                    .format(",".join(missing)))

instance_name = input_json["instance_name"]

bind_to_apps=input_json.get("apps", [])

#optional payload argument

child_env = os.environ.copy()
cf_home=input_json.get("cf_home", os.environ['HOME'])
child_env["CF_HOME"] = cf_home

cf_config=json.load(open(os.path.join(cf_home, ".cf", "config.json"), "r"))
space_guid=cf_config["SpaceFields"]["GUID"]

Popen(["cf", "create-user-provided-service", instance_name],
                     env = child_env, stdout = DEVNULL, stderr = DEVNULL).wait()

# it's ok to fail above, as long as we can successfuly get the guid
# since we're replacing the entire object

def cf_curl ( *args ):
    full_args = ["cf", "curl"] + list(args)
    p = subprocess.Popen(full_args, env = child_env,
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise Exception("cf curl {} had non-zero exit: {}"
                    .format(" ".join(args), out))
    try:
        return json.loads(out)
    except:
        raise Exception("cf curl returned non-JSON response: {}"
                        .format(out))

all_instances = cf_curl("/v2/user_provided_service_instances"
                  .format(space_guid, instance_name))["resources"]

services=[ups for ups in all_instances \
       if ups["entity"]["space_guid"]==space_guid and\
       ups["entity"]["name"]==instance_name]

if not len(services)==1:
    raise Exception("expected exactly one user-provided service guid in with name {} in space {}"
                    .format(instance_name, space_guid))


guid=services[0]["metadata"]["guid"]

#perform update
update_payload = { k: input_json[k] for k in
                   ["route_service_url", "syslog_drain_url", "credentials"]
                   if k in input_json}

args = ["cf", "curl",
                  "/v2/user_provided_service_instances/{}".format(guid),
		"-X", "PUT", "-d", json.dumps(update_payload)]
p = Popen(args, env = child_env, stdout = DEVNULL, stderr = sys.stderr)
p.wait()


if p.returncode != 0:
    raise Exception("updating user-provided service failed with args"
                    .format(args))

for app_name in bind_to_apps:
    args=["cf", "bind-service", app_name, instance_name]
    print (" ".join(args), file=sys.stderr)
    p = Popen(args, env = child_env, stdout = sys.stderr, stderr = sys.stderr)
    p.wait()

print (json.dumps({"SERVICE_GUID" : guid}))

# Local Variables:
# compile-command: "./cf-cups.py < test.json "
# End:
