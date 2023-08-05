from libcloud.dns.drivers.route53 import Route53DNSDriver as LibCloudRoute53DNSDriver
from libcloud.dns.base import Zone

from libcloud.utils.xml import findall, findtext

import uuid

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET

API_VERSION = '2013-04-01'
API_HOST = 'route53.amazonaws.com'
API_ROOT = '/%s/' % (API_VERSION)

NAMESPACE = 'https://%s/doc%s' % (API_HOST, API_ROOT)


class Route53DNSDriver(LibCloudRoute53DNSDriver):

    def ex_create_private_zone(self, domain, vpc_id, region):
        zone = ET.Element('CreateHostedZoneRequest', {'xmlns': NAMESPACE})
        ET.SubElement(zone, 'Name').text = domain
        ET.SubElement(zone, 'CallerReference').text = str(uuid.uuid4())
        hzg = ET.SubElement(zone, 'HostedZoneConfig')
        ET.SubElement(hzg, 'PrivateZone').text = "true"
        vpc = ET.SubElement(zone, 'VPC')
        ET.SubElement(vpc, 'VPCId').text = vpc_id
        ET.SubElement(vpc, 'VPCRegion').text = region
        uri = API_ROOT + 'hostedzone'
        data = ET.tostring(zone)
        rsp = self.connection.request(uri, method='POST', data=data).object
        elem = findall(element=rsp, xpath='HostedZone', namespace=NAMESPACE)[0]
        return self._to_zone(elem=elem)

    def _to_zone(self, elem):
        name = findtext(element=elem, xpath='Name', namespace=NAMESPACE)
        id = findtext(element=elem, xpath='Id',
                      namespace=NAMESPACE).replace('/hostedzone/', '')
        comment = findtext(element=elem, xpath='Config/Comment',
                           namespace=NAMESPACE)
        resource_record_count = int(findtext(element=elem,
                                             xpath='ResourceRecordSetCount',
                                             namespace=NAMESPACE))

        extra = {'Comment': comment, 'ResourceRecordSetCount':
                 resource_record_count}

        zone = Zone(id=id, domain=name, type='master', ttl=0, driver=self,
                    extra=extra)
        return zone