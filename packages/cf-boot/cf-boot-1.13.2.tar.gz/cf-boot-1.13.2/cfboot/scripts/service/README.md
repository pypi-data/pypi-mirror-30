Create a service instance, and possibly extract service binding credentials.

This is a more declarative version of cf-create-service, which takes care of low-level plumbing to extract service credentials.
It is a wrapper built on top of cf-create-service, cf-delete-service, cf-push-app, extract-service-credentials.

# Input

(required\*)

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
<td class="left">instance\_name\*</td>
<td class="left">string</td>
<td class="left">app-hub-redis-service</td>
<td class="left">name of the instance</td>
</tr>


<tr>
<td class="left">service\*</td>
<td class="left">string</td>
<td class="left">redis</td>
<td class="left">service label</td>
</tr>


<tr>
<td class="left">plan\*</td>
<td class="left">string</td>
<td class="left">shared-vm</td>
<td class="left">plan</td>
</tr>


<tr>
<td class="left">cf\_home</td>
<td class="left">string</td>
<td class="left">"/tmp/cf-home-240964"</td>
<td class="left">CF\_HOME where login has been issued, defaults to $HOME</td>
</tr>


<tr>
<td class="left">payload</td>
<td class="left">arbitrary</td>
<td class="left">&#xa0;</td>
<td class="left">payload to create-service</td>
</tr>


<tr>
<td class="left">credential\_paths</td>
<td class="left">map (string->list of string)</td>
<td class="left">{"acs\_zone": ["zone", "http-header-value"], "acs\_uri": ["uri"]}</td>
<td class="left">A map {"<CUSTOM\_CREDENTIAL\_NAME>" : ["json", "path", "to", "credential"] }</td>
</tr>


<tr>
<td class="left">\*if\_exists</td>
<td class="left">string</td>
<td class="left">"ignore", "update", "delete"</td>
<td class="left">what to do when service instance exists</td>
</tr>
</tbody>
</table>

### if\_exists options

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

-   create an event hub instance and extract the publish and subscribe uaa scopes

    {
         "instance_name": "cf-boot-service-test-ehub",
         "service": "predix-event-hub",
         "plan": "Beta",
         "payload": {"trustedIssuerIds": ["https://908485db-10b7-4bc2-acfc-740f1bc540e7.predix-uaa.run.asv-pr.ice.predix.io/oauth/token"]},
         "credential_paths": {
             "event_hub_scope_user":
             ["publish", "protocol_details", 0, "zone-token-scope", 0],
    
             "event_hub_scope_publish_grpc":
             ["publish", "protocol_details", 0, "zone-token-scope", 1],
    
             "event_hub_scope_publish_wss":
             ["publish", "protocol_details", 1, "zone-token-scope", 1],
    
             "event_hub_scope_subscribe_grpc":
             ["subscribe", "protocol_details", 0, "zone-token-scope", 1]
         }
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


<tr>
<td class="left">"<CREDENTIAL\_NAME\_A>"</td>
<td class="left">any</td>
<td class="left">"predix-event-hub.zones.e7df08b1-256c-42d9-aeeb-bf94b9c92921.grpc.publish"</td>
<td class="left">custom credential value</td>
</tr>


<tr>
<td class="left">"<CREDENTIAL\_NAME\_B>"</td>
<td class="left">any</td>
<td class="left">"predix-event-hub.zones.e7df08b1-256c-42d9-aeeb-bf94b9c92921.grpc.subscribe"</td>
<td class="left">custom credential value</td>
</tr>


<tr>
<td class="left">&#x2026;</td>
<td class="left">any</td>
<td class="left">&#xa0;</td>
<td class="left">custom credential value</td>
</tr>
</tbody>
</table>

## Example:

    {
      "event_hub_scope_subscribe_grpc": "predix-event-hub.zones.e7df08b1-256c-42d9-aeeb-bf94b9c92921.grpc.subscribe",
      "event_hub_scope_publish_grpc": "predix-event-hub.zones.e7df08b1-256c-42d9-aeeb-bf94b9c92921.grpc.publish",
      "event_hub_scope_user": "predix-event-hub.zones.e7df08b1-256c-42d9-aeeb-bf94b9c92921.user",
      "event_hub_scope_publish_wss": "predix-event-hub.zones.e7df08b1-256c-42d9-aeeb-bf94b9c92921.wss.publish",
      "SERVICE_GUID": "e7df08b1-256c-42d9-aeeb-bf94b9c92921"
    }

# Idempotence

The script may be called any number of times. If the instance does not exist, it is created.