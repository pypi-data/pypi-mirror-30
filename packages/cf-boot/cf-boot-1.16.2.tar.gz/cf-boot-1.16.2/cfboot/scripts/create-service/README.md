# Input

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

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
<td class="left">**required?**</td>
</tr>


<tr>
<td class="left">instance\_name</td>
<td class="left">string</td>
<td class="left">app-hub-redis-service</td>
<td class="left">name of the instance</td>
<td class="left">y</td>
</tr>


<tr>
<td class="left">service</td>
<td class="left">string</td>
<td class="left">redis</td>
<td class="left">service label</td>
<td class="left">y</td>
</tr>


<tr>
<td class="left">plan</td>
<td class="left">string</td>
<td class="left">shared-vm</td>
<td class="left">plan</td>
<td class="left">y</td>
</tr>


<tr>
<td class="left">cf\_home</td>
<td class="left">string</td>
<td class="left">"/tmp/cf-home-240964"</td>
<td class="left">CF\_HOME where login has been issued, defaults to $HOME</td>
<td class="left">&#xa0;</td>
</tr>


<tr>
<td class="left">\*if\_exists</td>
<td class="left">string</td>
<td class="left">"ignore", "update", "delete"</td>
<td class="left">what to do when service instance exists</td>
<td class="left">&#xa0;</td>
</tr>


<tr>
<td class="left">payload</td>
<td class="left">arbitrary</td>
<td class="left">&#xa0;</td>
<td class="left">payload to create-service</td>
<td class="left">&#xa0;</td>
</tr>
</tbody>
</table>

## if\_exists options

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="left" />

<col  class="left" />
</colgroup>
<tbody>
<tr>
<td class="left">**option**</td>
<td class="left">**description**</td>
</tr>


<tr>
<td class="left">"ignore"</td>
<td class="left">do nothing (default)</td>
</tr>


<tr>
<td class="left">"update"</td>
<td class="left">update the service instance with a new payload or service plan</td>
</tr>


<tr>
<td class="left">"delete"</td>
<td class="left">delete the old service instance, including its service bindings</td>
</tr>
</tbody>
</table>

## Examples:

-   create a redis instance

    {
      "instance_name": "app-hub-redis-service",
      "cf_home": "/tmp/cf-home-240964",
      "plan": "shared-vm",
      "service": "redis"
    }

-   create a uaa service with admin secret payload

    {
     "instance_name": "hubs-config-manager-uaa",
     "service": "predix-uaa",
     "plan": "Tiered",
     "cf_home": "/Users/212556701",
     "payload": {"admin_secret" : "***REMOVED***"}
    }

-   create an acs service with a payload

    {
     "instance_name": "hub-acs-dev-configservice",
     "service": "predix-acs",
     "plan": "Tiered",
     "cf_home": "/tmp/cf-home-240964",
     "payload" : {"trustedIssuerIds" : "https://908485db-10b7-4bc2-acfc-740f1bc540e7.predix-uaa.run.asv-pr.ice.predix.io"}
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
<td class="left">output name</td>
<td class="left">JSON type</td>
<td class="left">example</td>
<td class="left">description</td>
</tr>


<tr>
<td class="left">"SERVICE\_GUID"</td>
<td class="left">string</td>
<td class="left">"c41f5741-97f6-43a9-82dc-b32f00588819"</td>
<td class="left">guid of the instance</td>
</tr>
</tbody>
</table>

## Example:

    {"SERVICE_GUID": "c41f5741-97f6-43a9-82dc-b32f00588819"}

# Idempotence

The script may be called any number of times. If the instance does not exist, it is created.