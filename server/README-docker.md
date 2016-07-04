# Grader server Docker image

You probably want to use the [compose file](https://github.com/whs/grader) as this
does not include other required services.

Run with

```
sudo docker run -e SECRET=randomstring -e ALLOWED_HOST=example.com \
    -e ADMIN_PASSWORD=hackme \
    -v /path/to/store:/data \
    -p 8080:80 willwill/grader
```

## Environment variables

These variables will be put into Python string without escaping, so make sure
quotation marks (") are escaped.

- SECRET: **required** grader runner secret communication token (any random string)
- SECRET_KEY: Django's `SECRET_KEY`. Will be randomized on start if you didn't set one.
- DATABASE_URL: Database URL to connect. Defaults to `sqlite:///data/db.sqlite`
- ALLOWED_HOST: Allowed `Host` headers to connect. Set to your production URL.
  Defaults to `localhost` and **debug mode will be enabled**
- BEANSTALK: Beanstalkd IP or hostname. Defaults to `127.0.0.1` which is probably invalid.
- BEANSTALK_PORT: Beanstalkd port. Defaults to `11300`
- REGISTER_ALLOWED: Set to `false` to disable register.
- ADMIN_USERNAME: Admin user to create, defaults to admin
- ADMIN_PASSWORD: Admin password to create, if left blank no admin user will be created
- ADMIN_EMAIL: Admin email to create, defaults to empty.
- WAIT_FOR_IT: Run [wait-for-it](https://github.com/vishnubob/wait-for-it) with the given arguments.

## Volumes

Mount `/data` to store your uploaded files. Also the default configuration will store a sqlite file there.
