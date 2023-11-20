import os
from typing import Any, Callable
from urllib.parse import urljoin

from google.auth.transport import Response
from google.auth.transport.requests import AuthorizedSession as DefaultAuthedSession

from dealroom_cloud_run_auth.id_token_credentials import (
    get_default_id_token_credentials,
)

URLJoiner = Callable[[str, str], str]
Timeout = float | tuple[float, float]

_120_SECONDS = 120.0


def default_url_joiner(base_url: str, path: str) -> str:
    """Use `urllib.parse.urljoin` to join the base URL and the path."""
    return urljoin(base_url + "/", path)


def default_user_agent() -> str | None:
    k_service = os.getenv("K_SERVICE")
    k_revision = os.getenv("K_REVISION")
    if k_service and k_revision:
        return f"{k_service}/{k_revision}"
    # These cases are unlikely to happen, but just in case
    elif k_service:
        return k_service
    elif k_revision:
        return k_revision


class AuthorizedBaseUrlSession(DefaultAuthedSession):

    """
    Session-like object that authorizes service-to-service requests through an
    ID token. The ID token is authorized for the target audience, which is the
    base URL used to initialize this session.

    It is a subclass of google.auth.transport.requests.AuthorizedSession that
    adds a number of features that come in handy for the services architecture
    used by the Data Team at Dealroom:

        * a URL that all requests will use as base:

        ```
        >>> cloud_run_url = "https://my-cloud-run-url.com"
        >>> session = AuthorizedBaseUrlSession(cloud_run_url)
        >>> response = session.get("resource")
        >>> print(response.request.url)
        https://my-cloud-run-url.com/resource
        ```

        By default, the base URL and the path are combined using `urljoin`. This
        works fine for most of the cases, but if it doesn't, you can override this
        behavior by passing a suitable callable to the `url_joiner` parameter:

        ```
        >>> cloud_run_url = "https://my-cloud-run-url.com"
        >>> session = AuthorizedBaseUrlSession(
        ...     cloud_run_url,
        ...     url_joiner=lambda base_url, path: base_url + "/" + path
        ... )
        >>> response = session.get("resource")
        >>> print(response.request.url)
        https://my-cloud-run-url.com/resource
        ```

        More info: https://github.com/requests/toolbelt/blob/master/requests_toolbelt/sessions.py

        * the `base_url` is used to initialize the credentials used to call that
        same service:

        ```
        >>> cloud_run_url = "https://my-cloud-run-url.com"
        >>> session = AuthorizedBaseUrlSession(cloud_run_url)
        >>> # Make a request to the Cloud Run, so that the token is generated
        >>> response = session.get("resource")
        >>> print(response.request.headers["Authorization"])
        # Prints a JWT token that authorizes requests to that Cloud Run.
        # Lasts for 1 hour
        ```

        The underlying credentials object takes care of refreshing the token
        when it's expired.

        More info: https://cloud.google.com/run/docs/authenticating/service-to-service

        * can set header "User-Agent" from the constructor:

        ```
        >>> cloud_run_url = "https://my-cloud-run-url.com"
        >>> user_agent = "my-user-agent"
        >>> session = AuthorizedBaseUrlSession(cloud_run_url, user_agent=user_agent)
        >>> print(session.headers["User-Agent"])
        my-user-agent
        ```

        It defaults to a suitable combination of env vars `K_SERVICE` and
        `K_REVISION`. These are reserved env vars in Cloud Run and Cloud Functions
        that are set to the name of the service. It is recommended to use this
        default, or provide a non-null value, as the user-agent appears in the
        request logs of the receiving service and thus can be used for debugging
        and monitoring.

        When None, it defaults to the User-Agent from the requests library:
        https://github.com/psf/requests/blob/2c2138e811487b13020eb331482fb991fd399d4e/requests/utils.py#L808

        More info:
        https://cloud.google.com/run/docs/container-contract#services-env-vars
        https://cloud.google.com/functions/docs/configuring/env-var#setting_build_environment_variables
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent

        * can set a session-wide timeout:

        ```
        >>> cloud_run_url = "https://my-cloud-run-url.com"
        >>> timeout = 5
        >>> session = AuthorizedBaseUrlSession(cloud_run_url, timeout=timeout)
        >>> print(session.timeout)
        5
        ```

        Any request-specific timeout will override the session-wide timeout for
        that specific request only.

        If unset or set to None, it defaults to 120 seconds.

        * can turn off keep-alive:

        ```
        >>> cloud_run_url = "https://my-cloud-run-url.com"
        >>> session = AuthorizedBaseUrlSession(cloud_run_url, keep_alive=False)
        >>> print(session.headers["Connection"])
        close
        ```

        This forces the connection to close after each request. In general, it's
        recommended to leave this as True, as it improves performance by reusing
        the connection.

        More info: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection
    """

    def __init__(
        self,
        base_url: str,
        *,
        user_agent: str | None = None,
        timeout: Timeout | None = _120_SECONDS,
        url_joiner: URLJoiner = default_url_joiner,
        keep_alive: bool = True,
    ) -> None:
        credentials = get_default_id_token_credentials(target_audience=base_url)
        super().__init__(credentials)

        self._base_url = base_url.rstrip("/")
        self._url_joiner = url_joiner
        self._timeout = timeout if timeout is not None else _120_SECONDS

        if ua := (user_agent or default_user_agent()):
            self.headers["User-Agent"] = ua

        if not keep_alive:
            self.headers["Connection"] = "close"

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def user_agent(self) -> str | bytes:
        return self.headers["User-Agent"]

    @property
    def timeout(self) -> Timeout:
        return self._timeout

    @property
    def url_joiner(self) -> URLJoiner:
        return self._url_joiner

    def request(self, method: str, path: str, *args, **kwargs) -> Any | Response:
        if kwargs.get("timeout") is None and self._timeout:
            # Not sure this is ok
            kwargs["timeout"] = self._timeout

        url = self._url_joiner(self._base_url, path)
        return super(AuthorizedBaseUrlSession, self).request(
            method, url, *args, **kwargs
        )


def create_session(
    base_url: str,
    *,
    user_agent: str | None = None,
    timeout: Timeout | None = _120_SECONDS,
    url_joiner: URLJoiner = default_url_joiner,
    keep_alive: bool = True,
) -> AuthorizedBaseUrlSession:
    """Returns a session object that can make authorized requests to a service.

    Args:
        base_url: The base URL of the service to authorize requests to. This is
            also used as the target audience to generate the ID token.
        url_joiner: A callable that takes a base URL and a path and returns the
            full URL. Defaults to `urllib.parse.urljoin`.
        user_agent: The value to set in the "User-Agent" header. Defaults to a
            suitable combination of env vars `K_SERVICE` and `K_REVISION`. It is
            recommended to keep this default in production environments.
        timeout: A session-wide timeout. Defaults to 120 seconds. Request-specific
            timeouts override this value for that specific request only.
        keep_alive: Whether to reuse the connection after each request. Defaults
            to `True`. It is recommended to leave this as is, as it improves
            performance by reusing the connection.
    """
    return AuthorizedBaseUrlSession(
        base_url=base_url,
        url_joiner=url_joiner,
        user_agent=user_agent,
        timeout=timeout,
        keep_alive=keep_alive,
    )
