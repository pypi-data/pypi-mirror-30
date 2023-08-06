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
<td class="left">\*required?</td>
</tr>


<tr>
<td class="left">instance\_name</td>
<td class="left">string</td>
<td class="left">"my-user-provided-service"</td>
<td class="left">name of the instance</td>
<td class="left">y</td>
</tr>


<tr>
<td class="left">credentials</td>
<td class="left">arbitrary</td>
<td class="left">{"key1":"value1","key2":"value2"}</td>
<td class="left">credentials JSON</td>
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
<td class="left">route\_service\_url</td>
<td class="left">string</td>
<td class="left">"<https://example.com>"</td>
<td class="left">route service url</td>
<td class="left">&#xa0;</td>
</tr>
</tbody>
</table>

## Example:

-   create a user provided service instance

    {
    "instance_name": "my-db-mine",
    "credentials": {"username":"admin","password":"***REMOVED***"},
    "cf_home": "/home/user"
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

The script may be called any number of times. The instance is deleted and recreated every time.