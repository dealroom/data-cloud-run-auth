# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import json
import os

import google.auth.transport
from google.auth import credentials as google_auth_credentials
from google.auth import environment_vars, exceptions
from google.oauth2 import credentials as oauth2_credentials
from google.oauth2 import service_account

# Valid types accepted for file-based credentials.
# They are taken  from "google.auth._default" and since they are all "protected" and the imports might
# change any time and fail the whole Google provider functionality - we should inline them
_AUTHORIZED_USER_TYPE = "authorized_user"
_SERVICE_ACCOUNT_TYPE = "service_account"
_EXTERNAL_ACCOUNT_TYPE = "external_account"
_EXTERNAL_ACCOUNT_AUTHORIZED_USER_TYPE = "external_account_authorized_user"
_IMPERSONATED_SERVICE_ACCOUNT_TYPE = "impersonated_service_account"
_GDCH_SERVICE_ACCOUNT_TYPE = "gdch_service_account"
_VALID_TYPES = (
    _AUTHORIZED_USER_TYPE,
    _SERVICE_ACCOUNT_TYPE,
    _EXTERNAL_ACCOUNT_TYPE,
    _EXTERNAL_ACCOUNT_AUTHORIZED_USER_TYPE,
    _IMPERSONATED_SERVICE_ACCOUNT_TYPE,
    _GDCH_SERVICE_ACCOUNT_TYPE,
)

_DEFAULT_SCOPES = ["openid"]


class IDTokenCredentialsAdapter(google_auth_credentials.Credentials):
    """Convert Credentials with `openid` scope to IDTokenCredentials."""

    def __init__(self, credentials: oauth2_credentials.Credentials) -> None:
        super().__init__()
        self.credentials = credentials
        self.token = credentials.id_token

    @property
    def expired(self) -> bool:
        return self.credentials.expired

    def refresh(self, request) -> None:
        self.credentials.refresh(request)
        self.token = self.credentials.id_token


def _load_credentials_from_file(
    filename: str, *, target_audience: str | None, scopes: list[str] | None = None
) -> google_auth_credentials.Credentials:
    """Loads credentials from a file.

    The credentials file must be a service account key or a stored authorized user credential.

    Args:
        filename: The full path to the credentials file.
        target_audience: The intended audience for these credentials. For example,
            the URL of a Cloud Run to authenticate to.
        scopes: Optional list of scopes to include in the credentials.

    Raises:
        google.auth.exceptions.DefaultCredentialsError: if the file is in the
            wrong format or is missing.
    """
    if not os.path.exists(filename):
        raise exceptions.DefaultCredentialsError(f"File {filename} was not found.")

    with open(filename) as file_obj:
        try:
            info = json.load(file_obj)
        except json.JSONDecodeError:
            raise exceptions.DefaultCredentialsError(
                f"File {filename} is not a valid json file."
            )

    # The type key should indicate that the file is either a service account
    # credentials file or an authorized user credentials file.
    credential_type = info.get("type")

    if credential_type == _AUTHORIZED_USER_TYPE:
        current_credentials = oauth2_credentials.Credentials.from_authorized_user_info(
            info, scopes=scopes
        )
        current_credentials = IDTokenCredentialsAdapter(credentials=current_credentials)

        return current_credentials

    elif credential_type == _SERVICE_ACCOUNT_TYPE:
        try:
            return service_account.IDTokenCredentials.from_service_account_info(
                info, target_audience=target_audience
            )
        except ValueError:
            raise exceptions.DefaultCredentialsError(
                f"Failed to load service account credentials from {filename}"
            )

    raise exceptions.DefaultCredentialsError(
        f"The file {filename} does not have a valid type. Type is {credential_type}, "
        f"expected one of {_VALID_TYPES}."
    )


def _get_explicit_environ_credentials(
    target_audience: str | None, scopes: list[str] | None = None
) -> google_auth_credentials.Credentials | None:
    """Gets credentials from the GOOGLE_APPLICATION_CREDENTIALS environment variable."""
    explicit_file = os.environ.get(environment_vars.CREDENTIALS)

    if explicit_file is None:
        return None

    current_credentials = _load_credentials_from_file(
        os.environ[environment_vars.CREDENTIALS],
        target_audience=target_audience,
        scopes=scopes,
    )

    return current_credentials


def _get_gcloud_sdk_credentials(
    target_audience: str | None, scopes: list[str] | None = None
) -> google_auth_credentials.Credentials | None:
    """Gets the credentials and project ID from the Cloud SDK."""
    from google.auth import _cloud_sdk

    # Check if application default credentials exist.
    credentials_filename = _cloud_sdk.get_application_default_credentials_path()

    if not os.path.isfile(credentials_filename):
        return None

    current_credentials = _load_credentials_from_file(
        credentials_filename, target_audience=target_audience, scopes=scopes
    )

    return current_credentials


def _get_gce_credentials(
    target_audience: str | None, request: google.auth.transport.Request | None = None
) -> google_auth_credentials.Credentials | None:
    """Gets credentials and project ID from the GCE Metadata Service."""
    # Ping requires a transport, but we want application default credentials
    # to require no arguments. So, we'll use the _http_client transport which
    # uses http.client. This is only acceptable because the metadata server
    # doesn't do SSL and never requires proxies.

    # While this library is normally bundled with compute_engine, there are
    # some cases where it's not available, so we tolerate ImportError.
    try:
        from google.auth import compute_engine
        from google.auth.compute_engine import _metadata
    except ImportError:
        return None

    from google.auth.transport import _http_client

    if request is None:
        request = _http_client.Request()

    if _metadata.ping(request=request):
        return compute_engine.IDTokenCredentials(
            request, target_audience, use_metadata_identity_endpoint=True
        )

    return None


def get_default_id_token_credentials(
    target_audience: str | None,
    request: google.auth.transport.Request | None = None,
    scopes: list[str] = _DEFAULT_SCOPES,
) -> google_auth_credentials.Credentials:
    """Gets the default ID Token credentials for the current environment.

    `Application Default Credentials` provides an easy way to obtain credentials
    to call Google APIs for server-to-server or local applications. For more info:
    https://developers.google.com/identity/protocols/application-default-credentials

    Args:
        target_audience: The intended audience for these credentials. For example,
            the URL of a Cloud Run to authenticate to.
        request: An object used to make HTTP requests. This is used to detect
            whether the application is running on Compute Engine. If not specified,
            then it will use the standard library http client to make requests.
        scopes: List of scopes to include in the credentials. Defaults to `openid`.

    Returns:
        The current environment's credentials.

    Raises:
        google.auth.exceptions.DefaultCredentialsError: If no credentials were
            found, or if the credentials found were invalid.
    """
    checkers = (
        lambda: _get_explicit_environ_credentials(target_audience, scopes),
        lambda: _get_gcloud_sdk_credentials(target_audience, scopes),
        lambda: _get_gce_credentials(target_audience, request),
    )

    for checker in checkers:
        current_credentials = checker()
        if current_credentials is not None:
            return current_credentials

    raise exceptions.DefaultCredentialsError(
        (
            "Could not automatically determine credentials."
            "\n\n"
            f"Please set {environment_vars.CREDENTIALS} or explicitly create credentials and re-run the application."
            "\n\n"
            "Alternatively, if you are developing locally and need to acquire new user credentials to use with ADC, run:"
            "\n\n"
            "    gcloud auth application-default login"
            "\n\n"
            "For more information, please see https://cloud.google.com/docs/authentication/getting-started"
        )
    )
