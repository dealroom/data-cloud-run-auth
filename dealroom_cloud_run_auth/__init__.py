"""
For quick local development, you can execute this module to get an ID token:

    python -m dealroom_cloud_run_auth

To decode and obtain info about this token, run the following commands:

    ID_TOKEN="$(python -m dealroom_cloud_run_auth)"
    curl "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=${ID_TOKEN}"
"""


from dealroom_cloud_run_auth.session import create_session
