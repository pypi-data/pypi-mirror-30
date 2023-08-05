# Required Inputs

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

<col  class="left" />

<col  class="left" />

<col  class="left" />
</colgroup>
<tbody>
<tr>
<td class="left">**arg name**</td>
<td class="left">**JSON type**</td>
<td class="left">**example**</td>
<td class="left">**description**</td>
</tr>


<tr>
<td class="left">app\_name</td>
<td class="left">string</td>
<td class="left">ref-app</td>
<td class="left">name of the app</td>
</tr>


<tr>
<td class="left">cf\_home</td>
<td class="left">string</td>
<td class="left">"/tmp/cf-home-240964"</td>
<td class="left">CF\_HOME where login has been issued</td>
</tr>
</tbody>
</table>

# Optional inputs

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

<col  class="left" />

<col  class="left" />

<col  class="left" />
</colgroup>
<tbody>
<tr>
<td class="left">**arg name**</td>
<td class="left">**JSON type**</td>
<td class="left">**example**</td>
<td class="left">**description**</td>
</tr>


<tr>
<td class="left">git\_url</td>
<td class="left">string</td>
<td class="left">"<https://github.com/cloudfoundry-community/kibana-me-logs.git>"</td>
<td class="left">github url</td>
</tr>


<tr>
<td class="left">services</td>
<td class="left">list of string</td>
<td class="left">[ "logstash-space-wide" ]</td>
<td class="left">services to bind</td>
</tr>


<tr>
<td class="left">envs</td>
<td class="left">map (string->string)</td>
<td class="left">{ "KIBANA\_USERNAME": "kibana\_user", "KIBANA\_PASSWORD": "******REMOVED******" }</td>
<td class="left">environment variables to values. if provided, app will be restaged</td>
</tr>


<tr>
<td class="left">stack</td>
<td class="left">string</td>
<td class="left">"cflinuxfs2"</td>
<td class="left">option</td>
</tr>


<tr>
<td class="left">buildpack</td>
<td class="left">string</td>
<td class="left">"<https://github.com/heroku/heroku-buildpack-go.git>"</td>
<td class="left">buildpack</td>
</tr>


<tr>
<td class="left">git\_relpath\_build</td>
<td class="left">string</td>
<td class="left">"app-1/"</td>
<td class="left">relative path for cf push -p flag (app directory, jar, etc), defaults to git root</td>
</tr>


<tr>
<td class="left">git\_relpath\_deploy</td>
<td class="left">string</td>
<td class="left">"app-2/"</td>
<td class="left">relative path for build directory, defaults to git root</td>
</tr>


<tr>
<td class="left">hostname</td>
<td class="left">string</td>
<td class="left">"app-hostname"</td>
<td class="left">hostname option to cf push</td>
</tr>
</tbody>
</table>

## Examples:

-   push a basic-auth-protected kibana

    {
      "app_name": "kibana-space-wide",
      "buildpack": "https://github.com/heroku/heroku-buildpack-go.git",
      "envs": {
        "KIBANA_USERNAME": "kibana_user",
        "KIBANA_PASSWORD": "***REMOVED***"
      },
      "cf_home": "/tmp/cf-home-600396",
      "git_url": "https://github.com/cloudfoundry-community/kibana-me-logs.git",
      "services": [
        "logstash-space-wide"
      ],
      "stack": "cflinuxfs2"
    }

-   create an app for binding services and extracting credentials only.
    no push required

    {
       "app_name": "ref-app",
       "cf_home": "$CF_HOME"
    }

# Output

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

<col  class="left" />

<col  class="left" />

<col  class="left" />
</colgroup>
<tbody>
<tr>
<td class="left">**output name**</td>
<td class="left">**JSON type**</td>
<td class="left">**example**</td>
<td class="left">**description**</td>
</tr>


<tr>
<td class="left">app\_guid</td>
<td class="left">string</td>
<td class="left">"f9e82e7f-5f15-4ea9-b499-9ceab30d9660"</td>
<td class="left">app guid</td>
</tr>


<tr>
<td class="left">app\_url</td>
<td class="left">string</td>
<td class="left">"<https://kibana-me-logs-poc.run.asv-pr.ice.predix.io>"</td>
<td class="left">app url (first mapped route, space/org uniquified)</td>
</tr>
</tbody>
</table>

## Example:

    {
     "app_url": "https://kibana-me-logs-poc.run.asv-pr.ice.predix.io",
     "app_guid": "f9e82e7f-5f15-4ea9-b499-9ceab30d9660"
    }

# Idempotence

The script may be called any number of times. The app will be pushed again if it exists

# Notes

-   Push hostname is an name, org-space uniquified app name
-   The intent of this script is to deploy utility apps like kibana, phpadmin,

and throwaway apps for binding services and extracting credentials, not to compete with CI/CD.