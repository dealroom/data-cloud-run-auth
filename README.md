# Cloud Run Auth

Make authorized requests to private services in GCP using a `requests`-like interface.

The caller may be an authorized user (e.g. a developer using this library locally), or an authorized Service Account (e.g. a DataFlow job that needs to call one or more service).

Terminology:

* **Service**: a Cloud Run or a Cloud Function.

* **Authorized**: a caller that has the appropriate role to call the service, that is `roles/run.invoker` for Cloud Run, `roles/cloudfunctions.invoker` for Cloud Functions.

## Install

* **Poetry**:

    ```shell
    poetry add git+https://github.com/dealroom/data-cloud-run-auth.git#main
    ```

* **pip**:

    ```shell
    pip install git+https://github.com/dealroom/data-cloud-run-auth.git@main
    ```

## Usage

This package provides a session-like object that can be used to make authorized requests to a Cloud Run or a Cloud Function.

In 90% of the cases, you use it like so:

* make authorized requests to a Cloud Run:

    ```python
    from dealroom_cloud_run_auth import create_session

    cloud_run_url = "https://my-cloud-run-service.com"
    session = create_session(cloud_run_url)
    # Using "/my-endpoint" or "my-endpoint" makes no difference
    response = session.get("/my-endpoint")
    ```

* make authorized requests to a Cloud Function:

    ```python
    from dealroom_cloud_run_auth import create_session

    # Use the full URL for Cloud Functions, as the base URL is the same for
    # all functions in a certain zone
    cloud_function_url = "https://cloud-functions.com/function-name"
    session = create_session(cloud_function_url)
    response = session.post("", json={"key": "value"})
    ```

For the remainder 10%:

* you may want to set a custom timeout:

    ```python
    ...
    session = create_session(cloud_run_url, timeout=10)
    ...
    ```

* you may want to set a custom user agent. For example, the user agent is not set when you use this package locally, so you could set it yourself:

    ```python
    ...
    session = create_session(cloud_run_url, user_agent="my-user-agent")
    ...
    ```

📢 ⚠️ You should not need to set the user agent in production, as it is set automatically to a value that identifies the caller.

To know more about these and other parameters, check out the docstrings of class `AuthorizedBaseUrlSession`.

### Troubleshooting

If for any reason the library cannot get the ID token credentials to call the service, it will raise a `google.auth.exceptions.DefaultCredentialsError` exception.

### Best practices

* Module structure: `services/` module.

* How to do retries (tenacity vs. Retry from urllib).

## Development

* Install environment and activate it:

    ```shell
    poetry install && poetry shell
    ```

* Refresh requirements files:

    ```shell
    ./scripts/export_requirements.sh
    ```

## References

* This package is based on the [Airflow module to get ID token credentials in GCP](https://github.com/apache/airflow/blob/b1196460db1a21b2c6c3ef2e841fc6d0c22afe97/airflow/providers/google/common/utils/id_token_credentials.py#L1)

* [Google Cloud Run - Authenticating service-to-service](https://cloud.google.com/run/docs/authenticating/service-to-service)

* [Google Cloud Run - Authenticating developers](https://cloud.google.com/run/docs/authenticating/developers)
