# Copyright 2016 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ddt
import mock

from os_win.tests import test_base
from os_win.utils import _acl_utils


@ddt.ddt
class ACLUtilsTestCase(test_base.OsWinBaseTestCase):
    def setUp(self):
        super(ACLUtilsTestCase, self).setUp()
        self._setup_lib_mocks()

        self._acl_utils = _acl_utils.ACLUtils()
        self._acl_utils._win32_utils = mock.Mock()
        self._mock_run = self._acl_utils._win32_utils.run_and_check_output

    def _setup_lib_mocks(self):
        self._ctypes = mock.Mock()
        self._ctypes.c_wchar_p = lambda x: (x, "c_wchar_p")
        self._ctypes.c_uint = lambda x: (x, 'c_uint')
        self._ctypes.c_ulong = lambda x: (x, 'c_ulong')

        mock.patch.multiple(_acl_utils,
                            ctypes=self._ctypes,
                            advapi=mock.DEFAULT,
                            kernel32=mock.DEFAULT,
                            create=True).start()

    def test_get_void_pp(self):
        pp_void = self._acl_utils._get_void_pp()

        self.assertEqual(pp_void, self._ctypes.pointer.return_value)
        self._ctypes.pointer.assert_called_once_with(
            self._ctypes.c_void_p.return_value)
        self._ctypes.c_void_p.assert_called_once_with()

    @ddt.data(
        {'security_info_flags':
            (_acl_utils.OWNER_SECURITY_INFORMATION |
             _acl_utils.GROUP_SECURITY_INFORMATION |
             _acl_utils.DACL_SECURITY_INFORMATION),
         'expected_info': ['pp_sid_owner', 'pp_sid_group',
                           'pp_dacl', 'pp_sec_desc']},
        {'security_info_flags': _acl_utils.SACL_SECURITY_INFORMATION,
         'expected_info': ['pp_sacl', 'pp_sec_desc']})
    @ddt.unpack
    @mock.patch.object(_acl_utils.ACLUtils, '_get_void_pp')
    def test_get_named_security_info(self, mock_get_void_pp,
                                     security_info_flags,
                                     expected_info):
        sec_info = self._acl_utils.get_named_security_info(
            mock.sentinel.obj_name,
            mock.sentinel.obj_type,
            security_info_flags)

        self.assertEqual(set(expected_info), set(sec_info.keys()))
        for field in expected_info:
            self.assertEqual(sec_info[field],
                             mock_get_void_pp.return_value)

        self._mock_run.assert_called_once_with(
            _acl_utils.advapi.GetNamedSecurityInfoW,
            self._ctypes.c_wchar_p(mock.sentinel.obj_name),
            self._ctypes.c_uint(mock.sentinel.obj_type),
            self._ctypes.c_uint(security_info_flags),
            sec_info.get('pp_sid_owner'),
            sec_info.get('pp_sid_group'),
            sec_info.get('pp_dacl'),
            sec_info.get('pp_sacl'),
            sec_info['pp_sec_desc'])

    @mock.patch.object(_acl_utils.ACLUtils, '_get_void_pp')
    def test_set_entries_in_acl(self, mock_get_void_pp):
        new_acl = mock_get_void_pp.return_value

        returned_acl = self._acl_utils.set_entries_in_acl(
            mock.sentinel.entry_count,
            mock.sentinel.entry_list,
            mock.sentinel.old_acl)

        self.assertEqual(new_acl, returned_acl)
        self._mock_run.assert_called_once_with(
            _acl_utils.advapi.SetEntriesInAclW,
            self._ctypes.c_ulong(mock.sentinel.entry_count),
            mock.sentinel.entry_list,
            mock.sentinel.old_acl,
            new_acl)
        mock_get_void_pp.assert_called_once_with()

    def test_set_named_security_info(self):
        self._acl_utils.set_named_security_info(
            mock.sentinel.obj_name,
            mock.sentinel.obj_type,
            mock.sentinel.security_info_flags,
            mock.sentinel.p_sid_owner,
            mock.sentinel.p_sid_group,
            mock.sentinel.p_dacl,
            mock.sentinel.p_sacl)

        self._mock_run.assert_called_once_with(
            _acl_utils.advapi.SetNamedSecurityInfoW,
            self._ctypes.c_wchar_p(mock.sentinel.obj_name),
            self._ctypes.c_uint(mock.sentinel.obj_type),
            self._ctypes.c_uint(mock.sentinel.security_info_flags),
            mock.sentinel.p_sid_owner,
            mock.sentinel.p_sid_group,
            mock.sentinel.p_dacl,
            mock.sentinel.p_sacl)