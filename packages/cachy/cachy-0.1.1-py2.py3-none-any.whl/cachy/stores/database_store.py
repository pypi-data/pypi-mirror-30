# -*- coding: utf-8 -*-

import time
from ..contracts.store import Store


try:
    from orator import DatabaseManager
except ImportError:
    DatabaseManager = None


try:
    from cryptography.fernet import Fernet

    class Encrypter(Fernet):

        def __init__(self, key, store):
            self._store = store

            super(Encrypter, self).__init__(key)

        def encrypt(self, value):
            value = self._store.serialize(value)

            return super(Encrypter, self).encrypt(value)

        def decrypt(self, value):
            data = super(Encrypter, self).decrypt(value)

            return self._store.unserialize(data)

except ImportError:
    Encrypter = None


class DatabaseStore(Store):
    """
    A cache store using a database as its backend.
    """

    def __init__(self, config, encryption, table, prefix=''):
        """
        :param config: The database configuration
        :type config: dict

        :param encryption: The encryption config
        :type encryption: dict

        :param table: The database table used for caching
        :type table: str

        :param prefix: The cache prefix
        :type prefix: str
        """
        if DatabaseManager is None:
            raise RuntimeError('The [orator] module must be installed '
                               'to use the database store.')

        if Encrypter is None:
            raise RuntimeError('The [cryptography] module must be installed '
                               'to use the database store.')

        self._table = table
        self._prefix = prefix
        self._encrypter = Encrypter(encryption['key'], self)
        self._connection = DatabaseManager(config).connection()

    def get(self, key):
        """
        Retrieve an item from the cache by key.

        :param key: The cache key
        :type key: str

        :return: The cache value
        """
        prefixed = self._prefix + key

        cache = self.table().where('key', '=', prefixed).first()
        # If we have a cache record we will check the expiration time against current
        # time on the system and see if the record has expired. If it has, we will
        # remove the records from the database table so it isn't returned again.
        if cache is not None:
            if self._get_time() >= cache['expiration']:
                self.forget(key)

                return

            return self._encrypter.decrypt(cache['value'])

    def put(self, key, value, minutes):
        """
        Store an item in the cache for a given number of minutes.

        :param key: The cache key
        :type key: str

        :param value: The cache value
        :type value: mixed

        :param minutes: The lifetime in minutes of the cached value
        :type minutes: int
        """
        key = self._prefix + key

        value = self._encrypter.encrypt(value)

        expiration = self._get_time() + minutes * 60

        try:
            self.table().insert(
                key=key,
                value=value,
                expiration=int(expiration)
            )
        except Exception:
            self.table().where('key', '=', key).update(value=value, expiration=expiration)

    def increment(self, key, value=1):
        """
        Increment the value of an item in the cache.

        :param key: The cache key
        :type key: str

        :param value: The increment value
        :type value: int

        :rtype: int or bool
        """
        with self._connection.transaction():
            return self._increment_or_decrement(
                key, value,
                lambda current: current + value
            )

    def decrement(self, key, value=1):
        """
        Decrement the value of an item in the cache.

        :param key: The cache key
        :type key: str

        :param value: The decrement value
        :type value: int

        :rtype: int or bool
        """
        with self._connection.transaction():
            return self._increment_or_decrement(
                key, value,
                lambda current: current - value
            )

    def _increment_or_decrement(self, key, value, callback):
        """
        Increment or decrement an item in the cache.

        :param key: The cache key
        :type key: str

        :param value: The increment or decrement value
        :type value: int

        :param callback: The callback to execute
        :type callback: callable
        """
        prefixed = self._prefix + key

        cache = self.table().where('key', '=', prefixed).lock_for_update().first()

        if cache is not None:
            current = self._encrypter.decrypt(cache['value'])

            if current.is_digit():
                self.table().where('key', '=', prefixed).update(
                    value = self._encrypter.encrypt(callback(current))
                )

    def _get_time(self):
        """
        Get the current system time.

        :rtype: int
        """
        return int(time.time())

    def forever(self, key, value):
        """
        Store an item in the cache indefinitely.

        :param key: The cache key
        :type key: str

        :param value: The value
        :type value: mixed
        """
        return self.put(key, value, 5256000)

    def forget(self, key):
        """
        Remove an item from the cache.

        :param key: The cache key
        :type key: str

        :rtype: bool
        """
        self.table().where('key', '=', self._prefix + key).delete()

        return True

    def flush(self):
        """
        Remove all items from the cache.
        """
        self.table().delete()

    def table(self):
        """
        Get a query builder for the cache table.

        :rtype: orator.query.builder.Builder
        """
        return self._connection.table(self._table)

    def get_prefix(self):
        """
        Get the cache key prefix.

        :rtype: str
        """
        raise NotImplementedError()
