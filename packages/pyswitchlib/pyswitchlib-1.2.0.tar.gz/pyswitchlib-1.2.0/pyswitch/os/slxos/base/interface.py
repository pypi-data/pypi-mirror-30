import pyswitch.utilities
from pyswitch.exceptions import InvalidVlanId
from pyswitch.os.base.interface import Interface as BaseInterface
from pyswitch.utilities import Util
import re
from ipaddress import ip_interface


class Interface(BaseInterface):
    """
      The Interface class holds all the actions assocaiated with the Interfaces
      of a NOS device.

      Attributes:
          None
      """

    def __init__(self, callback):
        """
        Interface init function.

        Args:
           callback: Callback function that will be called for each action.

        Returns:
           Interface Object

        Raises:
           None
        """

        super(Interface, self).__init__(callback)

    @property
    def valid_int_types(self):

        return [
            'ethernet',
            'port_channel',
            'loopback',
            've'
        ]

    @property
    def valid_intp_types(self):
        return [
            'ethernet'

        ]

    @property
    def l2_mtu_const(self):
        minimum_mtu = 1548
        maximum_mtu = 9216
        return (minimum_mtu, maximum_mtu)

    @property
    def l3_mtu_const(self):
        minimum_mtu = 1300
        maximum_mtu = 9194
        return (minimum_mtu, maximum_mtu)

    @property
    def l3_ipv6_mtu_const(self):
        minimum_mtu = 1300
        maximum_mtu = 9194
        return (minimum_mtu, maximum_mtu)

    @property
    def has_rbridge_id(self):
        return False

    def fabric_isl(self, **kwargs):
        raise ValueError('Not available on this Platform')

    def fabric_trunk(self, **kwargs):
        raise ValueError('Not available on this Platform')

    def ip_anycast_gateway(self, **kwargs):
        """
        Add anycast gateway under interface ve.

        Args:
            int_type: L3 interface type on which the anycast ip
               needs to be configured.
            name:L3 interface name on which the anycast ip
               needs to be configured.
            anycast_ip: Anycast ip which the L3 interface
               needs to be associated.
            enable (bool): If ip anycast gateway should be enabled
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `int_type`, `name`, `anycast_ip` is not passed.
            ValueError: if `int_type`, `name`, `anycast_ip` is invalid.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         dev.interface.ip_anycast_gateway(
            ...         int_type='ve', name='89',
            ...         anycast_ip='10.20.1.1/24')
            ...         output = dev.interface.ip_anycast_gateway(
            ...         get=True,int_type='ve',name='89',
            ...         anycast_ip='10.20.1.1/24')
            ...         dev.interface.ip_anycast_gateway(
            ...         enable=False,int_type='ve',
            ...         name='89',anycast_ip='10.20.1.1/24')
         """

        int_type = kwargs.pop('int_type').lower()
        name = kwargs.pop('name')
        anycast_ip = kwargs.pop('anycast_ip', '')
        enable = kwargs.pop('enable', True)
        get = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)
        valid_int_types = ['ve']

        if get and anycast_ip == '':
            enable = None
            if int_type not in valid_int_types:
                raise ValueError('`int_type` must be one of: %s' %
                                 repr(valid_int_types))
            anycast_args = dict(ve=name)

            method_name1 = 'interface_%s_ip_anycast_address_get'\
                           % int_type
            method_name2 = 'interface_%s_ipv6_anycast_address_get'\
                           % int_type
            if not pyswitch.utilities.valid_vlan_id(name):
                raise InvalidVlanId("`name` must be between `1` and `8191`")

            config1 = (method_name1, anycast_args)
            config2 = (method_name2, anycast_args)
            result = []
            op = callback(config1, handler='get_config')
            util = Util(op.data)
            result.append(util.find(util.root, './/ip-address'))
            op = callback(config2, handler='get_config')
            util = Util(op.data)
            result.append(util.find(util.root, './/ipv6-address'))

            return result

        ipaddress = ip_interface(unicode(anycast_ip))
        if int_type not in valid_int_types:
            raise ValueError('`int_type` must be one of: %s' %
                             repr(valid_int_types))
        if anycast_ip != '':
            ipaddress = ip_interface(unicode(anycast_ip))
            if ipaddress.version == 4:
                anycast_args = dict(
                    ve=name, ip_anycast_address=(str(anycast_ip),))
                method_name = 'interface_%s_ip_anycast_address'\
                              % int_type
            elif ipaddress.version == 6:
                anycast_args = dict(
                    ve=name, ipv6_anycast_address=(
                        str(anycast_ip),))
                method_name = 'interface_%s_ipv6_anycast_address'\
                              % int_type

        if not pyswitch.utilities.valid_vlan_id(name):
            raise InvalidVlanId("`name` must be between `1` and `8191`")
        create_method = "%s_create" % method_name
        config = (create_method, anycast_args)

        if not enable:
            delete_method = "%s_delete" % method_name
            config = (delete_method, anycast_args)
        return callback(config)

    def anycast_mac(self, **kwargs):
        """Configure an anycast MAC address.

        Args:
             mac (str): MAC address to configure
                 (example: '0011.2233.4455').
            delete (bool): True is the IP address is added and False if its to
                be deleted (True, False). Default value will be False if not
                specified.
            get (bool): Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
                 method.  The only parameter passed to `callback` will be the
                 ``ElementTree`` `config`.

        Returns:
            Return value of `callback`.

        Raises:
            KeyError: if `mac` is not passed.

        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.86.57']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...    conn = (switch, '22')
            ...    with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...        output = dev.interface.anycast_mac(mac='0011.2233.4455')
            ...        output = dev.interface.anycast_mac(mac='0011.2233.4455', get=True)
            ...        output = dev.interface.anycast_mac(mac='0011.2233.4455', delete=True)
        """
        callback = kwargs.pop('callback', self._callback)

        arguments = {}
        if kwargs.pop('get', False):
            method_name = 'ip_anycast_gateway_mac_get'
            config = (method_name, arguments)
            op = callback(config, handler="get_config")
            util = Util(op.data)
            return util.find(util.root, './/ip-anycast-gateway-mac')

        if kwargs.pop('delete', False):
            method_name = 'ip_anycast_gateway_mac_delete'
            config = (method_name, arguments)
        else:
            arguments = {'ip_anycast_gateway_mac': kwargs.pop('mac')}
            method_name = 'ip_anycast_gateway_mac_update'
            config = (method_name, arguments)
        return callback(config)

    def ipv6_anycast_mac(self, **kwargs):
        """Configure an anycast MAC address.

        Args:
             mac (str): MAC address to configure
                 (example: '0011.2233.4455').
            delete (bool): True is the IP address is added and False if its to
                be deleted (True, False). Default value will be False if not
                specified.
            get (bool): Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
                 method.  The only parameter passed to `callback` will be the
                 ``ElementTree`` `config`.

        Returns:
            Return value of `callback`.

        Raises:
            KeyError: if `mac` is not passed.

        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.86.57']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...    conn = (switch, '22')
            ...    with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...        output = dev.interface.ipv6_anycast_mac(mac='0011.2233.4455')
            ...        output = dev.interface.ipv6_anycast_mac(mac='0011.2233.4455', get=True)
            ...        output = dev.interface.ipv6_anycast_mac(mac='0011.2233.4455', delete=True)
        """
        callback = kwargs.pop('callback', self._callback)

        arguments = {}
        if kwargs.pop('get', False):
            method_name = 'ipv6_anycast_gateway_mac_get'
            config = (method_name, arguments)
            op = callback(config, handler="get_config")
            util = Util(op.data)
            return util.find(util.root, './/ip-anycast-gateway-mac')

        if kwargs.pop('delete', False):
            method_name = 'ipv6_anycast_gateway_mac_delete'
            config = (method_name, arguments)
        else:
            arguments = {'ipv6_anycast_gateway_mac': kwargs.pop('mac')}
            method_name = 'ipv6_anycast_gateway_mac_update'
            config = (method_name, arguments)
        return callback(config)

    def spanning_tree_state(self, **kwargs):
        """Set Spanning Tree state.

        Args:
            int_type (str): Type of interface. (gigabitethernet,
                tengigabitethernet, vlan, port_channel etc).
            name (str): Name of interface or VLAN id.
                (For interface: 1/0/5, 1/0/10 etc).
                (For VLANs 0, 1, 100 etc).
                (For Port Channels 1, 100 etc).
            enabled (bool): Is Spanning Tree enabled? (True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.

        Returns:
            Return value of `callback`.

        Raises:
            KeyError: if `int_type`, `name`, or `enabled` is not passed.
            ValueError: if `int_type`, `name`, or `enabled` are invalid.

        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         enabled = True
            ...         int_type = 'tengigabitethernet'
            ...         name = '225/0/37'
            ...         output = dev.interface.enable_switchport(int_type,
            ...         name)
            ...         output = dev.interface.spanning_tree_state(
            ...         int_type=int_type, name=name, enabled=enabled)
            ...         enabled = False
            ...         output = dev.interface.spanning_tree_state(
            ...         int_type=int_type, name=name, enabled=enabled)
            ...         int_type = 'vlan'
            ...         name = '102'
            ...         enabled = False
            ...         output = dev.interface.add_vlan_int(name)
            ...         output = dev.interface.enable_switchport(
            ...             int_type, name)
            ...         output = dev.interface.spanning_tree_state(
            ...         int_type=int_type, name=name, enabled=enabled)
            ...         enabled = False
            ...         output = dev.interface.spanning_tree_state(
            ...         int_type=int_type, name=name, enabled=enabled)
            ...         output = dev.interface.del_vlan_int(name)
            ...         int_type = 'port_channel'
            ...         name = '2'
            ...         enabled = False
            ...         output = dev.interface.channel_group(name='225/0/20',
            ...                              int_type='tengigabitethernet',
            ...                              port_int=name,
            ...                              channel_type='standard',
            ...                              mode='active')
            ...         output = dev.interface.enable_switchport(
            ...             int_type, name)
            ...         output = dev.interface.spanning_tree_state(
            ...         int_type=int_type, name=name, enabled=enabled)
            ...         enabled = False
            ...         output = dev.interface.spanning_tree_state(
            ...         int_type=int_type, name=name, enabled=enabled)
            ...         output = dev.interface.remove_port_channel(
            ...             port_int=name)
        """
        int_type = kwargs.pop('int_type').lower()
        name = kwargs.pop('name')
        get = kwargs.pop('get', False)

        callback = kwargs.pop('callback', self._callback)
        valid_int_types = self.valid_int_types

        if int_type not in valid_int_types:
            raise ValueError('int_type must be one of: %s' %
                             repr(valid_int_types))
        state_args = dict()
        state_args[int_type] = name
        if get:
            method_name = 'interface_%s_spanning_tree_get' % int_type
            if int_type == 'vlan':
                method_name = 'vlan_spanning_tree_get'
            config = (method_name, state_args)
            x = callback(config, handler='get_config')
            util = Util(x.data)
            shutdown_status = util.find(util.root, './/shutdown')
            if shutdown_status and shutdown_status == 'false':
                return True
            return False

        enabled = kwargs.pop('enabled')
        if not isinstance(enabled, bool):
            raise ValueError('%s must be `True` or `False`.' % repr(enabled))

        if int_type == 'vlan':
            if not pyswitch.utilities.valid_vlan_id(name):
                raise InvalidVlanId(
                    '%s must be between 0 to 8191.' % int_type)
            shutdown_name = 'stp_shutdown'
            method_name = 'interface_%s_spanning_tree_update' % int_type

        else:
            if not pyswitch.utilities.valid_interface(int_type, name):
                raise ValueError('`name` must be in the format of x/y/z for '
                                 'physical interfaces or x for port channel.')
            shutdown_name = 'shutdown'
            method_name = 'interface_%s_spanning_tree_update' % int_type

        if enabled:
            state_args[shutdown_name] = False
        else:
            state_args[shutdown_name] = True
        try:
            config = (method_name, state_args)
            return callback(config)
        # TODO: Catch existing 'no shut'
        # This is in place because if the interface spanning tree is already
        # up,`ncclient` will raise an error if you try to admin up the
        # interface again.
        # TODO: add logic to shutdown STP at protocol level too.
        except AttributeError:
            return None

    def vlan_router_ve(self, **kwargs):
        """Configure/get/delete router interface ve on a vlan.

        Args:
            vlan_id (str): Vlan number.
            ve_config (str) : router ve interface
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the router ve on the vlan.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.

        Returns:
            Return value of `callback`.

        Raises:
            KeyError: if `vlan_id`  is not specified.
            ValueError: if `vlan_id` is not a valid value.

        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.vlan_router_ve(
            ...         get=True, vlan_id='100')
            ...         output = dev.interface.vlan_router_ve(
            ...         delete=True, vlan_id='100')
            ...         output = dev.interface.vlan_router_ve(
            ...         vlan_id='100', ve_config='200')
            Traceback (most recent call last):
            KeyError
        """
        vlan = kwargs.pop('vlan_id')
        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if not pyswitch.utilities.valid_vlan_id(vlan):
            raise InvalidVlanId(
                '%s must be between 0 to 8191.' % vlan)
        if delete:
            ve_args = dict(vlan=vlan)
            config = (self.method_prefix('vlan_router_interface_ve_delete'),
                      ve_args)
            return callback(config)

        if not get_config:
            ve_config = kwargs.pop('ve_config')
            ve_args = dict(vlan=vlan, ve_config=ve_config)
            config = (self.method_prefix('vlan_router_interface_ve_update'),
                      ve_args)
            result = callback(config)
        elif get_config:
            ve_args = dict(vlan=vlan)
            config = (self.method_prefix('vlan_router_interface_ve_get'),
                      ve_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            result = util.find(util.root, './/Ve')
        return result

    def is_ve_id_required(self):
        """ Check if VE id is required for creating VE or vlan id is sufficient
        """
        # TBD change this to True once workflow impact is considered by making VE as
        # mandatory
        return False

    def is_vlan_rtr_ve_config_req(self):
        """ Check if router interface config is required for VLAN
        """
        return True

    def bridge_domain(self, **kwargs):
        """Configure/get/delete bridge-domain.

        Args:
            bridge_domain (str): bridge domain number.
            bridge_domain_service_type (str): service type. ('p2mp', 'p2p')
            vc_id_num (str): VC Id under the VPLS Instance
            statistics (bool): Configure Statistics. (True, False)
            pw_profile_name (str): Pw-profile name (Max Size - 64).
            bpdu_drop_enable (bool): Drop BPDU packets. (True, False)
            local_switching (bool): Configure local switching. (True, False)
            firmware_version(str): OS version number.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the bd.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.

        Returns:
            Return value of `callback`.

        Raises:
            KeyError: if `bridge_domain`  is not specified.
            KeyError: if `vc_id_num` is not speciied.

        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.bridge_domain(
            ...         get=True, bridge_domain='100')
            ...         output = dev.interface.bridge_domain(
            ...         delete=True, bridge_domain='100')
            ...         output = dev.interface.bridge_domain(
            ...         bridge_domain='100', vc_id_num='200')
            Traceback (most recent call last):
            KeyError
        """
        bridge_domain = kwargs.pop('bridge_domain')
        bridge_domain_service = kwargs.pop('bridge_domain_service_type', 'p2mp')
        statistics = kwargs.pop('statistics', None)
        pw_profile_name = kwargs.pop('pw_profile_name', None)
        bpdu_drop_enable = kwargs.pop('bpdu_drop_enable', None)
        local_switching = kwargs.pop('local_switching', None)

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if bridge_domain_service not in ['p2mp', 'p2p']:
            raise ValueError("`bridge_domain_service_type` must match one of them "
                             "`p2mp, p2p`")

        bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service))
        if delete:
            config = (self.method_prefix('bridge_domain_delete'), bd_args)
            return callback(config)

        if not get_config:
            vc_id_num = kwargs.pop('vc_id_num')
            firmware = kwargs.pop('firmware_version', None)
            re_pat1 = '\d+r'
            if firmware is None or re.match(re_pat1, firmware):
                bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service),
                               vc_id_num=vc_id_num, statistics=statistics,
                               pw_profile_name=pw_profile_name,
                               bpdu_drop_enable=bpdu_drop_enable,
                               local_switching=local_switching)
            else:
                bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service))

            config = (self.method_prefix('bridge_domain_create'), bd_args)
            result = callback(config)
        elif get_config:
            config = (self.method_prefix('bridge_domain_get'), bd_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            bridge_domain_id = util.find(util.root, './/bridge-domain-id')
            if bridge_domain_id is not None:
                bridge_domain_type = util.find(util.root, './/bridge-domain-type')
                vc_id = util.find(util.root, './/vc-id')
                pw_profile = util.find(util.root, './/pw-profile')
                statistics = util.find(util.root, './/statistics')
                bpdu_drop_enable = util.find(util.root, './/bpdu-drop-enable')
                local_switching = util.find(util.root, './/local-switching')
                result = {'bridge_domain_id': bridge_domain_id,
                          'bridge_domain_type': bridge_domain_type,
                          'vc_id': vc_id, 'pw_profile': pw_profile,
                          'statistics': statistics,
                          'bpdu_drop_enable': bpdu_drop_enable,
                          'local_switching': local_switching}
            else:
                result = None
        return result

    def bridge_domain_peer(self, **kwargs):
        """Configure/get/delete PW Peer related configuration.

        Args:
            bridge_domain (str): bridge domain number.
            bridge_domain_service_type (str): service type. ('p2mp', 'p2p')
            peer_ip (str): PW Peer Ip for remote peer
            load_balance (bool): load-balance. (True, False)
            cos (str): cos value. <cos value: 0..7>
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete peer_ips on bd.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.

        Returns:
            Return value of `callback`.

        Raises:
            KeyError: if `bridge_domain`  is not specified.
            KeyError: if `peer_ip` is not speciied.

        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.bridge_domain_peer(
            ...         get=True, bridge_domain='100', peer_ip='1.1.1.1')
            ...         output = dev.interface.bridge_domain_peer(
            ...         delete=True, bridge_domain='100', peer_ip='1.1.1.1')
            ...         output = dev.interface.bridge_domain_peer(
            ...         bridge_domain='100', peer_ip='1.1.1.1', cos='1',
            ...         load_balance=True)
            Traceback (most recent call last):
            KeyError
        """

        bridge_domain = kwargs.pop('bridge_domain')
        bridge_domain_service = kwargs.pop('bridge_domain_service_type', 'p2mp')
        load_balance = kwargs.pop('load_balance', None)
        cos = kwargs.pop('cos', None)
        peer_ip = str(kwargs.pop('peer_ip'))

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if bridge_domain_service not in ['p2mp', 'p2p']:
            raise ValueError("`bridge_domain_service_type` must match one of them "
                             "`p2mp, p2p`")
        if cos is not None and cos not in range(0, 8):
            raise ValueError("`cos' value should be in-between `0-7`")

        bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service),
                       peer=(peer_ip, load_balance, cos))
        if delete:
            config = (self.method_prefix('bridge_domain_peer_delete'),
                      bd_args)
            return callback(config)

        if not get_config:
            config = (self.method_prefix('bridge_domain_peer_create'),
                      bd_args)
            result = callback(config)
        elif get_config:
            config = (self.method_prefix('bridge_domain_peer_get'),
                      bd_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            peer_ip = util.find(util.root, './/peer-ip')
            if peer_ip is not None:
                load_balance = util.find(util.root, './/load_balance')
                cos = util.find(util.root, './/cos')
                lsp = util.find(util.root, './/lsp')
                result = {'peer_ip': peer_ip, 'load_balance': load_balance,
                          'cos': cos, 'lsp': lsp}
            else:
                result = None
        return result

    def bridge_domain_logical_interface(self, **kwargs):
        """Configure/get/delete logical-interface on a bridge-domain.
        Args:
            bridge_domain (str): bridge domain number.
            bridge_domain_service_type (str): service type. ('p2mp', 'p2p')
            intf_type (str): Type of interface. ['ethernet', 'port_channel']
            lif_name  (str): Logical Interface name.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete single/all LIFs on a bd.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `bridge_domain` or `lif_name` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.bridge_domain_logical_interface(
            ...         get=True, bridge_domain='100', lif_name='1/34.1')
            ...         output = dev.interface.bridge_domain_logical_interface(
            ...         delete=True, bridge_domain='100', lif_name='1/34.1')
            ...         output = dev.interface.bridge_domain_logical_interface(
            ...         bridge_domain='100', lif_name='1/34.1')
            Traceback (most recent call last):
            KeyError
        """

        bridge_domain = kwargs.pop('bridge_domain')
        bridge_domain_service = kwargs.pop('bridge_domain_service_type', 'p2mp')
        intf_type = kwargs.pop('intf_type', 'ethernet')
        lif_name = kwargs.pop('lif_name', None)

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if bridge_domain_service not in ['p2mp', 'p2p']:
            raise ValueError("`bridge_domain_service_type` must "
                             "match one of them "
                             "`p2mp, p2p`")
        if intf_type not in ['ethernet', 'port_channel']:
            raise ValueError("`intf_ype` must match one of them "
                             "`ethernet, port_channel`")
        if intf_type == 'port_channel':
            bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service))
        else:
            bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service))

        if lif_name is not None and intf_type == 'port_channel':
            bd_args.update(port_channel=lif_name)
        elif lif_name is not None and intf_type == 'ethernet':
            bd_args.update(ethernet=lif_name)

        if delete:
            method_name = 'bridge_domain_logical_interface_%s_delete' % \
                          intf_type
            config = (method_name, bd_args)
            return callback(config)
        if not get_config:
            method_name = 'bridge_domain_logical_interface_%s_create' % \
                          intf_type
            config = (method_name, bd_args)
            result = callback(config)
        elif get_config:
            method_name = 'bridge_domain_logical_interface_%s_get' % \
                          intf_type
            config = (method_name, bd_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            if intf_type == 'port_channel':
                result = util.find(util.root, './/pc-lif-bind-id')
            else:
                result = util.find(util.root, './/lif-bind-id')
        return result

    def logical_interface_create(self, **kwargs):
        """Configure/get/delete logical interface on an ethernet/port-channel.
        Args:
            intf_type (str): Type of interface. ['ethernet', 'port_channel']
            intf_name (str): Intername name.
            lif_name  (str): Logical Interface name.
            firmware_version(str): OS version number.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete single/all lifs on intf.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `intf_name`  is not specified.
            KeyError: if `lif_name` is not speciied.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.logical_interface_create(
            ...         get=True, intf_name='0/34')
            ...         output = dev.interface.logical_interface_create(
            ...         delete=True, intf_name='0/34')
            ...         output = dev.interface.logical_interface_create(
            ...         intf_name='0/34', lif_name='0/34.1')
            ...         output = dev.interface.logical_interface_create(
            ...         intf_name='111', lif_name='111.1',
            ...         intf_type='port_channel')
            ...         output = dev.interface.logical_interface_create(
            ...         delete=True, intf_name='0/34', lif_name='0/34.1')
            Traceback (most recent call last):
            KeyError
        """
        intf_type = kwargs.pop('intf_type', 'ethernet')
        intf_name = kwargs.pop('intf_name', None)
        lif_name = kwargs.pop('lif_name', None)
        firmware = kwargs.pop('firmware_version', None)

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if intf_type not in ['ethernet', 'port_channel']:
            raise ValueError("`intf_ype` must match one of them "
                             "`ethernet, port_channel`")

        if intf_type == 'port_channel':
            lg_args = dict(port_channel=intf_name)
        else:
            lg_args = dict(ethernet=intf_name)

        if delete:
            if lif_name is not None and intf_type == 'port_channel':
                lg_args.update(port_channel_=lif_name)
            elif lif_name is not None and intf_type == 'ethernet':
                lg_args.update(ethernet_=lif_name)
            method_name = 'interface_%s_logical_interface_%s_delete' % \
                          (intf_type, intf_type)
            config = (method_name, lg_args)
            return callback(config)
        if not get_config:
            if intf_type == 'port_channel':
                lg_args = dict(port_channel=intf_name, port_channel_=lif_name)
            else:
                lg_args = dict(ethernet=intf_name, ethernet_=lif_name)
            method_name = 'interface_%s_logical_interface_%s_create' % \
                          (intf_type, intf_type)
            config = (method_name, lg_args)
            result = callback(config)
        elif get_config:
            result = []
            re_pat1 = '\d+s'
            inner_vlan = []
            lg_args.update(resource_depth=3)
            method_name = 'interface_%s_logical_interface_%s_get' % \
                          (intf_type, intf_type)
            config = (method_name, lg_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            for each in util.findlist(util.root, './/port-channel'):
                int_name = util.find(each, './/pc-instance-id')
                outer_vlan = util.find(each, './/outer-tagged-vlan-id')
                if not re.match(re_pat1, firmware):
                    inner_vlan = util.find(each, './/inner-vlan')
                else:
                    inner_vlan = None
                if not re.match(re_pat1, firmware):
                    untag = util.find(each, './/untagged-vlan-id')
                else:
                    untag = util.find(each, './/untagged-flag')
                item_results = {'intf_name': int_name,
                                'outer_vlan': outer_vlan,
                                'inner_vlan': inner_vlan,
                                'untag': untag}
                result.append(item_results)
        return result

    def logical_interface_tag_vlan(self, **kwargs):
        """Configure/get/delete outer-vlan,inner-vlan on a LIF
        Args:
            intf_type (str): Type of interface. ['ethernet', 'port_channel']
            intf_name (str): Intername name.
            lif_name  (str): Logical Interface name.
            outer_tag_vlan_id (str): Outer vlan ID
            inner_vlan (bool): Enable inner vlan.(True, False)
            inner_tag_vlan_id (str): Inner vlan ID
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the tag vlan.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `lif_name`, `intf_name` `outer_tag_vlan_id`
                      is not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.logical_interface_tag_vlan(
            ...         get=True, intf_name='1/34', lif_name='1/34.1')
            ...         output = dev.interface.logical_interface_tag_vlan(
            ...         delete=True, intf_name='1/34', lif_name='1/34.1')
            ...         output = dev.interface.logical_interface_tag_vlan(
            ...         intf_name='111', lif_name='111.1', inner_vlan=True,
            ...         outer_tag_vlan_id='100', inner_tag_vlan_id='200')
            Traceback (most recent call last):
            KeyError
        """
        intf_type = kwargs.pop('intf_type', 'ethernet')
        intf_name = kwargs.pop('intf_name', None)
        lif_name = kwargs.pop('lif_name', None)

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if intf_type not in ['ethernet', 'port_channel']:
            raise ValueError("`intf_ype` must match one of them "
                             "`ethernet, port_channel`")

        if intf_type == 'port_channel':
            lg_args = dict(port_channel=intf_name, port_channel_=lif_name)
        else:
            lg_args = dict(ethernet=intf_name, ethernet_=lif_name)

        if delete:
            method_name = 'interface_%s_logical_interface_%s_vlan_delete' % \
                          (intf_type, intf_type)
            config = (method_name, lg_args)
            return callback(config)
        if not get_config:
            outer_tagged_vlan_id = kwargs.pop('outer_tag_vlan_id')
            if not pyswitch.utilities.valid_vlan_id(outer_tagged_vlan_id):
                raise InvalidVlanId("Invalid outer Vlan value.")
            inner_vlan = kwargs.pop('inner_vlan', None)
            if intf_type == 'port_channel':
                lg_args = dict(port_channel=intf_name, port_channel_=lif_name,
                               outer_tagged_vlan_id=outer_tagged_vlan_id)
            else:
                lg_args = dict(ethernet=intf_name, ethernet_=lif_name,
                               outer_tagged_vlan_id=outer_tagged_vlan_id)
            if inner_vlan:
                inner_tagged_vlan_id = kwargs.pop('inner_tag_vlan_id')
                if not pyswitch.utilities.valid_vlan_id(inner_tagged_vlan_id):
                    raise InvalidVlanId("Invalid inner Vlan value.")
                lg_args['inner_vlan'] = inner_vlan
                lg_args['inner_tagged_vlan_id'] = inner_tagged_vlan_id
            method_name = 'interface_%s_logical_interface_%s_vlan_update' % \
                          (intf_type, intf_type)
            config = (method_name, lg_args)
            result = callback(config)
        elif get_config:
            method_name = 'interface_%s_logical_interface_%s_vlan_get' % \
                          (intf_type, intf_type)
            config = (method_name, lg_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            outer_vlan = util.find(util.root, './/outer-tagged-vlan-id')
            inner_vlan = util.find(util.root, './/inner-tagged-vlan-id')
            result = dict(outer_vlan=outer_vlan, inner_vlan=inner_vlan)
        return result

    def logical_interface_untag_vlan(self, **kwargs):
        """Configure/get/delete untag-vlan on a LIF
        Args:
            intf_type (str): Type of interface. ['ethernet', 'port_channel']
            intf_name (str): Intername name.
            lif_name  (str): Logical Interface name.
            untag_vlan_id (str): Outer vlan ID
            firmware_version(str): OS version number.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the untag vlan on lif.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `intf_name` is not specified.
            KeyError: if `lif_name` or `untag_vlan_id` is not speciied.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.logical_interface_untag_vlan(
            ...         get=True, intf_name='1/34', lif_name='1/34.1')
            ...         output = dev.interface.logical_interface_untag_vlan(
            ...         delete=True, intf_name='1/34', lif_name='1/34.1')
            ...         output = dev.interface.logical_interface_untag_vlan(
            ...         intf_name='111', lif_name='111.1',
            ...         untag_vlan_id='100')
            Traceback (most recent call last):
            KeyError
        """
        intf_type = kwargs.pop('intf_type', 'ethernet')
        intf_name = kwargs.pop('intf_name', None)
        lif_name = kwargs.pop('lif_name', None)
        firmware = kwargs.pop('firmware_version', None)
        untagged_vlan_id = kwargs.pop('untag_vlan_id', None)
        untagged_flag = kwargs.pop('untagged_flag', True)

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if intf_type not in ['ethernet', 'port_channel']:
            raise ValueError("`intf_ype` must match one of them "
                             "`ethernet, port_channel`")

        if untagged_vlan_id is not None and\
                not pyswitch.utilities.valid_vlan_id(untagged_vlan_id):
            raise InvalidVlanId("Invalid untagged Vlan value.")
        re_pat1 = '\d+r'
        if intf_type == 'port_channel':
            lg_args = dict(port_channel=intf_name, port_channel_=lif_name)
        else:
            lg_args = dict(ethernet=intf_name, ethernet_=lif_name)

        if delete:
            if not re.match(re_pat1, firmware):
                method_name = 'interface_%s_logical_interface_%s_'\
                              'untagged_vlan_delete' % (intf_type, intf_type)
            else:
                method_name = 'interface_%s_logical_interface_%s_'\
                              'untagged_vlan_untagged_vlan_id_delete'\
                              % (intf_type, intf_type)
            config = (method_name, lg_args)
            return callback(config)
        if not get_config:
            lg_args.update(untagged_vlan_id=untagged_vlan_id)
            if not re.match(re_pat1, firmware):
                lg_args.update(untagged_flag=untagged_flag)
                method_name = 'interface_%s_logical_interface_%s_'\
                              'untagged_update' % (intf_type, intf_type)
            else:
                method_name = 'interface_%s_logical_interface_%s_'\
                              'untagged_vlan_untagged_vlan_id_update'\
                              % (intf_type, intf_type)
            config = (method_name, lg_args)
            result = callback(config)
        elif get_config:
            if not re.match(re_pat1, firmware):
                method_name = 'interface_%s_logical_interface_%s_'\
                              'untagged_vlan_get' % (intf_type, intf_type)
            else:
                method_name = 'interface_%s_logical_interface_%s_'\
                              'untagged_vlan_untagged_vlan_id_get'\
                              % (intf_type, intf_type)
            config = (method_name, lg_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            result = util.find(util.root, './/untagged-vlan-id')
        return result

    def ip_ospf(self, **kwargs):
        """Configure/get ospf on an interface
        Args:
            intf_type (str): Type of interface.
            intf_name (str): Intername name.
            area (str): OSPF areas.
            auth_change_wait_time (str): Authentication Change Wait time
                                         (MD5 and non MD5).
            hello_interval (str): Time between HELLO packets.
            dead_interval (str): Interval after which a neighbor
                                 is declared dead.
            retransmit_interval (str): Time between retransmitting lost
                                       link state advertisements.
            transmit_delay (str): Link state transmit delay.
            cost (str): Interface cost.
            network (str): Interface type.
                           ['broadcast', 'non-broadcast', 'point-to-point']
            intf_ldp_sync (str): Set LDP-SYNC operation mode on this interface.
                                 [enable, disable]
            mtu_ignore (bool): To disable OSPF MTU mismatch detection.
            active (bool):  Active information.
            passive (bool): Passive information.
            priority (str): Router priority.
            get (bool): Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `intf_name`, `area` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.ip_ospf(intf_type='loopback',
            ...         get=True, intf_name='11')
            ...         output = dev.interface.ip_ospf(intf_type='loopback',
            ...         area='0', intf_name='11')
            Traceback (most recent call last):
            KeyError
        """
        intf_type = kwargs.pop('intf_type', 'ethernet')
        intf_name = kwargs.pop('intf_name')
        auth_change_wait_time = kwargs.pop('auth_change_wait_time', None)
        hello_interval = kwargs.pop('hello_interval', None)
        dead_interval = kwargs.pop('dead_interval', None)
        retransmit_interval = kwargs.pop('retransmit_interval', None)
        transmit_delay = kwargs.pop('transmit_delay', None)
        cost = kwargs.pop('cost', None)
        network = kwargs.pop('network', None)
        intf_ldp_sync = kwargs.pop('intf_ldp_sync', None)
        mtu_ignore = kwargs.pop('mtu_ignore', None)
        active = kwargs.pop('active', None)
        passive = kwargs.pop('passive', None)
        priority = kwargs.pop('priority', None)
        valid_int_types = self.valid_int_types

        if intf_type not in self.valid_int_types:
            raise ValueError('intf_type must be one of: %s' %
                             repr(valid_int_types))
        ospf_args = {}
        get_config = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)

        ospf_args[intf_type] = intf_name
        if not get_config:
            area = kwargs.pop('area')
            ospf_args.update(area=area,
                             auth_change_wait_time=auth_change_wait_time,
                             hello_interval=hello_interval,
                             dead_interval=dead_interval,
                             retransmit_interval=retransmit_interval,
                             transmit_delay=transmit_delay, cost=cost,
                             network=network, intf_ldp_sync=intf_ldp_sync,
                             mtu_ignore=mtu_ignore, active=active,
                             passive=passive, priority=priority)
            method_name = 'interface_%s_ip_ospf_update' % intf_type
            config = (method_name, ospf_args)
            return callback(config)
        elif get_config:
            method_name = 'interface_%s_ip_ospf_get' % intf_type
            config = (method_name, ospf_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            ospf = util.find(util.root, './/area')
            if ospf is not None:
                active = util.find(util.root, './/active')
                passive = util.find(util.root, './/passive')
                mtu_ignore = util.find(util.root, './/mtu-ignore')
                result = {'area': ospf, 'active': active,
                          'passive': passive, 'mtu_ignore': mtu_ignore}
            else:
                result = None
        return result

    def ip_router_isis(self, **kwargs):
        """Configure/get/delete ISIS on an interface

        Args:
            intf_type (str): Type of interface.
            intf_name (str): Intername name.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the router isis on intf.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `intf_name` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.ip_router_isis(
            ...         intf_type='loopback', get=True, intf_name='11')
            ...         output = dev.interface.ip_router_isis(
            ...         intf_type='loopback', delete=True, intf_name='11')
            ...         output = dev.interface.ip_router_isis(
            ...         intf_type='loopback', intf_name='11')
            Traceback (most recent call last):
            KeyError
        """
        intf_type = kwargs.pop('intf_type', 'ethernet')
        intf_name = kwargs.pop('intf_name')

        if intf_type not in self.valid_int_types:
            raise ValueError('intf_type must be one of: %s' %
                             repr(self.valid_int_types))
        isis_args = {}
        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        isis_args[intf_type] = intf_name
        if delete:
            method_name = 'interface_%s_ip_router_isis_delete' % intf_type
            config = (method_name, isis_args)
            return callback(config)
        if not get_config:
            isis_args['interface_ip_router_isis'] = True
            method_name = 'interface_%s_ip_router_isis_update' % intf_type
            config = (method_name, isis_args)
            return callback(config)
        elif get_config:
            method_name = 'interface_%s_ip_router_isis_get' % intf_type
            config = (method_name, isis_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            result = util.find(util.root, './/isis')
        return result

    def interface_storm_control_ingress_create(self, **kwargs):
        """Config/get/delete BUM Control

        Args:
            intf_type (str): Interface Type.('ethernet',
                             gigabitethernet, tengigabitethernet etc).
            intf_name (str): Interface Name
            traffic_type (str): traffic_type.
                             ['broadcast', 'unknown-unicast', 'multicast']
            rate_format (str): rate format type.
                             ['limit-bps', 'limit-percent']
            rate_bps (int): Rate limit value in bps.
                            Valid Range <0-100000000000 bps>.
            rate_percent (int): Rate limit value in percent for line rate.
                               Valid Range <0-100>.
            bum_action (str): Bum Action. Valid Values ['monitor', 'shutdown']
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the service policy on the interface.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `intf_name`, `traffic_type_policy`, `rate_format`,
                      is not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output_all = dev.interface.interface_storm_control_
            ...         ingress_create(get=True, intf_name='1/45')
            ...         output_all = dev.interface.interface_storm_control_
            ...         ingress_create(delete=True, intf_name='1/45',
            ...         traffic_type='broadcast')
            ...         output_all = dev.interface.interface_storm_control_
            ...         ingress_create(delete=True, intf_name='1/45',
            ...         traffic_type='broadcast', rate_format='limit-bps',
            ...         rate_bps=10000000, bum_action='shutdown')
        """

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        intf_type = kwargs.pop('intf_type', 'ethernet')
        intf_name = kwargs.pop('intf_name')
        protocol_type = kwargs.pop('traffic_type', None)
        rate_format = kwargs.pop('rate_format', None)
        rate_bps = kwargs.pop('rate_bps', None)
        rate_percent = kwargs.pop('rate_percent', None)
        bum_action = kwargs.pop('bum_action', 'shutdown')

        valid_int_types = self.valid_int_types
        if intf_type not in valid_int_types:
            raise ValueError('intf_type must be one of: %s' %
                             repr(valid_int_types))

        if intf_type == 'ethernet':
            map_args = dict(ethernet=intf_name)
        elif intf_type == 'gigabitethernet':
            map_args = dict(gigabitethernet=intf_name)
        elif intf_type == 'tengigabitethernet':
            map_args = dict(tengigabitethernet=intf_name)
        else:
            map_args = dict(fortygigabitethernet=intf_name)

        if protocol_type is not None and protocol_type not in \
                ['broadcast', 'unknown-unicast', 'multicast']:
            raise KeyError('`traffic_type` must be one of them '
                           '[broadcast, unknown-unicast, multicast]')
        if bum_action not in ['monitor', 'shutdown']:
            raise KeyError('`bum_action` must be one of them '
                           '[monitor, shutdown]')
        if rate_format is not None and rate_format not in \
                ['limit-bps', 'limit-percent']:
            raise KeyError('`rate_format` must be one of them '
                           '[limit-bps, limit-percent]')
        if rate_bps is not None and not 0 <= rate_bps < 100000000001:
            raise ValueError("`rate_bps` must be in range <0-100000000000>",
                             rate_bps)
        if rate_percent is not None and not 0 <= rate_percent < 101:
            raise ValueError("`rate_percent` must be in range <0-100>",
                             rate_percent)

        if delete:
            map_args.update(ingress=(protocol_type, rate_format, rate_bps,
                                     rate_percent, bum_action))
            method_name = 'interface_%s_storm_control_ingress_delete' \
                          % intf_type
            config = (method_name, map_args)
            return callback(config)

        if not get_config:
            if rate_bps is None and rate_percent is None:
                raise KeyError('Pass either `rate_bps` or `rate_percent`')
            map_args.update(ingress=(protocol_type, rate_format, rate_bps,
                                     rate_percent, bum_action), rate_format=rate_format,
                            rate_bps=rate_bps, bum_action=bum_action,
                            rate_percent=rate_percent)
            method_name = 'interface_%s_storm_control_ingress_create' \
                          % intf_type
            config = (method_name, map_args)
            return callback(config)
        elif get_config:
            method_name = 'interface_%s_storm_control_ingress_get' \
                          % intf_type
            config = (method_name, map_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            if output.data != '<output></output>':
                result = util.findall(util.root, './/protocol-type')
            else:
                result = None
        return result

    def create_evpn_instance(self, **kwargs):
        """
        Add evpn instance.

        Args:
            evpn_instance_name: Instance name for evpn
            enable (bool): If evpn instance needs to be configured
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
            rbridge_id (str): rbridge-id for device. Only required when type is
                `ve`.
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if 'evpn_instance_name' is not passed.
            ValueError: if 'evpn_instance_name' is invalid.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.26.8.210']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.create_evpn_instance(
            ...         evpn_instance_name='sj_fabric')
            ...         output = dev.interface.create_evpn_instance(
            ...         get=True,
            ...         evpn_instance_name='sj_fabric')
            ...         print output
            ...         output = dev.interface.create_evpn_instance(
            ...         enable=False,
            ...         evpn_instance_name='sj_fabric')
            ...         output = dev.interface.create_evpn_instance(
            ...         get=True)
            ...         print output
            ...         # doctest: +IGNORE_EXCEPTION_DETAIL
            {'instance_name': 'sj_fabric', 'ignore_as': None, 'duplicate_mac_timer_value': None,
            'rd_auto': None, 'max_count': None}
            {'instance_name': None, 'ignore_as': None, 'duplicate_mac_timer_value': None,
            'rd_auto': None, 'max_count': None}
         """

        evpn_instance_name = kwargs.pop('evpn_instance_name', '')
        enable = kwargs.pop('enable', True)
        get = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)
        evpn_args = dict()

        if evpn_instance_name != '':
            evpn_args['evpn_instance'] = evpn_instance_name

        if get:
            enable = None

        method_name = 'evpn_evpn_instance_create'
        config = (method_name, evpn_args)

        if get:
            method_name = 'evpn_evpn_instance_get'
            evpn_args['resource_depth'] = 2
            config = (method_name, evpn_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            instance_name = util.find(util.root, './/instance-name')
            ignore_as = util.find(util.root, './/ignore-as')
            duplicate_mac_timer_value = util.find(
                util.root, './/duplicate-mac-timer-value')
            max_count = util.find(util.root, './/max-count')
            auto = util.find(util.root, './/rd..auto')
            return {'instance_name': instance_name, 'ignore_as': ignore_as,
                    'duplicate_mac_timer_value': duplicate_mac_timer_value,
                    'max_count': max_count, 'rd_auto': auto}
        if not enable:
            method_name = 'evpn_evpn_instance_delete'
            config = (method_name, evpn_args)
        return callback(config)

    def evpn_instance_rd_auto(self, **kwargs):
        """
        Add RD auto under EVPN instance.

        Args:
            rbridge_id: Rbrdige id .
            instance_name: EVPN instance name.

        Returns:
            True if command completes successfully or False if not.

        Raises:
            None
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.26.8.210']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.create_evpn_instance(
            ...         evpn_instance_name='sj_fabric')
            ...         output=dev.interface.evpn_instance_rd_auto(
            ...         evpn_instance_name='sj_fabric')

         """
        evpn_instance_name = kwargs.pop('evpn_instance_name', '')
        # enable = kwargs.pop('enable', True)
        # get = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)

        evpn_args = dict()

        method_name = 'evpn_evpn_instance_rd_auto_update'
        evpn_args['evpn_instance'] = evpn_instance_name
        evpn_args['auto'] = True
        config = (method_name, evpn_args)

        return callback(config)

    def evpn_instance_rt_both_ignore_as(self, **kwargs):
        """
        Add evpn instance route target ignore AS.

        Args:
            evpn_instance_name: Instance name for evpn
            enable (bool): If target community needs to be enabled
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
            rbridge_id (str): rbridge-id for device. Only required when type is
                `ve`.
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if 'evpn_instance_name' is not passed.
            ValueError: if 'evpn_instance_name' is invalid.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.26.8.210']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output=dev.interface.evpn_instance_rt_both_ignore_as(
            ...         evpn_instance_name='sj_fabric')
            ...         output=dev.interface.evpn_instance_rt_both_ignore_as(
            ...         get=True,
            ...         evpn_instance_name='sj_fabric')
            ...         print output
            ...         output=dev.interface.evpn_instance_rt_both_ignore_as(
            ...         enable=False,
            ...         evpn_instance_name='sj_fabric')
            ...         output=dev.interface.evpn_instance_rt_both_ignore_as(
            ...         get=True)
            ...         print output
            true
            None
         """

        evpn_instance_name = kwargs.pop('evpn_instance_name', '')
        enable = kwargs.pop('enable', True)
        get = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)
        evpn_args = dict()
        if get:
            enable = None

        if get:
            evpn_args['resource_depth'] = 3
            method_name = 'evpn_evpn_instance_get'
            config = (method_name, evpn_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            evpn_instance_item = util.find(util.root, './/ignore-as')
            return evpn_instance_item

        evpn_args['both'] = 'auto'
        evpn_args['evpn_instance'] = evpn_instance_name

        if not enable:
            method_name = 'evpn_evpn_instance_route_target_both_delete'

        else:
            method_name = 'evpn_evpn_instance_route_target_both_create'
            config = (method_name, evpn_args)
            callback(config)

            method_name = 'evpn_evpn_instance_route_target_both_update'
            evpn_args['ignore_as'] = True

        config = (method_name, evpn_args)
        return callback(config)

    def evpn_instance_duplicate_mac_timer(self, **kwargs):
        """
        Add "Duplicate MAC timer value" under evpn instance.

        Args:
            evpn_instance_name: Instance name for evpn
            duplicate_mac_timer_value: Duplicate MAC timer value.
            enable (bool): If target community needs to be enabled
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
            rbridge_id (str): rbridge-id for device. Only required when type is
                `ve`.
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if 'evpn_instance_name' is not passed.
            ValueError: if 'evpn_instance_name' is invalid.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.26.8.210']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...        output=dev.interface.evpn_instance_duplicate_mac_timer(
            ...         evpn_instance_name='evpn1',
            ...         duplicate_mac_timer_value='11')
            ...        output=dev.interface.evpn_instance_duplicate_mac_timer(
            ...         get=True,
            ...         evpn_instance_name='evpn1',
            ...         duplicate_mac_timer_value='11')
            ...        print output
            11
         """

        evpn_instance_name = kwargs.pop('evpn_instance_name', '')
        duplicate_mac_timer_value = kwargs.pop('duplicate_mac_timer_value',
                                               '180')
        enable = kwargs.pop('enable', True)
        get = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)

        evpn_args = dict()
        if get:
            enable = None

        if get:
            evpn_args['resource_depth'] = 3
            method_name = 'evpn_evpn_instance_get'
            config = (method_name, evpn_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            evpn_instance_item = util.find(
                util.root, './/duplicate-mac-timer-value')
            return evpn_instance_item

        evpn_args['evpn_instance'] = evpn_instance_name

        if not enable:
            method_name = 'evpn_evpn_instance_' \
                          'duplicate_mac_timer_delete'
            config = (method_name, evpn_args)
        else:

            evpn_args['duplicate_mac_timer_value'] = duplicate_mac_timer_value
            method_name = 'evpn_evpn_instance_' \
                          'duplicate_mac_timer_update'
            config = (method_name, evpn_args)

        return callback(config)

    def evpn_instance_mac_timer_max_count(self, **kwargs):
        """
        Add "Duplicate MAC max count" under evpn instance.

        Args:
            evpn_instance_name: Instance name for evpn
            max_count: Duplicate MAC max count.
            enable (bool): If target community needs to be enabled
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
                `ve`.
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if 'evpn_instance_name' is not passed.
            ValueError: if 'evpn_instance_name' is invalid.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.26.8.210']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...        output=dev.interface.evpn_instance_mac_timer_max_count(
            ...         evpn_instance_name='evpn1',
            ...         max_count='10')
            ...        output=dev.interface.evpn_instance_mac_timer_max_count(
            ...         get=True,
            ...         evpn_instance_name='evpn1',
            ...         max_count='10')
            ...        print output
            10
         """

        evpn_instance_name = kwargs.pop('evpn_instance_name', '')
        max_count = kwargs.pop('max_count', 5)
        enable = kwargs.pop('enable', True)
        get = kwargs.pop('get', False)
        callback = kwargs.pop('callback', self._callback)

        evpn_args = dict()
        if get:
            enable = None

        if get:
            evpn_args['resource_depth'] = 3
            method_name = 'evpn_evpn_instance_get'
            config = (method_name, evpn_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            evpn_instance_item = util.find(util.root, './/max-count')
            return evpn_instance_item

        evpn_args['evpn_instance'] = evpn_instance_name

        if not enable:
            method_name = 'evpn_evpn_instance_' \
                          'duplicate_mac_timer_delete'
            config = (method_name, evpn_args)
        else:
            evpn_args['max_count'] = max_count
            method_name = 'evpn_evpn_instance_' \
                          'duplicate_mac_timer_update'
            config = (method_name, evpn_args)

        return callback(config)

    def bridge_domain_router_interface(self, **kwargs):
        """Configure/get/delete router interface on a bridge-domain.
        Args:
            bridge_domain (str): bridge domain number.
            bridge_domain_service_type (str): service type. ('p2mp', 'p2p')
             (str): Type of interface. ['ethernet', 'port_channel']
            vlan_id (str): Vlan number.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete single/all LIFs on a bd.(True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `bridge_domain` or `vlan_id` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         dev.interface.bridge_domain_router_interface(
            ...         bridge_domain='100', vlan_id='100')
            ...         output = dev.interface.bridge_domain_router_interface(
            ...         get=True, bridge_domain='100')
            ...         print output
            ...         dev.interface.bridge_domain_router_interface(
            ...         delete=True, bridge_domain='100')
        """
        bridge_domain = kwargs.pop('bridge_domain')
        bridge_domain_service = kwargs.pop('bridge_domain_service_type', 'p2mp')

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        if bridge_domain_service not in ['p2mp', 'p2p']:
            raise ValueError("`bridge_domain_service_type` must "
                             "match one of them "
                             "`p2mp, p2p`")

        bd_args = dict(bridge_domain=(bridge_domain, bridge_domain_service))
        if delete:
            method_name = 'bridge_domain_router_interface_ve_delete'
            config = (method_name, bd_args)
            return callback(config)
        if not get_config:
            vlan_id = kwargs.pop('vlan_id')
            if not pyswitch.utilities.valid_vlan_id(vlan_id):
                raise InvalidVlanId("Invalid Vlan ID Value.")
            bd_args.update(router_ve=vlan_id)
            method_name = 'bridge_domain_router_interface_ve_update'
            config = (method_name, bd_args)
            result = callback(config)
        elif get_config:
            method_name = 'bridge_domain_router_interface_ve_get'
            config = (method_name, bd_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            result = util.find(util.root, './/Ve')
        return result

    def overlay_gateway_vlan_vni_auto(self, **kwargs):
        """Configure Overlay Gateway Vlan VNI mapping auto on VDX switches
        Args:
            gw_name: Name of Overlay Gateway
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete vlan to vni auto mapping. (True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `gw_name` is not passed.
            ValueError: if `gw_name` is invalid.
        Examples:
            >>> import pyswitch.device
            >>> conn = ('10.24.39.211', '22')
            >>> auth = ('admin', 'password')
            >>> with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...     output = dev.interface.overlay_gateway_vlan_vni_auto(
            ...     gw_name='Leaf')
            ...     output = dev.interface.overlay_gateway_vlan_vni_auto(
            ...     get=True)
            ...     output = dev.interface.overlay_gateway_vlan_vni_auto(
            ...     gw_name='Leaf', delete=True)
        """

        callback = kwargs.pop('callback', self._callback)
        get_config = kwargs.pop('get', False)
        if not get_config:
            gw_name = kwargs.pop('gw_name')

            config = ('overlay_gateway_map_vni_update', {
                'overlay_gateway': gw_name, 'auto': True})

        if get_config:
            gw_name = kwargs.pop('gw_name')
            config = (
                'overlay_gateway_map_vni_get', {
                    'overlay_gateway': gw_name})
            output = callback(config, handler='get_config')
            util = Util(output.data)
            if util.find(util.root, './/auto') is not None:
                return True
            else:
                return None

        if kwargs.pop('delete', False):
            config = (
                'overlay_gateway_map_vni_delete', {
                    'overlay_gateway': gw_name})

        return callback(config)

    def overlay_gateway_map_bd_vni(self, **kwargs):
        """configure overlay gateway bd vni mapping auto on slx switches
        args:
            gw_name (str): name of overlay gateway
            bd_vni_mapping (int): Specify BD to VNI mappings for the
                                  overlay gateway.
                                  <1-4096> bd id range
            vni (int): Specify VNI mapping for the BD.
                       <1-16777215> VNI/VNI range.
            get (bool): Get config instead of editing config. (True, False)
            delete (bool): True, delete the mapping.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `gw_name`, `bd_vni_mapping'
                      are not specified.
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         dev.interface.overlay_gateway_map_bd_vni(gw_name='leaf1',
            ...         bd_vni_mapping='10', vni='100')
            ...         output = dev.interface.overlay_gateway_map_bd_vni(
            ...         get=True, gw_name='leaf1')
            ...         dev.interface.overlay_gateway_map_bd_vni(gw_name='leaf1',
            ...         delete=True)
        """
        gw_name = kwargs.pop('gw_name')
        bd_vni_mapping = kwargs.pop('bd_vni_mapping', None)
        vni = kwargs.pop('vni', None)

        if bd_vni_mapping is not None and not\
                pyswitch.utilities.valid_vlan_id(bd_vni_mapping):
            raise InvalidVlanId("`bd_vni_mapping`"
                                " must be between `1` and `4096`")
        if vni is not None and\
                int(vni) not in xrange(1, 16777217):
            raise ValueError('`vni` %s must be in '
                             'range(1, 16777215)' % (vni))

        get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        callback = kwargs.pop('callback', self._callback)

        map_args = dict(overlay_gateway=gw_name)
        if delete:
            if bd_vni_mapping is not None:
                map_args.update(bd_vni_mapping=(bd_vni_mapping,))
            method_name = 'overlay_gateway_map_bd_vni_mapping_delete'
            config = (method_name, map_args)
            return callback(config)
        if not get_config:
            map_args.update(bd_vni_mapping=(bd_vni_mapping,),
                            vni=vni)
            method_name = 'overlay_gateway_map_bd_vni_mapping_create'
            config = (method_name, map_args)
            return callback(config)
        elif get_config:
            if bd_vni_mapping is not None:
                map_args.update(bd_vni_mapping=(bd_vni_mapping,))
            method_name = 'overlay_gateway_map_bd_vni_mapping_get'
            config = (method_name, map_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            result = {}
            if output.data != '<output></output>':
                if bd_vni_mapping is not None:
                    result = util.find(util.root, './/vni')
                else:
                    vls = util.findall(util.root, './/bridge-domain')
                    tvnis = []
                    for each_vl in vls:
                        method_name = 'overlay_gateway_map_vni_get'
                        map_args.update(bd_vni_mapping=str(each_vl))
                        output = callback(config, handler='get_config')
                        util = Util(output.data)
                        vni_value = util.find(util.root, './/vni')
                        tvnis.append(vni_value)
                    result = dict(vlans=vls, vnis=tvnis)
        return result

    def bridge_domain_all(self, **kwargs):
        """get all bridge-domains present on the device.
        Args:
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            None
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         dev.interface.bridge_domain(bridge_domain='100')
            ...         output = dev.interface.bridge_domain(
            ...         bridge_domain='100', get=True)
            ...         dev.interface.bridge_domain(bridge_domain='200')
            ...         output = dev.interface.bridge_domain_all()
        """
        callback = kwargs.pop('callback', self._callback)
        bd_args = {}
        config = (self.method_prefix('bridge_domain_get'), bd_args)
        output = callback(config, handler='get_config')
        util = Util(output.data)
        result = util.findall(util.root, './/bridge-domain-id')
        return result

    def bd_arp_suppression(self, **kwargs):
        """
        Enable Arp Suppression on a BD.

        Args:
            name: BD name on which the Arp suppression needs to be enabled.
            enable (bool): If arp suppression should be enabled
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `name` is not passed.
            ValueError: if `name` is invalid.
           output2 = dev.interface.bd_arp_suppression(name='89')
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.bd_arp_suppression(
            ...         name='89')
            ...         output = dev.interface.bd_arp_suppression(
            ...         get=True,name='89')
            ...         output = dev.interface.bd_arp_suppression(
            ...         enable=False,name='89')
            ...         # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            KeyError
         """

        name = kwargs.pop('name')
        enable = kwargs.pop('enable', True)

        callback = kwargs.pop('callback', self._callback)
        get = kwargs.pop('get', False)
        arp_args = dict(bridge_domain=(name, 'p2mp'))
        if int(name) < 1 or int(name) > 4096:
            raise ValueError("`name` must be between `1` and `4096`")

        if get:
            method_name = 'bridge_domain_suppress_arp_get'
            config = (method_name, arp_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            enable_item = util.find(util.root, './/enable')

            if enable_item is not None and enable_item == 'true':
                return True
            else:
                return None
        method_name = 'bridge_domain_suppress_arp_update'
        if not enable:
            arp_args['suppress_arp_enable'] = False
        else:
            arp_args['suppress_arp_enable'] = True

        config = (method_name, arp_args)
        return callback(config)

    def bd_nd_suppression(self, **kwargs):
        """
        Enable ND Suppression on a BD.

        Args:
            name: BD name on which the BD suppression needs to be enabled.
            enable (bool): If arp suppression should be enabled
                or disabled.Default:``True``.
            get (bool) : Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
               method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `name` is not passed.
            ValueError: if `name` is invalid.
           output2 = dev.interface.bd_arp_suppression(name='89')
        Examples:
            >>> import pyswitch.device
            >>> switches = ['10.24.39.211', '10.24.39.203']
            >>> auth = ('admin', 'password')
            >>> for switch in switches:
            ...     conn = (switch, '22')
            ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...         output = dev.interface.bd_nd_suppression(
            ...         name='89')
            ...         output = dev.interface.bd_nd_suppression(
            ...         get=True,name='89')
            ...         output = dev.interface.bd_nd_suppression(
            ...         enable=False,name='89')
            ...         # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            KeyError
         """

        name = kwargs.pop('name')
        enable = kwargs.pop('enable', True)

        callback = kwargs.pop('callback', self._callback)
        get = kwargs.pop('get', False)
        arp_args = dict(bridge_domain=(name, 'p2mp'))
        if int(name) < 1 or int(name) > 4096:
            raise ValueError("`name` must be between `1` and `4096`")

        if get:
            method_name = 'bridge_domain_suppress_nd_get'
            config = (method_name, arp_args)
            output = callback(config, handler='get_config')
            util = Util(output.data)
            enable_item = util.find(util.root, './/enable')

            if enable_item is not None and enable_item == 'true':
                return True
            else:
                return None
        method_name = 'bridge_domain_suppress_nd_update'
        if not enable:
            arp_args['suppress_nd_enable'] = False
        else:
            arp_args['suppress_nd_enable'] = True

        config = (method_name, arp_args)
        return callback(config)
