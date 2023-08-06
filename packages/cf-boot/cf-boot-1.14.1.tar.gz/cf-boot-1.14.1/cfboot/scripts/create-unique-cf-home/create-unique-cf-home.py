#!/usr/bin/python
import subprocess, os, json, random, sys, re
import hashlib

input_json = json.load(sys.stdin)

if set(("CF_TARGET", "CF_USER")).difference(input_json.keys()):
    raise Exception("must provide CF_TARGET CF_USER")

if not set(("CF_ORG", "CF_SPACE")).difference(input_json.keys()):
    org = input_json["CF_ORG"]
    space = input_json["CF_SPACE"]
elif "CF_ORG_SPACE" in input_json:
    (org, space) = input_json["CF_ORG_SPACE"].split("/")
else:
    raise Exception("{CF_ORG,CF_SPACE} or CF_ORG_SPACE inputs required")


args = ["cf", "login",
        "-a", input_json["CF_TARGET"],
        "-u", input_json["CF_USER"],
        "-o", org,
        "-s", space]

stdin=subprocess.PIPE
if "CF_PASSWORD" in input_json:
    args += ["-p", input_json["CF_PASSWORD"]]
elif "CF_SSO_PASSCODE" in input_json:
    args += ["--sso-passcode", input_json["CF_SSO_PASSCODE"]]
else:
    # raise Exception("CF_PASSWORD or CF_SSO_PASSCODE required")
    args += ["--sso"]
    fd = os.open('/dev/tty', os.O_RDWR)
    stdin = os.fdopen(fd, 'rw', 1)

def md5_hash ( string ):
    md5 = hashlib.md5()
    md5.update(string)
    return md5.hexdigest()

human_friendly = re.sub("[^a-zA-Z.@-]", "", "-".join((org, space)))
cf_home_md5 = md5_hash(" ".join(args))
cf_home_dir = "{}-{}".format(human_friendly, cf_home_md5)
cf_home_unique = os.path.join("/tmp", "cf-homes", cf_home_dir)

if not os.path.exists(cf_home_unique):
    os.makedirs(cf_home_unique)

try:
    subprocess.check_output(["which", "cf"])
except:
    CF_CLI_URL="https://docs.cloudfoundry.org/cf-cli/install-go-cli.html"
    raise Exception("cf cli not available. see {}".format(CF_CLI_URL))

os.environ["CF_HOME"] = cf_home_unique
child_env = os.environ.copy()
p = subprocess.Popen(args, env = child_env, stdout=sys.stderr,
                     stdin=stdin)
p.wait()
if p.returncode != 0:
    raise Exception("error running cf login")

json.dump({"CF_HOME" : cf_home_unique}, sys.stdout)
