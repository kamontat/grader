# Grader server Docker image

## Environment variables

These variables will be put into Python string without escaping, so make sure
quotation marks (") are escaped.

- SECRET: **required** grader runner secret communication token (any random string)
- SECRET_KEY: Django's `SECRET_KEY`. Will be randomized on start if you didn't set one. Required for distributed API setup
- DATABASE_URL: Database URL to connect. Defaults to `sqlite:///data/db.sqlite`
- ALLOWED_HOST: Allowed `Host` headers to connect. Set to your production URL. Defaults to `localhost`
- BEANSTALK: Beanstalkd IP or hostname. Defaults to `127.0.0.1` which is probably invalid.
- BEANSTALK_PORT: Beanstalkd port. Defaults to `11300`
- REGISTER_ALLOWED: Set to `false` to disable register.
