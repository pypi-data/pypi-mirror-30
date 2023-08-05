from bastion.provider_types import Providers
from bastion.compute.aws import AWSBaseCompute
from bastion.networking.aws import AWSNetworking
from bastion.compute.azure import AzureBaseCompute
from bastion.networking.azure import AzureNetworking
from libcloud.compute.types import Provider
from bastion.libcloudbastion.driver import get_driver
from bastion.component import Component

from bastion.libcloudbastion.driver_dns import get_driver as get_dns_driver
from libcloud.dns.types import Provider as DNSProvider


class Driver:

    prop = None
    cred = None

    def __init__(self):
        pass

    @staticmethod
    def create(provider_info):

        if provider_info.type == Providers.AWS:
            driver = AWSDriver(provider_info)
        if provider_info.type == Providers.AZURE:
            driver = AzureDriver(provider_info)

        return driver


class AzureDriver(Driver, Component):

    def __init__(self, provider_info):
        cls = get_driver(Provider.AZURE_ARM)
        self._cloud_driver = cls(tenant_id=provider_info.cred.tenant_id, subscription_id=provider_info.cred.subscription_id, key=provider_info.cred.application_id, secret=provider_info.cred.password)
        self.baseCompute = AzureBaseCompute(self)
        self.networking = AzureNetworking(self)
        self.prop = provider_info.prop
        self.cred = provider_info.cred

    def get_cloud_driver(self):
        return self._cloud_driver


class AWSDriver(Driver, Component):

    def __init__(self, provider_info):
        cls = get_driver(Provider.EC2)
        self._cloud_driver = cls(provider_info.cred.access_key, provider_info.cred.secret_key, region=provider_info.cred.region)
        self.baseCompute = AWSBaseCompute(self)
        self.networking = AWSNetworking(self)
        self.prop = provider_info.prop
        self.cred = provider_info.cred
        cls = get_dns_driver(DNSProvider.ROUTE53)
        dns_credentials = (provider_info.cred.access_key, provider_info.cred.secret_key)
        self.dns_driver = cls(*dns_credentials)

    def get_cloud_driver(self):
        return self._cloud_driver
