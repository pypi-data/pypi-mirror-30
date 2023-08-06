#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, random, sys, re
from os.path import realpath, join, dirname, exists

def check_output ( args, env ):
    "on exception, show output"
    p = subprocess.Popen(args, env = env,
                         stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE)
    [out, err] = p.communicate()
    if p.returncode != 0:
        raise Exception("{} returned non-zero exit status {}\nstderr: {}"
                        .format(args, p.returncode, out+err))
    else:
        return out

def cf_target_info ( cf_home ):
    "obtain cf target info (api, org, space)"
    config_fn = join(cf_home, ".cf", "config.json")
    config = json.load(open(config_fn))
    return {"org": config["OrganizationFields"]["Name"],
            "space": config["SpaceFields"]["Name"],
            "space_guid": config["SpaceFields"]["GUID"]}

def create_dummy_app ( app_name, space_guid, child_env ):
    "POST an app object to cf. no upload or start"
    data = {"name" : app_name,
            "space_guid": space_guid,
            "memory": 1}
    subprocess.check_output(["cf", "curl", "/v2/apps",
                             "-X", "POST",
                             "-d", json.dumps(data)], env = child_env)

def cf_curl_with_env ( args, child_env ):
    print ( args, file = sys.stderr )
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

def cf_app_lookup_by_name ( app_name, space_guid, child_env ):
    out = cf_curl_with_env(["/v2/spaces/{}/apps?q=name:{}"
                  .format(space_guid, app_name)], child_env)
    TOTAL_RESULTS="total_results"
    if not TOTAL_RESULTS in out:
        raise Exception("bad response from CF API /v2/spaces: "+
                        json.dumps(out, indent=4))

    if out[TOTAL_RESULTS]:
        app = out["resources"][0]
        return app

def url_basename ( git_url ):
    return os.path.splitext(os.path.basename(git_url))[0]

def git_clone_app ( git_url, proxy, branch=None, skip_pull=False ):
    child_env = os.environ.copy()
    proxy = proxy or ""
    child_env["https_proxy"] = proxy
    child_env["http_proxy"] = proxy
    child_env["HTTPS_PROXY"] = proxy
    child_env["HTTP_PROXY"] = proxy

    app_clone_name = url_basename(git_url)
    deployer_apps = join("/tmp", "deployer-apps")
    if not exists(deployer_apps):
        os.mkdir(deployer_apps)

    path = join(deployer_apps, app_clone_name)

    if not exists(path):
        os.chdir(deployer_apps)
        check_output(["git", "clone", git_url], env = child_env)
        if not exists(path):
            raise Exception("git clone {} didn't create {} in {}"
                            .format(git_url, app_clone_name, os.getcwd()))

    os.chdir(path)

    if branch:
        check_output(["git", "checkout", branch], env = child_env)

    if not skip_pull:
        # pull the latest changes
        branch=branch or subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        check_output(["git", "pull", "origin", branch],
                                env = child_env)

    return path

def cf_push_app ( app_name, path, child_env, host_name,
                  buildpack = None, stack = None, domain = None, memory=None):
    "push the app"
    memory=memory or "500M"
    cf_push_args = ["cf", "push", app_name,
                    "--no-start", "--no-manifest",
                    "-p", path,
                    "--hostname", host_name,
                    "-m", memory]
    if buildpack:
        cf_push_args += ["-b", buildpack]
    if stack:
        cf_push_args += ["-s", stack]
    if domain:
        cf_push_args += ["-d", domain]
    print ( " ".join(cf_push_args), file = sys.stderr )
    p = subprocess.Popen(cf_push_args, env = child_env, stdout=sys.stderr)
    p.wait()
    if p.returncode != 0:
        raise Exception("push failed: {}".format(" ".join(cf_push_args)))

def cf_bind_services ( app_name, services, child_env ):
    for instance_name in services:
        bind_args = ["cf", "bind-service", app_name, instance_name]
        print ( " ".join(bind_args), file = sys.stderr)
        check_output(bind_args, env = child_env)

def cf_set_envs ( app_name, envs_map, child_env ):
    for (k, v) in envs_map.iteritems():
        setenv_args = ["cf", "set-env", app_name, k, v]
        print ( " ".join(setenv_args), file = sys.stderr)
        check_output(setenv_args, env = child_env)

def cf_start ( app_name, child_env, restage=False ):
    # start app
    # don't use check_output, which buffers entire output
    subcmd="start" if not restage else "restage"
    p = subprocess.Popen(["cf", subcmd, app_name],
                         env = child_env, stdout=sys.stderr)
    p.wait()
    if p.returncode != 0:
        raise Exception("cf {} {} failed".format(subcmd, app_name))

