#  Copyright 2013 Cloudbase Solutions Srl
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

import mock
from oslotest import base

from oslo_windows import exceptions
from oslo_windows.utils import networkutilsv2


class NetworkUtilsV2TestCase(base.BaseTestCase):
    """Unit tests for the Hyper-V NetworkUtilsV2 class."""

    _MSVM_VIRTUAL_SWITCH = 'Msvm_VirtualEthernetSwitch'

    def setUp(self):
        super(NetworkUtilsV2TestCase, self).setUp()
        self._networkutils = networkutilsv2.NetworkUtilsV2()
        self._networkutils._conn = mock.MagicMock()

    def test_get_external_vswitch(self):
        mock_vswitch = mock.MagicMock()
        mock_vswitch.path_.return_value = mock.sentinel.FAKE_VSWITCH_PATH
        getattr(self._networkutils._conn,
                self._MSVM_VIRTUAL_SWITCH).return_value = [mock_vswitch]

        switch_path = self._networkutils.get_external_vswitch(
            mock.sentinel.FAKE_VSWITCH_NAME)

        self.assertEqual(mock.sentinel.FAKE_VSWITCH_PATH, switch_path)

    def test_get_external_vswitch_not_found(self):
        self._networkutils._conn.Msvm_VirtualEthernetSwitch.return_value = []

        self.assertRaises(exceptions.HyperVException,
                          self._networkutils.get_external_vswitch,
                          mock.sentinel.FAKE_VSWITCH_NAME)

    def test_get_external_vswitch_no_name(self):
        mock_vswitch = mock.MagicMock()
        mock_vswitch.path_.return_value = mock.sentinel.FAKE_VSWITCH_PATH

        mock_ext_port = self._networkutils._conn.Msvm_ExternalEthernetPort()[0]
        self._prepare_external_port(mock_vswitch, mock_ext_port)

        switch_path = self._networkutils.get_external_vswitch(None)
        self.assertEqual(mock.sentinel.FAKE_VSWITCH_PATH, switch_path)

    def _prepare_external_port(self, mock_vswitch, mock_ext_port):
        mock_lep = mock_ext_port.associators()[0]
        mock_lep1 = mock_lep.associators()[0]
        mock_esw = mock_lep1.associators()[0]
        mock_esw.associators.return_value = [mock_vswitch]

    def test_create_vswitch_port(self):
        self.assertRaises(
            NotImplementedError,
            self._networkutils.create_vswitch_port,
            mock.sentinel.FAKE_VSWITCH_PATH,
            mock.sentinel.FAKE_PORT_NAME)

    def test_vswitch_port_needed(self):
        self.assertFalse(self._networkutils.vswitch_port_needed())
