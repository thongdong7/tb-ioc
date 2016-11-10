# encoding=utf-8
import os

from os.path import join

from tb_ioc import IOC
from tests_tb_ioc.sample import HelloService

__author__ = 'hiepsimu'
import logging
import unittest

logging.basicConfig(level=logging.DEBUG)

current_folder = os.path.abspath(os.path.dirname(__file__))
data_dir = join(current_folder, 'data')


def load_ioc(path):
    ioc = IOC()
    ioc.load_file(join(data_dir, '%s.yml' % path))

    return ioc


class InitTestCase(unittest.TestCase):
    def test_01(self):
        ioc = IOC()

        actual = ioc.get('_Container')
        self.assertTrue(isinstance(actual, IOC))

    def test_unicode(self):
        ioc = load_ioc('unicode')

        actual = ioc.get_parameter("A")
        expected = u'Tiếng Việt'

        self.assertEqual(expected, actual)

    def test_method(self):
        ioc = load_ioc('ioc_method')
        hello_method = ioc.get('MyMethod')
        actual = hello_method('Peter')

        self.assertEqual('Hello Peter', actual)

        hello_method_result = ioc.get('MyMethodResult')
        self.assertEqual('Hello Peter', hello_method_result)

    def test_method_with_calls(self):
        ioc = load_ioc('ioc_method')
        hello_john = ioc.get('HelloJohnService')
        self.assertEqual('John', hello_john.name)

    def test_short_method(self):
        ioc = load_ioc('ioc_method')
        hello_moto = ioc.get('HelloMotoService')
        self.assertEqual('Moto', hello_moto.name)

        hello_moto_kwargs = ioc.get('HelloMotoKwargsService')
        self.assertEqual('Moto', hello_moto_kwargs.name)

    def test_class(self):
        ioc = load_ioc('ioc_class')
        service = ioc.get('MyService')
        self.assertTrue(isinstance(service, HelloService))

        self.assertEqual('Peter', service.name)

        # Test alias
        alias_service = ioc.get('MyAliasService')
        self.assertEqual('Peter', alias_service.name)

    def test_factory(self):
        ioc = load_ioc('ioc_factory')
        service = ioc.get('MyService')
        self.assertTrue(isinstance(service, HelloService))

        self.assertEqual('Peter', service.name)


if __name__ == '__main__':
    unittest.main()
