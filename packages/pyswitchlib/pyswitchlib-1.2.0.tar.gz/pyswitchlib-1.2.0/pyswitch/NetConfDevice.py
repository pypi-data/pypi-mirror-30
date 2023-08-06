import re
import sys
import xml.etree.ElementTree as ET

import ncclient
from lxml import etree as letree
from ncclient import manager
from ncclient import xml_

import pyswitch.raw.nos.base.acl.acl
import pyswitch.raw.slxos.base.acl.acl
import pyswitch.raw.slxos.ver_16r.acl
import pyswitch.raw.slxos.ver_17s.acl
import pyswitch.raw.nos.base.interface
import pyswitch.raw.slxos.base.interface
import pyswitch.utilities as util
from pyswitch.AbstractDevice import AbstractDevice
from pyswitch.AbstractDevice import DeviceCommError

NOS_ATTRS = ['snmp', 'interface', 'bgp', 'lldp', 'system', 'services',
             'fabric_service', 'vcs', 'acl']


NOS_VERSIONS = {
    '6.0': {
        'interface': pyswitch.raw.nos.base.interface.Interface,
        'acl': pyswitch.raw.nos.base.acl.acl.Acl,
    },
    '7.0': {
        'interface': pyswitch.raw.nos.base.interface.Interface,
        'acl': pyswitch.raw.nos.base.acl.acl.Acl,
    },
    '7.1': {
        'interface': pyswitch.raw.nos.base.interface.Interface,
        'acl': pyswitch.raw.nos.base.acl.acl.Acl,
    },
    '7.2': {
        'interface': pyswitch.raw.nos.base.interface.Interface,
        'acl': pyswitch.raw.nos.base.acl.acl.Acl,
    },
}
SLXOS_VERSIONS = {
    '16r.1': {
        'interface': pyswitch.raw.slxos.base.interface.Interface,
        'acl': pyswitch.raw.slxos.ver_16r.acl.Acl,
    },
    '17r.1': {
        'interface': pyswitch.raw.slxos.base.interface.Interface,
        'acl': pyswitch.raw.slxos.base.acl.acl.Acl,
    },
    '17r.2': {
        'interface': pyswitch.raw.slxos.base.interface.Interface,
        'acl': pyswitch.raw.slxos.base.acl.acl.Acl,
    },
    '17s.1': {
        'interface': pyswitch.raw.slxos.base.interface.Interface,
        'acl': pyswitch.raw.slxos.ver_17s.acl.Acl,
    },

}


