"""Utitilies for writing tests manipulating temporary files/directories."""

import shutil
import tempfile

from django.db import models

try:
    from django.utils.six import string_types, text_type
except ImportError:
    # Too new, no six, must be python 3
    string_types = [str]
    text_type = str

from mock import Mock


class MockStorage(Mock):

    def save(self, name, content, max_length=None):
        return name

    def url(self, name):
        return '/uploads/{0}'.format(name)

    def get_valid_name(self, name):
        return name

    def generate_filename(self, thing):
        return text_type(thing)


mockstorage = MockStorage()


class TempFileMixin(object):

    def setUp(self):
        super(TempFileMixin, self).setUp()
        self.temp_dir = tempfile.mkdtemp()
        _, self.temp_name = tempfile.mkstemp(dir=self.temp_dir)
        with open(self.temp_name, 'w') as f:
            f.write('X')

    def tearDown(self):
        super(TempFileMixin, self).tearDown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class Example(models.Model):
    name = models.CharField(max_length=100)
    upload = models.FileField(storage=mockstorage, upload_to='test/')
