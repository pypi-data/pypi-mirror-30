Format a string using printf and environment variables

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
<td class="left">envs</td>
<td class="left">map</td>
<td class="left">{"UAA\_URL": "<https://GUID.predix-uaa.predix.io>"}</td>
<td class="left">env var mappings to add to current process</td>
</tr>


<tr>
<td class="left">fmts</td>
<td class="left">map</td>
<td class="left">{"issuer\_url": "${UAA\_URL}/oauth/token"</td>
<td class="left">var names and printf format strings</td>
</tr>
</tbody>
</table>

## Examples:

-   format some strings based on environment variables

    {
        "envs": {
            "FIRST_NAME": "ernesto",
            "LAST_NAME": "alfonso"
        },
        "fmts": {
            "config": "${HOME}/.config",
            "random": "${RANDOM}-${RANDOM}-${RANDOM}",
            "full_name": "${FIRST_NAME}-${LAST_NAME}"
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
<td class="left">"<VAR 1>"</td>
<td class="left">string</td>
<td class="left">"*home/vagrant*.config"</td>
<td class="left">result of printf execution</td>
</tr>


<tr>
<td class="left">"<VAR 2>"</td>
<td class="left">string</td>
<td class="left">"10403-6129-3149"</td>
<td class="left">result of printf execution</td>
</tr>


<tr>
<td class="left">&#x2026;</td>
<td class="left">string</td>
<td class="left">&#xa0;</td>
<td class="left">result of printf execution</td>
</tr>
</tbody>
</table>

## Example:

    {
      "random": "10403-6129-3149", 
      "config": "/home/vagrant/.config", 
      "full_name": "ernesto-alfonso"
    }

# Idempotence

Always idempotent