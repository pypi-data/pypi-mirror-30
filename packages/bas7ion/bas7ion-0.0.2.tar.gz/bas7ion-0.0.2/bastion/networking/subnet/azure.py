# Subnet para Amazon

from bastion.networking.network_interface.azure import AzureNetworkInterface
from bastion.networking.subnet.base import Subnet
from bastion.component import Component


class AzureSubnet (Subnet, Component):

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def create_nic(self, private_ip, name=None):
        cloud_driver = self.get_cloud_driver()
        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.network.networking.driver.prop.location_id][0]
        nic = cloud_driver.ex_create_network_interface(name=name,
                                                       subnet=self,
                                                       resource_group=self.network.networking.driver.prop.resource_group,
                                                       location=location,
                                                       private_ip=private_ip)
        return AzureNetworkInterface(nic.id,
                                     nic.name,
                                     private_ip,
                                     self)

    def list_nics(self):
        cloud_driver = self.get_cloud_driver()
        all_nics = cloud_driver.ex_list_network_interfaces(resource_group=self.network.networking.driver.prop.resource_group)
        subnet_nics = []
        for lib_nic in all_nics:
            ips = lib_nic.extra["ipConfigurations"]
            for ip in ips:
                if ip["properties"]["subnet"]["id"] == self.id:
                    private_ip = ip["properties"]["privateIPAddress"]
                    subnet_nic = AzureNetworkInterface(lib_nic.id,
                                                       lib_nic.name,
                                                       private_ip,
                                                       self)
                    subnet_nics.append(subnet_nic)
        return subnet_nics

    def delete(self):
        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_delete_subnet(resource_group=self.network.networking.driver.prop.resource_group,
                                      name=self.name,
                                      network_name=self.network.name)
