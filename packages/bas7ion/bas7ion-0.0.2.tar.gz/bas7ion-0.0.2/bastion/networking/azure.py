# Networking para Azure

from bastion.component import Component
from bastion.networking.base import Networking
from bastion.networking.network.azure import AzureNetwork


class AzureNetworking(Networking, Component):

    def get_cloud_driver(self):
        return self.driver.get_cloud_driver()

    def create_network(self, cidr, name=None, dns=False):

        print "Creando Red Virtual Azure ..."

        cloud_driver = self.get_cloud_driver()
        cloud_network = cloud_driver.ex_create_network(cidr_block=cidr,
                                                       name=name,
                                                       resource_group=self.driver.prop.resource_group,
                                                       location_id=self.driver.prop.location_id)

        network = AzureNetwork(cloud_network.id,
                               cloud_network.name,
                               cidr,
                               self)

        # Create the VPN Subnet
        network.create_vpn_subnet()

        # Create the DNS Subnet
        if dns:
            network.create_dns_subnet()

        print "Red Virtual Azure creada con nombre='{0}', cidr='{1}'.".format(
            network.name,
            cidr)

        return network

    def get_network(self, network_id):
        pass

    def list_networks(self):
        cloud_driver = self.get_cloud_driver()
        networks = cloud_driver.ex_list_networks()
        result = list()
        for n in networks:
            result.append(AzureNetwork(n.id,
                                       n.name,
                                       n.extra["addressSpace"]["addressPrefixes"],
                                       self))
        return result

    def create_gateway(self, name=None):
        raise NotImplementedError('create_gateway not implemented for this driver')
