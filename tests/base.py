import unittest
import httpretty
from wq.io import load_file
from os.path import join
from os import environ
import re


class ClimataTestCase(unittest.TestCase):
    module = None

    def setUp(self):
        if environ.get('CLIMATA_DIRECT', None):
            return
        httpretty.enable()
        for row in load_file(join('tests', 'file_list.csv')):
            if row.module != self.module:
                continue
            f = file(join('tests', 'files', row.module + '_' + row.filename))
            data = f.read()
            f.close()
            method = getattr(httpretty, row.method.upper())
            url = row.url
            for char in '.?+':
                url = url.replace(char, '\\' + char)

            httpretty.register_uri(
                method,
                re.compile(url),
                body=data,
                match_querystring=True,
            )

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def assertHasFields(self, item, fields):
        for field in fields:
            self.assertTrue(
                hasattr(item, field),
                "%s missing %s field" % (type(item).__name__, field)
            )
