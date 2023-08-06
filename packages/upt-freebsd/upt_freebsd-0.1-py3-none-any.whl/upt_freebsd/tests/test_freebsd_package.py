# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest
from unittest import mock

import upt

from upt_freebsd.upt_freebsd import FreeBSDPackage


class TestDirectoryCreation(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '42')

    @mock.patch('os.getcwd')
    @mock.patch('os.makedirs')
    def test_create_directory_no_output(self, m_mkdir, m_cwd):
        m_cwd.return_value = '/cwd'
        freebsd_pkg = FreeBSDPackage(self.upt_pkg, None)
        freebsd_pkg._create_output_directory()
        m_mkdir.assert_called_with('/cwd/foo')

    @mock.patch('os.makedirs')
    def test_create_directory_output(self, m_mkdir):
        freebsd_pkg = FreeBSDPackage(self.upt_pkg, '/path/to/dir')
        freebsd_pkg._create_output_directory()
        m_mkdir.assert_called_with('/path/to/dir/foo')

    @mock.patch('os.path.expanduser')
    @mock.patch('os.makedirs')
    def test_create_directory_output_tilde(self, m_mkdir, m_expand):
        m_expand.return_value = '/home/user/ports'
        freebsd_pkg = FreeBSDPackage(self.upt_pkg, '~/ports')
        freebsd_pkg._create_output_directory()
        m_mkdir.assert_called_with('/home/user/ports/foo')


class TestFreeBSDPackage(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '42')
        self.freebsd_pkg = FreeBSDPackage(self.upt_pkg, None)

    def test_jinja2_reqformat(self):
        req = upt.PackageRequirement('foo', '>=1.0')
        out = self.freebsd_pkg.jinja2_reqformat(req)
        self.assertEqual(out, 'foo>=1.0:XXX/foo')

    def test_jinja2_reqformat_no_specifier(self):
        req = upt.PackageRequirement('foo', '')
        out = self.freebsd_pkg.jinja2_reqformat(req)
        self.assertEqual(out, 'foo>0:XXX/foo')

    def test_categories(self):
        self.freebsd_pkg.output_dir = '/usr/ports/ports-mgmt/py-upt-freebsd'
        self.freebsd_pkg.language_category = 'language'
        self.assertListEqual(self.freebsd_pkg.categories,
                             ['ports-mgmt', 'language'])

    def test_categories_invalid_category(self):
        self.freebsd_pkg.output_dir = '/usr/ports/invalid/py-upt-freebsd'
        self.freebsd_pkg.language_category = 'language'
        self.assertListEqual(self.freebsd_pkg.categories, ['XXX', 'language'])


if __name__ == '__main__':
    unittest.main()