def main (  ):
    input_json = json.load(sys.stdin)

    cf_home = input_json.get("cf_home", os.environ['HOME'])
    app_name = input_json.get("app_name")
    git_url = input_json.get("git_url")
    if_app_started = input_json.get("if_app_started", "push")

    if not (app_name or git_url):
        raise Exception( "either app_name or git_url must be provided" )

    app_name = app_name or url_basename(git_url)

    child_env = os.environ.copy()
    child_env["CF_HOME"] = cf_home

    cf_target = cf_target_info(cf_home)
    cf_org = cf_target["org"]
    cf_space = cf_target["space"]
    cf_space_guid = cf_target["space_guid"]
    cf_org_sanitized = re.sub("[^a-zA-Z0-9-]", "-", cf_org)
    envs = input_json.get("envs") or {}


    # determine app current status, if any
    app=cf_app_lookup_by_name(app_name, cf_space_guid, child_env)
    app_status=app["entity"]["state"] if app else None

    if app_status=="STARTED":
         if if_app_started == "push":
             skip_push=False
             start_restage_skip_action="start"
         elif if_app_started == "restage":
             skip_push=True
             start_restage_skip_action="restage"
         elif if_app_started == "skip":
             skip_push=True
             start_restage_skip_action="skip"
         else:
             raise Exception("invalid 'if_app_started' value")
    else:
         # git_url is optional. if not provided, skip cf "push"
         skip_push = not git_url
         start_restage_skip_action="start" if not skip_push else "restage" if envs else "skip"

    if skip_push:
        # create an app for binding purposes only
        # save time on git clone, cf upload and app start
        print ( "warn: skipping app push", file = sys.stderr )
        create_dummy_app(app_name, cf_space_guid, child_env)
    else:
        # actual git clone, cf push
        no_proxy = input_json.get("git_clone_no_proxy")
        proxy = "" if no_proxy else os.environ.get("https_proxy")
        buildpack = input_json.get("buildpack")
        stack = input_json.get("stack")
        domain = input_json.get("domain")
        git_relpath_build = input_json.get("git_relpath_build", "")
        git_relpath_deploy = input_json.get("git_relpath_deploy", "")
        build_command = input_json.get("build_command")
        branch = input_json.get("git_branch")
        memory = input_json.get("memory")
        skip_pull = input_json.get("git_skip_pull")

        git_root=git_clone_app(git_url, proxy, branch, skip_pull)
        app_path = join(git_root, git_relpath_deploy)
        build_path = join(git_root, git_relpath_build)
        host_name = input_json.get("hostname", "-".join([app_name, cf_org_sanitized, cf_space]))

        if build_command:
            print("cd {}; {}".format(build_path, " ".join(build_command)), file = sys.stderr)
            old_cwd=os.getcwd()
            os.chdir(build_path)
            p=subprocess.Popen(build_command, stdout=sys.stderr)
            p.wait()
            if p.returncode != 0:
                raise Exception("build failed")
            os.chdir(old_cwd)

        cf_push_app(app_name, app_path, child_env, host_name,
                    buildpack = buildpack,
                    stack = stack,
                    domain = domain,
                    memory = memory)



    services = input_json.get("services") or []
    cf_bind_services(app_name, services, child_env)


    # set requested environment variables
    cf_set_envs(app_name, envs, child_env)

    if start_restage_skip_action != "skip":
        cf_start(app_name, child_env, restage = start_restage_skip_action=="restage")
    else:
        print ( "warn: skipping app start/restage", file = sys.stderr )


    def cf_curl(*args):
        return cf_curl_with_env(args, child_env)

    # extract app guid and url
    resp = cf_curl("/v2/spaces/{}/apps?q=name:{}"
                   .format(cf_space_guid, app_name))

    app = resp["resources"][0]
    app_guid = app["metadata"]["guid"]

    url = None
    urls = []
    try:
        routes = cf_curl("/v2/apps/{}/routes".format(app_guid))["resources"]

        def route_to_url(route):
            route_host = route["entity"]["host"]
            domain_url = route["entity"]["domain_url"]
            domain_name = cf_curl(domain_url)["entity"]["name"]
            url = "https://{}.{}".format(route_host, domain_name)
            return url

        if routes:
            urls=map(route_to_url, routes)
            if urls:
                url=urls[0]
    except:
        pass

    json.dump({"app_name" : app_name,
               "app_guid": app_guid,
               "app_url": url,
               "app_urls": urls }, sys.stdout)

if __name__ == '__main__':
    main()
