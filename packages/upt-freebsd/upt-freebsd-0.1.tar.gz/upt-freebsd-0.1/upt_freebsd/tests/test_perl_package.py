# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_freebsd.upt_freebsd import FreeBSDPerlPackage


class TestPerlPackage(unittest.TestCase):
    def setUp(self):
        upt_pkg = upt.Package('foo', '42')
        self.freebsd_pkg = FreeBSDPerlPackage(upt_pkg, None)

    def test_freebsd_pkg_name(self):
        self.assertEqual(FreeBSDPerlPackage._freebsd_pkg_name('Test::More'),
                         'Test-More')

    def test_jinja2_reqformat(self):
        req = upt.PackageRequirement('foo::bar', '>=1.0')
        out = self.freebsd_pkg.jinja2_reqformat(req)
        self.assertEqual(out, 'p5-foo-bar>=1.0:XXX/p5-foo-bar')

    def test_jinja2_reqformat_no_specifier(self):
        req = upt.PackageRequirement('foo::bar', '')
        out = self.freebsd_pkg.jinja2_reqformat(req)
        self.assertEqual(out, 'p5-foo-bar>0:XXX/p5-foo-bar')


if __name__ == '__main__':
    unittest.main()
