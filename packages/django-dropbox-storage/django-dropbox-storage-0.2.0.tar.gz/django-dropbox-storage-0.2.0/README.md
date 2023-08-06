# django-dropbox-storage

> A Dropbox Storage for your Django apps

## What

`django-dropbox-storage` allows Django apps to use Dropbox as a storage backend for file uploading.

## Installing

First things first:

```
$ pip install django-dropbox-storage
```

Then open the `settings.py` of your project and include it to your `INSTALLED_APPS`:

```
INSTALLED_APPS = (
    ...
    'django_dropbox_storage',
    ...
)
```

If you want to use `django_dropbox_storage` as default storage for all file uploads, you need to adjust `DEFAULT_FILE_STORAGE` too:

```
DEFAULT_FILE_STORAGE = 'django_dropbox_storage.storage.DropboxStorage'
```

If you just want to use it on a single model field, you can simply import it:

```
from django_dropbox_storage.storage import DropboxStorage

DROPBOX_STORAGE = DropboxStorage()

photo = models.ImageField(upload_to='photos', storage=DROPBOX_STORAGE ...)
```

In order to let it work properly, you must set the next settings:

```
DROPBOX_ACCESS_TOKEN = 'xxx'
```

If you don't have `DROPBOX_ACCESS_TOKEN` you can create one after creating a Dropbox app at [Dropbox for Developers](https://www.dropbox.com/developers).
If you have your Dropbox `App key` and `App secret`, you can set `DROPBOX_CONSUMER_KEY` and `DROPBOX_CONSUMER_SECRET` settings in `settings.py`, then run:

```
$ python manage.py get_dropbox_token [--settings=test_settings]
```

And follow up on screen instructions, finally set the `DROPBOX_ACCESS_TOKEN_SECRET` in your `settings.py` module.

## Tests

Tests are written following Django's best practices.

In order to run them, you need to set `DROPBOX_ACCESS_TOKEN` properly.

**NOTE:** if you're testing this package as _stand-alone_, you can set the access token in a `local_settings.py` module put in the root folder.

To launch the test suite:

```
$ python manage.py test [--settings=test_settings]
```

To check the unit tests coverage you can:

```
$ pip install coverage
$ coverage run manage.py test [--settings=test_settings]
$ coverage report -m
```

## Contributing

When contributing, please follow these steps:

* Clone the repo and make your changes.
* Make sure your code has test cases written against it.
* Make sure all the tests pass.
* Lint your code with Flake8.
* Add your name to the list of contributers.
* Submit a Pull Request.

## Authors

* Emanuele Bertoldi

This project is based on previous work by:

* Andres Torres [django-dropbox]
* Maximiliano Cecilia [django-dropbox]
* Josh Schneier [django-storages]
* Danielle Madeley [django-storages]

**Thanks to all of you!**

## License

Copyright (c) 2018 Emanuele Bertoldi

[MIT License](http://en.wikipedia.org/wiki/MIT_License)

[django-dropbox]: https://github.com/andres-torres-marroquin/django-dropbox
[django-storages]: https://github.com/jschneier/django-storages
