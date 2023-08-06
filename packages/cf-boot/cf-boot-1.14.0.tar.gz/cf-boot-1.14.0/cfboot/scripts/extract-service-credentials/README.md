# Inputs

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
<td class="left">ref\_app\_guid</td>
<td class="left">string</td>
<td class="left">"f9e82e7f-5f15-4ea9-b499-9ceab30d9660"</td>
<td class="left">guid of a sample app</td>
</tr>


<tr>
<td class="left">service\_instance\_guid</td>
<td class="left">string</td>
<td class="left">"845f80d1-14ec-4144-82fd-d6417bedb7b7"</td>
<td class="left">guid of the service instance</td>
</tr>


<tr>
<td class="left">credential\_paths</td>
<td class="left">map (string->list of string)</td>
<td class="left">{"acs\_zone": ["zone", "http-header-value"], "acs\_uri": ["uri"]}</td>
<td class="left">A map {"OUTPUT\_KEY\_NAME" : ["json", "path", "to", "credential"] }</td>
</tr>


<tr>
<td class="left">cf\_home</td>
<td class="left">string</td>
<td class="left">"/User/12345"</td>
<td class="left">CF\_HOME where login has been issued, defaults to $HOME</td>
</tr>
</tbody>
</table>

## credential path

A credential path specifies the list of accessors used to "walk down" from the root credentials map to the desired credential.
-   Example credentials map:

    "credentials": {
           "uri": "https://predix-acs.run.asv-pr.ice.predix.io",
           "zone": {
             "http-header-value": "d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0",
             "oauth-scope": "predix-acs.zones.d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0.user",
             "http-header-name": "Predix-Zone-Id"
           }
         }

-   Example "credential\_paths" input

    {"acs_zone": ["zone", "http-header-value"],
     "acs_uri": ["uri"]}

For convenience on the common case where the credential one level from the root, it is possible to pass a string instead of a singleton. The above is equivalent to:

    {"acs_zone": ["zone", "http-header-value"],
     "acs_uri": "uri"}

## Examples:

-   extract uaa uri
    -   input
    
        {
         "service_instance_guid": "908485db-10b7-4bc2-acfc-740f1bc540e7",
         "app_guid": "f9e82e7f-5f15-4ea9-b499-9ceab30d9660",
         "credential_paths": {"uaa_uri": ["uri"]}
        }
    
    -   output
    
        {
         "uaa_uri": "https://908485db-10b7-4bc2-acfc-740f1bc540e7.predix-uaa.run.asv-pr.ice.predix.io",
        }
-   extract acs zone, uri
    
        {
         "app_guid": "f9e82e7f-5f15-4ea9-b499-9ceab30d9660",
         "service_instance_guid": "845f80d1-14ec-4144-82fd-d6417bedb7b7",
         "credential_paths": {"acs_zone": ["zone", "http-header-value"],
                                    "acs_uri": ["uri"]}
         }
    
    -   output
    
        {
         "acs_zone": "d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0",
         "acs_uri": "https://predix-acs.run.asv-pr.ice.predix.io"
        }

# Outputs

A json mapping each credential name to its value. See examples above

# Idempotence

The script may be called any number of times. Whenever the binding does not exist, it is created.

# Implementation details: How it works

1.  Bind the app to the service instance.
    Since we're given the app and instance **guids** instead of names, it's inconvenient to use `cf create-servce`.
    We use the [cf api](http://apidocs.cloudfoundry.org) (via cf curl) to directly [POST a service binding](http://apidocs.cloudfoundry.org/237/service_bindings/create_a_service_binding.html)
2.  The request may "fail" with error code "CF-ServiceBindingAppServiceTaken". This is OK, and to preserve idempotence, we need to explicitly ignore this error.
3.  We use the cf api to obtain the service binding payload (which includes credentials).
    -   We use the ["/v2/service\_bindings?q=service\_instance\_guid:{}&q=app\_guid:{}"](http://apidocs.cloudfoundry.org/237/service_bindings/list_all_service_bindings.html) endpoint  
               (List all service bindings filtering by both service instance and app guid)
    
    -   Example response
    
             {
          "total_results": 1,
          "next_url": null,
          "total_pages": 1,
          "prev_url": null,
          "resources": [
            {
              "metadata": {
                "url": "/v2/service_bindings/06a55a45-4e02-42df-8d99-34fa346bf1d4",
                "created_at": "2016-08-05T14:44:55Z",
                "guid": "06a55a45-4e02-42df-8d99-34fa346bf1d4",
                "updated_at": null
              },
              "entity": {
                "app_url": "/v2/apps/ec9c28c9-c27a-4cb5-95f2-546fc2d5e45f",
                "binding_options": {},
                "gateway_name": "",
                "gateway_data": null,
                "syslog_drain_url": null,
                "credentials": {
                  "uri": "https://predix-acs.run.asv-pr.ice.predix.io",
                  "zone": {
                    "http-header-value": "d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0",
                    "oauth-scope": "predix-acs.zones.d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0.user",
                    "http-header-name": "Predix-Zone-Id"
                  }
                },
                "service_instance_guid": "d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0",
                "app_guid": "ec9c28c9-c27a-4cb5-95f2-546fc2d5e45f",
                "volume_mounts": [],
                "service_instance_url": "/v2/service_instances/d5eaf878-f6ba-4da3-83c1-9ebccd5aeda0"
              }
            }
          ]
        }

4.  There can only be one service binding for an (app, service-instance) pair.
    We make sure this is the case
5.  Extract the credentials map from the service binding.
    Go through each (credential-name, credential-path),  from user input to construct an output map.