django-request-logger
==========================

Plug django-request-logger into your Django project to save request information to database.

## Installing

```bash
$ pip install django-request-logger
```

Add ```request_logger``` to you ```INSTALLED_APPS```

Then add ```request_logger.middleware.LoggerMiddleware``` to your ```MIDDLEWARE_CLASSES```.

For example:

```
MIDDLEWARE_CLASSES = (
    ...,
    'request_logger.middleware.LoggerMiddleware',
    ...,
)
```
