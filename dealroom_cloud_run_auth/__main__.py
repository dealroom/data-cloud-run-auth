import google.auth.transport
from google.auth.transport import requests

from dealroom_cloud_run_auth.id_token_credentials import (
    get_default_id_token_credentials,
)


def get_default_id_token(request: google.auth.transport.Request) -> str | None:
    creds = get_default_id_token_credentials(target_audience=None)
    creds.refresh(request=request)
    return creds.token


print(get_default_id_token(requests.Request()))
