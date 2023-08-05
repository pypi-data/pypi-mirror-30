from libcloud.common.providers import get_driver as _get_provider_driver
from libcloud.common.providers import set_driver as _set_provider_driver
from libcloud.compute.providers import DEPRECATED_DRIVERS
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import OLD_CONSTANT_TO_NEW_MAPPING
from libcloud.compute.providers import Provider

del DRIVERS[Provider.AZURE_ARM]
DRIVERS[Provider.AZURE_ARM] = ('bastion.libcloudbastion.azure_arm', 'AzureNodeDriver')
del DRIVERS[Provider.EC2]
DRIVERS[Provider.EC2] = ('bastion.libcloudbastion.ec2', 'EC2NodeDriver')


def get_driver(provider):
    deprecated_constants = OLD_CONSTANT_TO_NEW_MAPPING
    return _get_provider_driver(drivers=DRIVERS, provider=provider,
                                deprecated_providers=DEPRECATED_DRIVERS,
                                deprecated_constants=deprecated_constants)


def set_driver(provider, module, klass):
    return _set_provider_driver(drivers=DRIVERS, provider=provider,
                                module=module, klass=klass)
