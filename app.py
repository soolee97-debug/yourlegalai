google.auth.exceptions.DefaultCredentialsError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/yourlegalai/app.py", line 64, in <module>
    client = vision.ImageAnnotatorClient()
File "/home/adminuser/venv/lib/python3.14/site-packages/google/cloud/vision_v1/services/image_annotator/client.py", line 726, in __init__
    self._transport = transport_init(
                      ~~~~~~~~~~~~~~^
        credentials=credentials,
        ^^^^^^^^^^^^^^^^^^^^^^^^
    ...<7 lines>...
        api_audience=self._client_options.api_audience,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/cloud/vision_v1/services/image_annotator/transports/grpc.py", line 242, in __init__
    super().__init__(
    ~~~~~~~~~~~~~~~~^
        host=host,
        ^^^^^^^^^^
    ...<6 lines>...
        api_audience=api_audience,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/cloud/vision_v1/services/image_annotator/transports/base.py", line 113, in __init__
    credentials, _ = google.auth.default(
                     ~~~~~~~~~~~~~~~~~~~^
        scopes=scopes,
        ^^^^^^^^^^^^^^
        quota_project_id=quota_project_id,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        default_scopes=self.AUTH_SCOPES,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/auth/_default.py", line 714, in default
    credentials, project_id = checker()
                              ~~~~~~~^^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/auth/_default.py", line 707, in <lambda>
    lambda: _get_explicit_environ_credentials(quota_project_id=quota_project_id),
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/auth/_default.py", line 352, in _get_explicit_environ_credentials
    credentials, project_id = load_credentials_from_file(
                              ~~~~~~~~~~~~~~~~~~~~~~~~~~^
        os.environ[environment_vars.CREDENTIALS],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        quota_project_id=quota_project_id,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/google/auth/_default.py", line 178, in load_credentials_from_file
    raise exceptions.DefaultCredentialsError(
        "File {} was not found.".format(filename)
    )
