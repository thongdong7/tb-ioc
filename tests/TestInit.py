# encoding=utf-8
import os

from os.path import join

from tb_ioc import IOC

__author__ = 'hiepsimu'
import logging
import unittest

logging.basicConfig(level=logging.DEBUG)

current_folder = os.path.abspath(os.path.dirname(__file__))
data_dir = join(current_folder, 'data')


class InitTestCase(unittest.TestCase):
    def test_01(self):
        ioc = IOC()

        actual = ioc.get('_Container')
        self.assertTrue(isinstance(actual, IOC))

    def test_unicode(self):
        ioc = IOC()
        ioc.load_file(join(data_dir, 'unicode.yml'))

        actual = ioc.get_parameter("A")
        expected = u'Tiếng Việt'

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
