# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_freebsd.upt_freebsd import FreeBSDPythonPackage


class TestPythonPackage(unittest.TestCase):
    def setUp(self):
        upt_pkg = upt.Package('foo', '42')
        self.freebsd_pkg = FreeBSDPythonPackage(upt_pkg, None)

    def test_freebsd_pkg_name(self):
        out = self.freebsd_pkg._freebsd_pkg_name('requests')
        self.assertEqual(out, 'py-requests')

    def test_jinja2_reqformat(self):
        req = upt.PackageRequirement('foo', '>=1.0')
        out = self.freebsd_pkg.jinja2_reqformat(req)
        expected = '${PYTHON_PKGNAMEPREFIX}foo>=1.0:XXX/py-foo@${FLAVOR}'
        self.assertEqual(out, expected)

    def test_jinja2_reqformat_no_specifier(self):
        req = upt.PackageRequirement('foo', '')
        out = self.freebsd_pkg.jinja2_reqformat(req)
        expected = '${PYTHON_PKGNAMEPREFIX}foo>0:XXX/py-foo@${FLAVOR}'
        self.assertEqual(out, expected)


if __name__ == '__main__':
    unittest.main()
