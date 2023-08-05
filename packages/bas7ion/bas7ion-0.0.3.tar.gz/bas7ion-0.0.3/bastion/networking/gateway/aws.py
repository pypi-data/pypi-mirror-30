# Clases base
from bastion.networking.gateway.base import Gateway
from bastion.component import Component


class AWSGateway(Gateway, Component):

    def get_cloud_driver(self):
        return self.networking.get_cloud_driver()
