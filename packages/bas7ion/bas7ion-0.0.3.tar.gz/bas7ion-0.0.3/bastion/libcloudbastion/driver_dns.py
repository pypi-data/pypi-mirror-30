from libcloud.dns.providers import Provider
from libcloud.dns.providers import DRIVERS
from libcloud.dns.types import OLD_CONSTANT_TO_NEW_MAPPING
from libcloud.common.providers import get_driver as _get_provider_driver
from libcloud.common.providers import set_driver as _set_provider_driver

del DRIVERS[Provider.ROUTE53]
DRIVERS[Provider.ROUTE53] = ('bastion.libcloudbastion.route53', 'Route53DNSDriver')


def get_driver(provider):
    deprecated_constants = OLD_CONSTANT_TO_NEW_MAPPING
    return _get_provider_driver(drivers=DRIVERS, provider=provider,
                                deprecated_constants=deprecated_constants)


def set_driver(provider, module, klass):
    return _set_provider_driver(drivers=DRIVERS, provider=provider,
                                module=module, klass=klass)