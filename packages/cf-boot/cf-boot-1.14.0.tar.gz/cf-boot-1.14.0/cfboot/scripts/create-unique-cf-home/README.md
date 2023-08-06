# Inputs

-   c api endpoint, cf user
    
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
    <td class="left">CF\_TARGET</td>
    <td class="left">string</td>
    <td class="left">"<https://api.system.asv-pr.ice.predix.io>"</td>
    <td class="left">cf api endpoint</td>
    </tr>
    
    
    <tr>
    <td class="left">CF\_USER</td>
    <td class="left">string</td>
    <td class="left">"service.hubsservice@ge.com"</td>
    <td class="left">cf username</td>
    </tr>
    
    
    <tr>
    <td class="left">&#xa0;</td>
    <td class="left">&#xa0;</td>
    <td class="left">&#xa0;</td>
    <td class="left">&#xa0;</td>
    </tr>
    </tbody>
    </table>
-   password options
    1.  <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
        
        
        <colgroup>
        <col  class="left" />
        
        <col  class="left" />
        
        <col  class="left" />
        
        <col  class="left" />
        </colgroup>
        <tbody>
        <tr>
        <td class="left">CF\_PASSWORD</td>
        <td class="left">string</td>
        <td class="left">"******REMOVED******"</td>
        <td class="left">cf password</td>
        </tr>
        </tbody>
        </table>
    2.  <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
        
        
        <colgroup>
        <col  class="left" />
        
        <col  class="left" />
        
        <col  class="left" />
        
        <col  class="left" />
        </colgroup>
        <tbody>
        <tr>
        <td class="left">CF\_SSO\_PASSCODE</td>
        <td class="left">string</td>
        <td class="left">"******REMOVED******"</td>
        <td class="left">non-interactive one-time sso passcode</td>
        </tr>
        </tbody>
        </table>
    3.  if nothing provided, interactively prompt for sso passcode
-   org/space options
    -   <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
        
        
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
        <td class="left">CF\_ORG</td>
        <td class="left">string</td>
        <td class="left">"HUBS"</td>
        <td class="left">cf org</td>
        </tr>
        
        
        <tr>
        <td class="left">CF\_SPACE</td>
        <td class="left">string</td>
        <td class="left">"dev"</td>
        <td class="left">cf space</td>
        </tr>
        </tbody>
        </table>
    -   OR
        
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
        <td class="left">CF\_ORG\_SPACE</td>
        <td class="left">string</td>
        <td class="left">"HUBS/dev"</td>
        <td class="left">slash-delimited combination of CF\_ORG/CF\_SPACE</td>
        </tr>
        </tbody>
        </table>

## Examples:

    {
     "CF_TARGET": "https://api.system.asv-pr.ice.predix.io",
     "CF_PASSWORD": "***REMOVED***",
     "CF_USER": "service.hubsservice@ge.com",
     "CF_ORG_SPACE": "HUBS/dev"
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
<td class="left">CF\_HOME</td>
<td class="left">string</td>
<td class="left">"/tmp/cf-home-913530"</td>
<td class="left">path to login-issued CF\_HOME</td>
</tr>
</tbody>
</table>

## Example:

    {"CF_HOME": "/tmp/cf-home-913530"}

# Idempotence

The script may be called any number of times. It will create a new unique throwaway directory under /tmp and issue a cf login