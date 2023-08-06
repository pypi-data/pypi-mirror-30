from pyswitch.os.base.system import System as BaseSystem
from pyswitch.utilities import Util


class System(BaseSystem):
    """
        System class containing all system level methods and attributes.
        """

    def __init__(self, callback):
        """System init method.
        Args:
            callback: Callback function that will be called for each action.
        Returns:
            System Object
        Raises:
            None
        """

        super(System, self).__init__(callback)

    def chassis_name(self, **kwargs):
        """Get device's chassis name/Model.
        Args:
            rbridge_id (str): The rbridge ID of the device.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `rbridge_id` is not specified.
        Examples:
        >>> import pyswitch.device
        >>> switches = ['10.24.39.231']
        >>> auth = ('admin', 'password')
        >>> for switch in switches:
        ...     conn = (switch, '22')
        ...     with pyswitch.device.Device(conn=conn, auth=auth) as dev:
        ...         output = dev.system.chassis_name(rbridge_id='1')
        """

        rbridge_id = kwargs.pop('rbridge_id')
        chname_args = dict(rbridge_id=rbridge_id, resource_depth=2)
        config = ('rbridge_id_get', chname_args)

        output = self._callback(config, handler='get_config')

        util = Util(output.data)

        chassis_name = util.find(util.root, './/chassis-name')

        return chassis_name

    def router_id(self, **kwargs):
        """Configures device's Router ID.
        Args:
            router_id (str): Router ID for the device.
            rbridge_id (str): The rbridge ID of the device on which BGP will be
                configured in a VCS fabric.
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `router_id` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> conn = ('10.24.39.231', '22')
            >>> auth = ('admin', 'password')
            >>> with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...     output = dev.system.router_id(router_id='10.24.39.231',
            ...     rbridge_id='231')
        """
        router_id = kwargs.pop('router_id')
        rbridge_id = kwargs.pop('rbridge_id', '1')
        callback = kwargs.pop('callback', self._callback)

        rid_args = dict(rbridge_id=rbridge_id, router_id=router_id)
        config = ('rbridge_id_ip_router_id_update', rid_args)
        return callback(config)

    def host_name(self, **kwargs):
        """Configures device's host name.
        Args:
            rbridge_id (str): The rbridge ID of the device on which BGP will be
                configured in a VCS fabric.
            host_name (str): The host name of the device.
            get (bool): Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `rbridge_id` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> conn = ('10.24.39.231', '22')
            >>> auth = ('admin', 'password')
            >>> with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...     output = dev.system.host_name(rbridge_id='231',
            ...     host_name='sw0_231')
            ...     output = dev.system.host_name(rbridge_id='231', get=True)
            ...     print output
        """
        is_get_config = kwargs.pop('get', False)
        rbridge_id = kwargs.pop('rbridge_id')
        if not is_get_config:
            host_name = kwargs.pop('host_name', 'sw0')
        else:
            host_name = ' '
        callback = kwargs.pop('callback', self._callback)
        rid_args = dict(rbridge_id=rbridge_id, host_name=host_name)

        config = ('rbridge_id_switch_attributes_update', rid_args)

        if is_get_config:
            config = (
                'rbridge_id_get', {
                    'resource_depth': 2, 'rbridge_id': rbridge_id})
            output = callback(config, handler='get_config')

            util = Util(output.data)

            return util.find(util.root, './/host-name')

        return callback(config)

    def rbridge_id(self, **kwargs):
        """Configures device's rbridge ID. Setting this property will need
        a switch reboot
        Args:
            rbridge_id (str): The rbridge ID of the device on which BGP will be
                configured in a VCS fabric.
            get (bool): Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `rbridge_id` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> conn = ('10.24.39.211', '22')
            >>> auth = ('admin', 'password')
            >>> with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...     output = dev.system.rbridge_id(rbridge_id='225')
            ...     output = dev.system.rbridge_id(rbridge_id='225', get=True)
        """
        callback = kwargs.pop('callback', self._callback)
        is_get_config = kwargs.pop('get', False)
        if not is_get_config:
            rbridge_id = kwargs.pop('rbridge_id')
        else:
            rbridge_id = ''

        if is_get_config:
            config = ('rbridge_id_get', {})
            op = callback(config, handler='get_config')

            util = Util(op.data)
            return util.find(util.root, 'rbridge-id')

        rid_args = dict(rbridge_id=rbridge_id)
        config = ('vcs_rbridge_config_rpc', rid_args)
        return callback(config)

    def maintenance_mode(self, **kwargs):
        """Configures maintenance mode on the device
        Args:
            rbridge_id (str): The rbridge ID of the device on which
            Maintenance mode
                will be configured in a VCS fabric.
            get (bool): Get config instead of editing config. (True, False)
            callback (function): A function executed upon completion of the
                method.  The only parameter passed to `callback` will be the
                ``ElementTree`` `config`.
        Returns:
            Return value of `callback`.
        Raises:
            KeyError: if `rbridge_id` is not specified.
        Examples:
            >>> import pyswitch.device
            >>> conn = ('10.24.39.202', '22')
            >>> auth = ('admin', 'password')
            >>> with pyswitch.device.Device(conn=conn, auth=auth) as dev:
            ...     output = dev.system.maintenance_mode(rbridge_id='226')
            ...     output = dev.system.maintenance_mode(rbridge_id='226',
            ...     get=True)
            ...     assert output == True
            ...     output = dev.system.maintenance_mode(rbridge_id='226',
            ...     delete=True)
            ...     output = dev.system.maintenance_mode(rbridge_id='226',
            ...     get=True)
            ...     assert output == False
        """
        is_get_config = kwargs.pop('get', False)
        delete = kwargs.pop('delete', False)
        rbridge_id = kwargs.pop('rbridge_id')
        callback = kwargs.pop('callback', self._callback)
        rid_args = dict(rbridge_id=rbridge_id)

        if is_get_config:
            config = ('rbridge_id_get', rid_args)
            maint_mode = callback(config, handler='get_config')

            util = Util(maint_mode.data)

            system_mode = util.findNode(util.root, './/system-mode')
            maintenance = util.find(system_mode, './/maintenance')
            if maintenance:
                return True
            else:
                return False

        if delete:
            rid_args['maintenance'] = False
        else:
            rid_args['maintenance'] = True
        config = ('rbridge_id_system_mode_update', rid_args)
        return callback(config)

    def system_ip_mtu(self, **kwargs):
        """Set system mtu.

            Args:

                mtu (str): Value between 1522 and 9216
                version (int) : 4 or 6
                callback (function): A function executed upon completion of
                    the method.  The only parameter passed to `callback` will
                    be the
                    ``ElementTree`` `config`.

            Returns:
                Return value of `callback`.

            Raises:
                KeyError: if `int_type`, `name`, or `mtu` is not specified.
                ValueError: if `int_type`, `name`, or `mtu` is invalid.

            Examples:
                >>> import pyswitch.device
                >>> switches = ['10.24.39.231']
                >>> auth = ('admin', 'password')
                >>> for switch in switches:
                ...  conn = (switch, '22')
                ...  with pyswitch.device.Device(conn=conn, auth=auth) as dev:
                ...         output = dev.system.system_ip_mtu(mtu='1666')
                ...         output = dev.system.system_ip_mtu(get=True)
                ...         assert output == '1666'
                ...         output = dev.system.system_ip_mtu(mtu='1667',version=6)
                ...         output = dev.system.system_ip_mtu(get=True,version=6)
                ...         assert output == '1667'
            """

        callback = kwargs.pop('callback', self._callback)
        version = kwargs.pop('version', 4)
        if version is 4:
            ip_prefix = 'ip'
            # ns = '{urn:brocade.com:mgmt:brocade-ip-access-list}'
        if version is 6:
            ip_prefix = 'ipv6'
            # ns = '{urn:brocade.com:mgmt:brocade-mld-snooping}'

        if kwargs.pop('get', False):
            method_name = '%s_mtu_get' % ip_prefix
            config = (method_name, {})
            op = callback(config, handler='get_config')

            util = Util(op.data)
            return util.find(util.root, './/mtu')

        mtu = kwargs.pop('mtu')

        if version is 4:
            minimum_mtu = 1300
            maximum_mtu = 9100
            if int(mtu) < minimum_mtu or int(mtu) > maximum_mtu:
                raise ValueError(
                    "Incorrect mtu value, Valid Range %s-%s" %
                    (minimum_mtu, maximum_mtu))
        if version is 6:
            minimum_mtu = 1280
            maximum_mtu = 9100
            if int(mtu) < minimum_mtu or int(mtu) > maximum_mtu:
                raise ValueError(
                    "Incorrect mtu value, Valid Range %s-%s" %
                    (minimum_mtu, maximum_mtu))

        mtu_name = 'global_%s_mtu' % ip_prefix
        mtu_args = {mtu_name: mtu}

        method_name = '%s_mtu_update' % ip_prefix

        config = (method_name, mtu_args)
        return callback(config)

    def system_l2_mtu(self, **kwargs):
        """Set system mtu.

            Args:

                mtu (str): Value between 1522 and 9216
                version (int) : 4 or 6
                callback (function): A function executed upon completion of
                the method.  The only parameter passed to `callback` will be
                 the
                    ``ElementTree`` `config`.

            Returns:
                Return value of `callback`.

            Raises:
                KeyError: if `int_type`, `name`, or `mtu` is not specified.
                ValueError: if `int_type`, `name`, or `mtu` is invalid.

            Examples:
                >>> import pyswitch.device
                >>> switches = ['10.24.39.231']
                >>> auth = ('admin', 'password')
                >>> for switch in switches:
                ...  conn = (switch, '22')
                ...  with pyswitch.device.Device(conn=conn, auth=auth) as dev:
                ...         output = dev.system.system_l2_mtu(mtu='1666')
                ...         output = dev.system.system_l2_mtu(get=True)
                ...         assert output == '1666'
                ...         output = dev.system.system_l2_mtu(mtu='1667',version=6)
                ...         output = dev.system.system_l2_mtu(get=True,version=6)
                ...         assert output == '1667'
            """

        callback = kwargs.pop('callback', self._callback)

        if kwargs.pop('get', False):
            method_name = 'mtu_get'
            config = (method_name, {})
            op = callback(config, handler='get_config')

            util = Util(op.data)
            return util.find(util.root, './/mtu')

        mtu = kwargs.pop('mtu')

        minimum_mtu = 1522
        maximum_mtu = 9216
        if int(mtu) < minimum_mtu or int(mtu) > maximum_mtu:
            raise ValueError(
                "Incorrect mtu value, Valid Range %s-%s" %
                (minimum_mtu, maximum_mtu))

        mtu_name = 'global_l2_mtu'
        mtu_args = {mtu_name: mtu}

        method_name = 'mtu_update'

        config = (method_name, mtu_args)
        return callback(config)
