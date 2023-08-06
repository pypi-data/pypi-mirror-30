import json
from json.decoder import JSONDecodeError

from django.db import models


class KeyValueSettingManager(models.Manager):
    def set(self, key, value):
        """
        Creates or updates a setting by the key.

        Inputs:

            key (str) = The key of the setting
            value (str or dict) = The setting's value

        Returns:

            KeyValueSetting (obj) = The setting object
        """
        # if isinstance(value, dict):
        #     value = json.dumps(value)
        setting, created = self.update_or_create(
            key=key,
            defaults={'value': value})
        return setting

    def get_value(self, key):
        """
        Gets a setting's value by the key.

        Inputs:

            key = The key of the setting

        Returns:

            value (str or dict) = The setting's value
        """
        key_value_setting = super(KeyValueSettingManager, self).get_queryset().get(key=key)
        try:
            return json.loads(key_value_setting.value)
        except (JSONDecodeError, ValueError):
            return key_value_setting.value


class KeyValueSetting(models.Model):
    key = models.CharField(
        unique=True,
        max_length=255)
    value = models.TextField()
    notes = models.TextField(
        blank=True)
    added_on = models.DateTimeField(
        auto_now_add=True)
    updated_on = models.DateTimeField(
        auto_now=True)

    objects = KeyValueSettingManager()

    @property
    def get_value(self):
        """
        Gets a setting's value.

        Inputs:

            key = The key of the setting

        Returns:

            value (str or dict) = The setting's value
        """
        try:
            return json.loads(self.value)
        except (JSONDecodeError, ValueError):
            return self.value

    def save(self, *args, **kwargs):
        if isinstance(self.value, dict):
            self.value = json.dumps(self.value)
        return super(KeyValueSetting, self).save(*args, **kwargs)

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'key value setting'
        verbose_name_plural = 'key value settings'
