# ci authzero-utils

Various scripts utilizing authzerolib to do things such as sync'ing authzero login page, rules, clients, settings, etc.
Useful to run in your CI!

# Usage

## Credentials & Scopes

You will need to create a non-interactive client in your Auth0 deployment, and assign it scopes in the Auth0 API setup
section, for the Auth0 management API. Refer to Auth0's documentation if you need help on how to do this.

The required scopes depend on the script, though they all follow these general rules:
- do not require scopes allowing access to secrets if possible (passwords, keys, etc.)
- require the minimum set of scopes possible

## Scripts
### uploader_login_page.py
SCOPES: `update:clients`

```
usage: uploader_login_page.py [-h] [-u URI] -c CLIENTID -s CLIENTSECRET
                              [--default-client DEFAULT_CLIENT] --login-page
                              LOGIN_PAGE
uploader_login_page.py: error: the following arguments are required: -c/--clientid, -s/--clientsecret, --login-page
```

Example: `./uploader_login_page.py -u auth-dev.mozilla.auth0.com -c AAA -s BBB --default-client CCC --login-page some.html`

Note that `CCC` above represents a special Auth0 "default" client. You can find this `client_id` by going to the "hosted
page" setup in Auth0 and looking at your web-browser dev tools network tab. Click "preview page" and look for the
`client_id` used in the requests.

### uploader_rules.py
SCOPES: `read:rules`, `update:rules`, `delete:rules`, `create:rules`

```
usage: uploader_rules.py [-h] [-u URI] -c CLIENTID -s CLIENTSECRET
                         [-r RULES_DIR]
uploader_rules.py: error: the following arguments are required: -c/--clientid, -s/--clientsecret
```

Example: `./uploader_rules.py -u auth-dev.mozilla.auth0.com -c AAA -s BBB -r rules`

Where the `rules` directory contains JSON and JS documents such as these:

AccessRules.json:
```
{
    "enabled": true,
    "order": 1
}
```

AccessRules.js:
```
function (user, context, callback) {
  ...code here...
  return callback(null, null, context);
}

```

Note that this is the Auth0 GitHub extension rule format.

### uploader_clients.py
SCOPES: `read:clients`, `update:clients`, `delete:clients`, `create:clients`
```
usage: uploader_clients.py [-h] [-u URI] -c CLIENTID -s CLIENTSECRET
                           [-r CLIENTS_DIR] [-g]
uploader_clients.py: error: the following arguments are required: -c/--clientid, -s/--clientsecret
```

Example: `./uploader_clients.py -u auth-dev.mozilla.auth0.com -c AAA -s BBB -r clients`

Where the `clients` directory contains JSON formated Auth0 client descriptions. You can get all current clients from
your Auth0 deployment to provision the initial setup with:

Example: `./uploader_clients.py -u auth-dev.mozilla.auth0.com -c AAA -s BBB -r clients -g`

A client JSON file looks such as this:

1gBNrcIdcyuus3S8DdK7O9A5iFrAdTmj.json <= the file name is the `client_id`
```
{
    "tenant": "auth-dev",
    "global": false,
    "is_token_endpoint_ip_header_trusted": false,
    "name": "cis_hris_publisher",
    "is_first_party": true,
    "sso_disabled": false,
    "cross_origin_auth": false,
    "oidc_conformant": false,
    "client_id": "1gBNrcIdcyuus3S8DdK7O9A5iFrAdTmj",
    "callback_url_template": false,
    "jwt_configuration": {
        "lifetime_in_seconds": 36000,
        "secret_encoded": false
    },
    "app_type": "non_interactive",
    "grant_types": [
        "authorization_code",
        "implicit",
        "refresh_token",
        "client_credentials"
    ],
    "custom_login_page_on": true
}
```
