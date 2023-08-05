# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import upt

from upt_nix.upt_nix import NixPerlPackage


class TestNixPerlPackage(unittest.TestCase):
    def setUp(self):
        self.upt_pkg = upt.Package('foo', '1.0')
        self.nix_pkg = NixPerlPackage(self.upt_pkg)

    def test_to_nix_name(self):
        self.assertEqual(self.nix_pkg._to_nix_name('Test::More'), 'TestMore')

    def test_url(self):
        self.upt_pkg.download_urls = [
            'https://cpan.metacpan.org/authors/id/' +
            'N/NE/NEILB/AppConfig-1.71.tar.gz'
        ]
        url = 'mirror://cpan/authors/id/N/NE/NEILB/AppConfig-1.71.tar.gz'
        self.assertEqual(self.nix_pkg.url, url)


if __name__ == '__main__':
    unittest.main()
