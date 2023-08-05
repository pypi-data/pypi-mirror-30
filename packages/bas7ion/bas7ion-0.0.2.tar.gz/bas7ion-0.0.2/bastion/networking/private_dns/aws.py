
from bastion.networking.private_dns.base import PrivateDns
from bastion.component import Component
from libcloud.dns.base import RecordType


class AWSPrivateDns(PrivateDns, Component):

    def __init__(self, domain, dns_server, network):
        super(AWSPrivateDns, self).__init__(dns_server, network)
        self.domain = domain

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def add_hostname(self, hostname, vm):
        self.network.networking.driver.dns_driver.create_record(name=hostname,
                                                                zone=self.dns_server,
                                                                type=RecordType.A,
                                                                data=vm.private_ips[0])
