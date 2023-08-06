# Django Key Value Settings
A small app for storing meta information for a Django app as KV pairs.
The settings are stored in the database.

## Version

2.0.0

## Features

* Stores meta-information/settings required by a typical project, for e.g the "License" text
* API for storing the data as string or as dict
* The value can be fetched directly as dict or as string

## Dependencies

* Django 1.7 or above

## Installation

Using pip

```
pip install kv_settings
```

## Setup

* Add the following in your settings.py file

```
INSTALLED_APPS = [
    ...
    'kv_settings',
    ...
]
```

* Run migrations

```
python manage.py migrate
```

## Properties

* **key:** A unique string to identify the setting.
* **value:** The value of the setting. Can be dict or a str.
* **notes:** A string for comments or notes on the setting.
* **added_on:** Added on datetime.
* **updated_on:** Last updated on datetime.

## Usage

Import it by

```
from kv_settings.models import KeyValueSetting
```

Create and fetch a setting

```
# Create or update an existing setting by
setting = KeyValueSetting.objects.set(key='some_setting', value={'foo': 'bar'})

# It can also be created like django model object
setting = KeyValueSetting(key='some_setting', value={'foo': 'bar'})
setting.save()

# Get the value back
setting = KeyValueSetting.objects.get_value(key='some_setting')
setting
>>> {"foo": "bar"}

# Or get the model obj
setting = KeyValueSetting.objects.get(key='some_setting')
setting
>>> <KeyValueSetting: some_setting>
```

## Future

Support for in-memory database might be provided.