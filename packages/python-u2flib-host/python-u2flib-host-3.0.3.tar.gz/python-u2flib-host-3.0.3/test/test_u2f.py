# Copyright (c) 2016 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from u2flib_host import u2f, u2f_v2
import unittest


class MockDevice(object):

    def __init__(self, *versions):
        self._versions = versions

    def get_supported_versions(self):
        return self._versions

    def send_apdu(self, ins, p1, p2, request):
        return b''


class TestU2F(unittest.TestCase):

    def test_get_lib_supported(self):
        lib = u2f.get_lib(MockDevice('U2F_V2'), {'version': 'U2F_V2'})
        self.assertEqual(lib, u2f_v2)

        lib = u2f.get_lib(MockDevice('foo', 'U2F_V2'), {'version': 'U2F_V2'})
        self.assertEqual(lib, u2f_v2)

        lib = u2f.get_lib(MockDevice('U2F_V2', 'bar'), {'version': 'U2F_V2'})
        self.assertEqual(lib, u2f_v2)

    def test_get_lib_unsupported_by_device(self):
        self.assertRaises(ValueError, u2f.get_lib,
                          MockDevice('unknown', 'versions'),
                          {'version': 'U2F_V2'})

    def test_get_lib_unsupported_by_lib(self):
        self.assertRaises(ValueError, u2f.get_lib,
                          MockDevice('U2F_V2'),
                          {'version': 'invalid_version'})
