# Clases base

import hashlib


class Networking:
    def __init__(self, driver):
        self.driver = driver

    def create_network(self, **kwargs):
        raise NotImplementedError('create_network not implemented for this driver')

    def get_network(self, network_id):
        raise NotImplementedError('list_networks not implemented for this driver')

    def list_networks(self):
        raise NotImplementedError('list_networks not implemented for this driver')

    def create_gateway(self, name=None):
        raise NotImplementedError('create_gateway not implemented for this driver')

    @staticmethod
    def connect_networks(network1, network2):

        print "Preparando conexion VPN ..."

        network1.prepare_vpn_connection()
        network2.prepare_vpn_connection()

        print "Esperando asignacion de IPs Publicas ..."

        network1_vpn_public_ip = network1.get_vpn_connection_public_ip()
        network2_vpn_public_ip = network2.get_vpn_connection_public_ip()

        print "Conectando terminales VPN ..."

        shared_key = hashlib.sha512().hexdigest()
        network1.connect_to_vpn_network(network2.cidr, network2_vpn_public_ip, shared_key)
        network2.connect_to_vpn_network(network1.cidr, network1_vpn_public_ip, shared_key)

        network1.start_vpn_connection()
        network2.start_vpn_connection()

        print "Conexion VPN establecida!"

