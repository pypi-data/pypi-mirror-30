# Security Group para AWS

from bastion.networking.security_group.base import SecurityGroup
from bastion.component import Component


class AWSSecurityGroup (SecurityGroup, Component):

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def allow_inbound_traffic(self, port):
        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_authorize_security_group_ingress(id=self.id,
                                                         from_port=port,
                                                         to_port=port,
                                                         cidr_ips=["0.0.0.0/0"])

    def delete(self):
        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_delete_security_group_by_id(group_id=self.id)