class NetConfDevice(AbstractDevice):
    """
       Device object holds the state for a single NOS device.
       Attributes:
           bgp: BGP related actions and attributes.
           interface: Interface related actions and attributes.
           snmp: SNMP related actions and attributes.
           lldp: LLDP related actions and attributes.
           system: System level actions and attributes.
       """

    def __init__(self, **kwargs):
        """
        Args:
            conn (tuple): IP/Hostname and port of the VDX device you
                intend to connect to. Ex. ('10.0.0.1', '22')
            auth (tuple): Username and password of the VDX device you
                intend to connect to. Ex. ('admin', 'password')
            hostkey_verify (bool): True to verify hostkey, False to bypass
                verify.
            auth_method (string): ```key``` if using ssh-key auth.
                ```userpass``` if using username/password auth.
            auth_key (string): Location of ssh key to use for authentication.
        Returns:
            Instance of the device object.
        Examples:
            >>> from pprint import pprint
            >>> import pyswitch.rawdevice1
            >>> conn = ('10.24.39.211', '22')
            >>> auth = ('admin', 'password')
            >>> dev = pyswitch.rawdevice1.Device(conn=conn, auth=auth)
            >>> dev.connection
            True
            >>> del dev
            >>> with pyswitch.rawdevice1.Device(conn=conn, auth=auth) as dev:
            ...     pprint(dev.mac_table) # doctest: +ELLIPSIS
            [{'interface'...'mac_address'...'state'...'type'...'vlan'...}]
            >>> dev.connection
            False
        """
        self.base = kwargs.pop('base')
        self._conn = kwargs.pop('conn')
        self._auth = kwargs.pop('auth', (None, None))
        if 'auth_snmp' in kwargs:
            auth_snmp = kwargs.pop('auth_snmp', (None, None, None, None))
            self._auth = (auth_snmp[0], auth_snmp[1])
        self._hostkey_verify = kwargs.pop('hostkey_verify', None)
        self._auth_method = kwargs.pop('auth_method', 'userpass')
        self._auth_key = kwargs.pop('auth_key', None)
        self._test = kwargs.pop('test', False)
        self._callback = kwargs.pop('callback', None)
        if self._callback is None:
            self._callback = self._callback_main

        self._mgr = None

        self.reconnect()
        self._fetch_firmware_version()
        self.platform_type_val = None

        self.fullver = self.firmware_version

        thismodule = sys.modules[__name__]

        self.os_table = getattr(thismodule, '%s_VERSIONS' % str(self.os_type).upper())

        if self.fullver in self.os_table:
            self.ver = self.fullver
        else:
            self.ver = util.get_two_tuple_version(self.fullver)

        for nos_attr in NOS_ATTRS:
            if nos_attr in self.os_table[self.ver]:
                setattr(
                    self.base,
                    nos_attr,
                    self.os_table[self.ver][nos_attr](
                        self._callback_main))

    def __enter__(self):
        if not self.connection and self._test is False:
            self.reconnect()
        return self

    def __exit__(self, exctype, excisnt, exctb):
        if self.connection:
            self.close()

    @property
    def connection(self):
        """
        Poll if object is still connected to device in question.
        Args:
            None
        Returns:
            bool: True if connected, False if not.
        Raises:
            None
        """
        if self._test is False:
            return self._mgr.connected
        else:
            return False

    def reconnect(self):
        """
        Reconnect session with device.
        Args:
            None
        Returns:
            bool: True if reconnect succeeds, False if not.
        Raises:
            None
        """
        if self._auth_method is "userpass":
            self._mgr = manager.connect(host=self._conn[0],
                                        port=self._conn[1],
                                        username=self._auth[0],
                                        password=self._auth[1],
                                        hostkey_verify=self._hostkey_verify)
        elif self._auth_method is "key":
            self._mgr = manager.connect(host=self._conn[0],
                                        port=self._conn[1],
                                        username=self._auth[0],
                                        key_filename=self._auth_key,
                                        hostkey_verify=self._hostkey_verify)
        else:
            raise ValueError("auth_method incorrect value.")
        self._mgr.timeout = 600

        return True

    @property
    def platform_type(self):
        return self.platform_type_val

    def _callback_main(self, call, handler='edit_config', target='running',
                       source='startup'):
        """
        Callback for NETCONF calls.
        Args:
            call: An Element Tree element containing the XML of the NETCONF
                call you intend to make to the device.
            handler: Type of ncclient call to make.
                get_config: NETCONF standard get config.
                get: ncclient dispatch. For custom RPCs.
                edit_config: NETCONF standard edit.
                delete_config: NETCONF standard delete.
                copy_config: NETCONF standard copy.
            target: Target configuration location for action. Only used for
                edit_config, delete_config, and copy_config.
            source: Source of configuration information for copying
                configuration. Only used for copy_config.
        Returns:
            None
        Raises:
            None
        """
        try:
            if handler == 'get_config':
                output = self._mgr.get_config(filter=('xpath', call), source='running')
                # pylint: disable=E1101
                return ET.fromstring(letree.tostring(output.data))

            if handler == 'get':
                call_element = xml_.to_ele(call)
                return ET.fromstring(str(self._mgr.dispatch(call_element)))
            if handler == 'edit_config':
                self._mgr.edit_config(target=target, config=call)
            if handler == 'delete_config':
                self._mgr.delete_config(target=target)
            if handler == 'copy_config':
                self._mgr.copy_config(target=target, source=source)
        except (ncclient.transport.TransportError,
                ncclient.transport.SessionCloseError,
                ncclient.transport.SSHError,
                ncclient.transport.AuthenticationError,
                ncclient.transport.SSHUnknownHostError):
            raise DeviceCommError

    def close(self):
        """Close NETCONF session.
        Args:
            None
        Returns:
            None
        Raises:
            None
        Examples:
            >>> import pyswitch.device
            >>> conn = ('10.24.39.211', '22')
            >>> auth = ('admin', 'password')
            >>> dev = pyswitch.device.Device(conn=conn, auth=auth)
            >>> dev.connection
            True
            >>> dev.close() # doctest: +ELLIPSIS
            <?xml...<rpc-reply...<ok/>...
            >>> dev.connection
            False
        """
        return self._mgr.close_session()

    @property
    def os_type(self):
        return self._os_type

    @property
    def suports_rbridge(self):
        return self.os_type == 'nos'

    @property
    def firmware_version(self):
        """
        Returns firmware version.
        Args:
            None
        Returns:
            Dictionary
        Raises:
            None
        """

        return self._os_ver

    def _fetch_firmware_version(self):
        namespace = "urn:brocade.com:mgmt:brocade-firmware-ext"

        request_ver = '<show-firmware-version ' \
                      'xmlns="urn:brocade.com:mgmt:brocade-firmware-ext"></show-firmware-version>'

        ver = self._callback(request_ver, handler='get')

        self.os_name = ver.find('.//*{%s}os-name' % namespace).text

        if self.os_name is not None:
            if 'Network Operating System' in self.os_name:
                self._os_type = 'nos'
            elif 'SLX' in self.os_name:
                self._os_type = 'slxos'

        self._os_full_ver = ver.find('.//*{%s}firmware-full-version' % namespace).text
        self._os_ver = ver.find('.//*{%s}os-version' % namespace).text

        if self._os_type == 'slxos':
            slxos_ver = self._os_ver.split('.')

            if len(slxos_ver) >= 2:
                slxos_pattern_string = '^({0}[rs]{{1}})\.{1}\.'.format(slxos_ver[0], slxos_ver[1])
            elif len(slxos_ver) == 1:
                slxos_pattern_string = '^({0}[rs]{{1}})\.'.format(slxos_ver[0])
            else:
                slxos_pattern_string = '^(\d+[rs]{1})\.'

            slxos_pattern = re.compile(slxos_pattern_string)

            match = slxos_pattern.match(self._os_full_ver)

            if match:
                slxos_ver[0] = match.group(1)
                self._os_ver = '.'.join(slxos_ver)


if __name__ == '__main__':
    import time
    start = time.time()
    conn = ('10.26.8.212', '22')
    auth = ('admin', 'password')
    from pyswitch.device import Device
    with Device(conn=conn, auth=auth, connection_type='NETCONF') as dev:
        print dev.firmware_version
        print dev.suports_rbridge

        """
        from pyswitch.device import Device
        dev = Device(conn=conn, auth=auth)
        for vlan_id in range(2,4090):
            dev.interface.add_vlan_int(vlan_id=vlan_id)
        """
    end = time.time()
    print(end - start)
