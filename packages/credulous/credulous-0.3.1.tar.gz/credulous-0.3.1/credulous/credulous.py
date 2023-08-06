import copy
import datetime
import json
import time
from google_auth_oauthlib.flow import InstalledAppFlow

def format_as_credentials(
    input_secrets,
    credentials
):
    expiry_date = datetime.datetime.utcnow() + datetime.timedelta(hours = 1)
    formatted_expiry_date = expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    client_id = input_secrets['installed']['client_id']
    client_secret = input_secrets['installed']['client_secret']

    secrets = {
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'client_id': client_id,
        'client_secret': client_secret,
        'token_expiry': formatted_expiry_date,
        'user_agent': None,
        'token_response': {
            'token_type': 'Bearer',
            'expires_in': 3600,
            'access_token': credentials.token
        },
        'scopes': [],
        'invalid': False,
        'access_token': credentials.token,
        'id_token_jwt': None,
        'revoke_uri': 'https://accounts.google.com/o/oauth2/revoke',
        'token_info_uri': None,
        'id_token': None,
        '_class': 'OAuth2Credentials',
        'refresh_token': credentials.refresh_token,
        '_module': 'oauth2client.client'
    }

    return secrets

def format_as_client_secret(
    input_secrets,
    credentials
):
    secrets = copy.deepcopy(input_secrets)

    secrets['access_token'] = credentials.token
    secrets['refresh_token'] = credentials.refresh_token
    secrets['expires_in'] = 3600
    secrets['created'] = int(time.time())

    return secrets

class Credulous:
    def __init__(
        self,
        secret_path,
        scopes_path,
        output_path,
        format_function
    ):
        self.secret_path = secret_path
        self.scopes_path = scopes_path
        self.output_path = output_path
        self.format_function = format_function

    def authenticate(self):
        input_secrets = self._load(self.secret_path)
        scopes = self._load(self.scopes_path)['scopes']['google']

        flow = InstalledAppFlow.from_client_secrets_file(
            self.secret_path,
            scopes = scopes
        )

        credentials = flow.run_local_server(
            host = 'localhost',
            port = 8080,
            authorization_prompt_message = 'Please visit this URL: {url}',
            success_message = 'You may close this window.',
            open_browser = True
        )

        secrets = self.format_function(
            input_secrets,
            credentials
        )

        if 'developer_token' in input_secrets:
            secrets['developer_token'] = input_secrets['developer_token']

        if 'user_agent' in input_secrets:
            secrets['user_agent'] = input_secrets['user_agent']

        if 'customer_id' in input_secrets:
            secrets['customer_id'] = input_secrets['customer_id']

        if 'account_id' in input_secrets:
            secrets['account_id'] = input_secrets['account_id']

        self._store_secrets(secrets)
        print('Credentials saved in ' + self.output_path)

    def _load(self, file_path):
        with open(file_path) as handle:
            return json.load(handle)

    def _store_secrets(self, secrets):
        with open(self.output_path, 'w') as handle:
            json.dump(
                secrets,
                handle,
                indent = 4
            )
