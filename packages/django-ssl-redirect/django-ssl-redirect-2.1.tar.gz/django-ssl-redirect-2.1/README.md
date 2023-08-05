Django SSL Redirect
===================

Django SSL Redirect is a middleware that ensures secured URLs and only secured URLs are accessed securely over HTTPS.

Installation
------------

Run `pip install django-ssl-redirect`

Add `ssl_redirect.middleware.SSLRedirectMiddleware` to the top of your MIDDLEWARE_CLASSES setting:

```python
MIDDLEWARE_CLASSES = (
    'ssl_redirect.middleware.SSLRedirectMiddleware',
	...
)
```

Securing Views
--------------
To secure a view simply add `'SSL': True` the views kwargs

```python
urlpatterns = patterns('my_app.views',
    url(r'^secure/path/$', 'secure_view', {'SSL':True}),
)
```

You can always ensure a view is not served over SSL with `'SSL': True`

```python
urlpatterns = patterns('my_app.views',
    url(r'^unsecure/path/$', 'secure_view', {'SSL': False}),
)
```

Settings
--------
`SSL_ON (default True)`
Use SSL redirects. This setting overrides all other settings.

`SSL_ALWAYS (default False)`
Use SSL throughout the entire site.

`HTTPS_PATHS (default [])`
A list of secure paths.

`SSL_PORT (default None)`
Port number of the SSL connection. If the value is not None it will be appended after the host.