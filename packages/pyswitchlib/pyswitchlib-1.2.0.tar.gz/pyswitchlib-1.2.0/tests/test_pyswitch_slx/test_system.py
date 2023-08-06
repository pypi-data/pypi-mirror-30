from __future__ import absolute_import
import unittest
from pyswitch.device import Device


class SystemTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = ('10.24.4.215', '22')

        self.auth = ('admin', 'password')
        self.rbridge_id = '1'
        self.system_ip_mtu = '1610'
        self.system_ipv6_mtu = '3910'
        self.system_mtu = '2100'

    def test_uptime(self):
        with Device(conn=self.conn, auth=self.auth) as dev:
            print dev.system.uptime

    def test_chassis_name(self):
        with Device(conn=self.conn, auth=self.auth) as dev:
            print dev.system.chassis_name()

    def test_rbridge_id_router_id(self):
        with Device(conn=self.conn, auth=self.auth) as dev:
            with self.assertRaises(ValueError) as context:
                dev.system.router_id(router_id='10.24.39.211',
                                     rbridge_id='1')
                print context

    def test_host_name(self):

        with Device(conn=self.conn, auth=self.auth) as dev:
            dev.system.host_name(rbridge_id='1',
                                 host_name='sw0-test')
            output = dev.system.host_name(rbridge_id='1', get=True)

            print 'Host Name %s' % output
            self.assertEqual('sw0-test', output)

    def test_rbridge_id(self):
        with Device(conn=self.conn, auth=self.auth) as dev:
            with self.assertRaises(ValueError) as context:
                dev.system.rbridge_id(get=True)
                print context

    def test_maintenance_mode(self):
        with Device(conn=self.conn, auth=self.auth) as dev:
            with self.assertRaises(ValueError) as context:
                dev.system.maintenance_mode(rbridge_id='1')
                print context

    def test_system_ip_mtu(self):
        with Device(conn=self.conn, auth=self.auth) as dev:
            with self.assertRaises(ValueError) as context:
                dev.system.system_ip_mtu(mtu=self.system_ip_mtu)
                print context

    def test_system_l2_mtu(self):

        with Device(conn=self.conn, auth=self.auth) as dev:
            with self.assertRaises(ValueError) as context:
                dev.system.system_l2_mtu(mtu=self.system_mtu)
                print context
