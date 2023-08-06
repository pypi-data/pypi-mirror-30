# PyCredulous

Copy of [PHP Credulous](https://github.com/brainlabs-digital/credulous) by ryutaro@brainlabsdigital.com

## Installation

```bash
pip install credulous
```

## Getting access and refresh tokens

Follow [these instructions](https://developers.google.com/gmail/api/quickstart/python) for downloading a `client_secret.json` file.
This should look something like

```json
{
    "installed": {
        "client_id": "...",
        "project_id": "...",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "...",
        "redirect_uris": [
            "urn:ietf:wg:oauth:2.0:oob",
            "http://localhost"
        ]
    }
}
```

Then create a `scopes.json` file containing the scopes that you want to authorize.
For example, if you want to use the AdWords API then you would have something like

```json
{
    "scopes": {
        "google": [
            "https://www.googleapis.com/auth/adwords"
        ]
    }
}
```

Then run

```bash
credulous --secret path/to/client_secret.json path/to/scopes.json
```

## Running with options

The `-c` flag exports credentials in a format compatible with the [oauth2client.client.Storage](https://developers.google.com/api-client-library/python/guide/aaa_oauth#storage) class.

```bash
credulous --secret path/to/client_secret.json path/to/scopes.json -c
```

The `-o` flag can be used to specify the output file. If this isn't specified then `client_secret.json` will be overwritten.

```bash
credulous --secret path/to/client_secret.json path/to/scopes.json -o path/to/output.json
```
