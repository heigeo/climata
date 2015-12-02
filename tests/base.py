import unittest


class ClimataTestCase(unittest.TestCase):
    module = None

    def assertHasFields(self, item, fields):
        for field in fields:
            self.assertTrue(
                hasattr(item, field),
                "%s missing %s field" % (type(item).__name__, field)
            )
