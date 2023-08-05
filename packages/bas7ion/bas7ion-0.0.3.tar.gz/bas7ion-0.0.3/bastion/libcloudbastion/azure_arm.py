
import time

from libcloud.compute.drivers.azure_arm import AzureNodeDriver as LibCloudAzureNodeDriver
from libcloud.compute.drivers.azure_arm import AzureNetwork, AzureSubnet, AzureNic
from libcloud.common.types import LibcloudError


class AzureLocalNetworkGateway:
    def __init__(self, id, name, address_space, gateway_ip_address):
        self.id = id
        self.name = name
        self.address_space = address_space
        self.gatewayIpAddress = gateway_ip_address


class AzureVirtualPrivateGateway:
    def __init__(self, id, name, public_ip):
        self.id = id
        self.name = name
        self.public_ip = public_ip


class AzureConnection:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class AzureNodeDriver(LibCloudAzureNodeDriver):

    def ex_update_network(self, resource_group, location_id, cidr_block, name, dns_server):

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s" \
                 % (self.connection.subscription_id, resource_group, name)

        r = self.connection.request(action,
                                    params={"api-version": "2017-08-01"},
                                    method="GET")

        data = r.object

        data["properties"]["dhcpOptions"] = {
                                                "dnsServers": [
                                                    dns_server
                                                ]
                                            }

        r = self.connection.request(action,
                                    params={"api-version": "2017-08-01"},
                                    method="PUT",
                                    data=data)

        return AzureNetwork(r.object["id"],
                            r.object["name"],
                            r.object["location"],
                            r.object["properties"])

    def ex_create_network(self, resource_group, location_id, cidr_block, dns_server=None, name=None):

        data = {
            "location": location_id,
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        cidr_block
                    ]
                }
            }
        }

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s" \
                 % (self.connection.subscription_id, resource_group, name)

        r = self.connection.request(action,
                                    params={"api-version": "2017-03-01"},
                                    method="PUT",
                                    data=data)
        return AzureNetwork(r.object["id"],
                            r.object["name"],
                            r.object["location"],
                            r.object["properties"])

    def ex_delete_network(self, resource_group, name):

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s" \
                 % (self.connection.subscription_id, resource_group, name)

        r = self.connection.request(action,
                                    params={"api-version": "2017-03-01"},
                                    method="DELETE")

    def ex_create_subnet(self, resource_group, cidr_block, network_name, name=None):

        data = {
            "properties": {
                "addressPrefix": cidr_block
            }
        }

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s/subnets/%s" \
                 % (self.connection.subscription_id, resource_group, network_name, name)

        r = self.connection.request(action,
                                    params={"api-version": "2017-03-01"},
                                    method="PUT",
                                    data=data)

        return AzureSubnet(r.object["id"],
                           r.object["name"],
                           r.object["properties"])

    def ex_delete_subnet(self, resource_group, name, network_name):

        action = "/subscriptions/%s/resourceGroups/%s/providers/" \
                 "Microsoft.Network/virtualNetworks/%s/subnets/%s" \
                 % (self.connection.subscription_id, resource_group, network_name, name)

        r = self.connection.request(action,
                                    params={"api-version": "2016-09-01"},
                                    method="DELETE")

    def ex_create_public_ip(self, name, resource_group, location=None, allocation_method='Dynamic'):
        """
        Create a public IP resources.

        :param name: Name of the public IP resource
        :type name: ``str``

        :param resource_group: The resource group to create the public IP
        :type resource_group: ``str``

        :param location: The location at which to create the public IP
        (if None, use default location specified as 'region' in __init__)
        :type location: :class:`.NodeLocation`

        :param allocation_method:
        :type location: ``str``

        :return: The newly created public ip object
        :rtype: :class:`.AzureIPAddress`
        """

        if location is None:
            if self.default_location:
                location = self.default_location
            else:
                raise ValueError("location is required.")

        target = "/subscriptions/%s/resourceGroups/%s/" \
                 "providers/Microsoft.Network/publicIPAddresses/%s" \
                 % (self.subscription_id, resource_group, name)
        data = {
            "location": location.id,
            "tags": {},
            "properties": {
                "publicIPAllocationMethod": allocation_method
            }
        }
        r = self.connection.request(target,
                                    params={"api-version": "2017-09-01"},
                                    data=data,
                                    method='PUT'
                                    )
        return self._to_ip_address(r.object)

    # def ex_get_public_ip(self, name, resource_group):
    #     """
    #     Create a public IP resources.
    #
    #     :param name: Name of the public IP resource
    #     :type name: ``str``
    #
    #     :param resource_group: The resource group to create the public IP
    #     :type resource_group: ``str``
    #
    #     """
    #
    #     "/Microsoft.Network/publicIPAddresses/{publicIpAddressName}?api-version=2017-09-01"
    #
    #     target = "/subscriptions/%s/resourceGroups/%s/" \
    #              "providers/Microsoft.Network/publicIPAddresses/%s" \
    #              % (self.subscription_id, resource_group, name)
    #
    #     r = self.connection.request(target,
    #                                 params={"api-version": "2017-09-01"},
    #                                 method='GET'
    #                                 )
    #     return self._to_ip_address(r.object)

    def wait_until_public_ip_running(self, public_ip_id, wait_period=3, timeout=600):
        """
        Block until the provided nodes are considered running.

        Node is considered running when it's state is "running" and when it has
        at least one IP address assigned.

        :param public_ip_id: Public IP Id.
        :type public_ip_id: ``str``

        :param wait_period: How many seconds to wait between each loop
                            iteration. (default is 3)
        :type wait_period: ``int``

        :param timeout: How many seconds to wait before giving up.
                        (default is 600)
        :type timeout: ``int``
        """

        start = time.time()
        end = start + timeout

        while time.time() < end:

            pub_addr = self.ex_get_public_ip(public_ip_id)
            addr = pub_addr.extra.get("ipAddress")
            if addr:
                return pub_addr
            else:
                time.sleep(wait_period)
                continue

        raise LibcloudError(value='Timed out after %s seconds' % (timeout),
                            driver=self)

    def ex_create_network_interface(self, name, subnet, resource_group,
                                    location=None, public_ip=None, private_ip=None):
        """
        Create a virtual network interface (NIC).

        :param name: Name of the NIC resource
        :type name: ``str``

        :param subnet: The subnet to attach the NIC
        :type subnet: :class:`.AzureSubnet`

        :param resource_group: The resource group to create the NIC
        :type resource_group: ``str``

        :param location: The location at which to create the NIC
        (if None, use default location specified as 'region' in __init__)
        :type location: :class:`.NodeLocation`

        :param public_ip: Associate a public IP resource with this NIC
        (optional).
        :type public_ip: :class:`.AzureIPAddress`

        :return: The newly created NIC
        :rtype: :class:`.AzureNic`
        """

        if location is None:
            if self.default_location:
                location = self.default_location
            else:
                raise ValueError("location is required.")

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/networkInterfaces/%s" \
                 % (self.subscription_id, resource_group, name)

        data = {
            "location": location.id,
            "tags": {},
            "properties": {
                "ipConfigurations": [{
                    "name": "myip1",
                    "properties": {
                        "subnet": {
                            "id": subnet.id
                        },
                        "privateIPAllocationMethod": "Dynamic"
                    }
                }]
            }
        }

        if private_ip:
            data["properties"]["ipConfigurations"][0]["properties"]["privateIPAllocationMethod"] = "Static"
            data["properties"]["ipConfigurations"][0]["properties"]["privateIPAddress"] = private_ip

        if public_ip:
            data["properties"]["ipConfigurations"][0]["properties"]["publicIPAddress"] = {
                "id": public_ip.id
            }

        r = self.connection.request(target,
                                    params={"api-version": "2016-09-01"},
                                    data=data,
                                    method='PUT'
                                    )
        return AzureNic(r.object["id"], r.object["name"], r.object["location"],
                        r.object["properties"])

    def ex_list_network_interfaces(self, resource_group):

        action = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/networkInterfaces" \
                 % (self.subscription_id, resource_group)
        r = self.connection.request(action,
                                    params={"api-version": "2017-09-01"},
                                    method="GET"
                                    )
        return [AzureNic(nic["id"], nic["name"], nic["location"],
                         nic["properties"]) for nic in r.object["value"]]

    def ex_create_local_network_gateway(self, name, address_space, gateway_ip_address, resource_group,
                                        location=None):

        if location is None:
            if self.default_location:
                location = self.default_location
            else:
                raise ValueError("location is required.")

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/localNetworkGateways/%s" \
                 % (self.subscription_id, resource_group, name)

        data = {
            "location": location.id,
            "tags": {},
            "properties": {
                "localNetworkAddressSpace": {
                    "addressPrefixes": [
                        address_space
                    ]
                },
                "gatewayIpAddress": gateway_ip_address,
            }
        }

        r = self.connection.request(target,
                                    params={"api-version": "2017-03-01"},
                                    data=data,
                                    method='PUT'
                                    )

        return AzureLocalNetworkGateway(r.object["id"],
                                        r.object["name"],
                                        address_space,
                                        gateway_ip_address)

    def ex_create_virtual_network_gateway(self, name, subnet, resource_group,
                                          location=None, public_ip=None):

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/virtualNetworkGateways/%s" \
                 % (self.subscription_id, resource_group, name)

        data = {
            "location": location.id,
            "tags": {},
            "properties": {
                "ipConfigurations": [{
                    "properties": {
                        "privateIPAllocationMethod": "Dynamic",
                        "subnet": {
                            "id": subnet.id
                        },
                        "publicIPAddress": {
                            "id": public_ip.id
                        }
                    },
                    "name": name
                }],
                "gatewayType": "Vpn",
                "vpnType": "RouteBased"
            }
        }

        r = self.connection.request(target,
                                    params={"api-version": "2017-03-01"},
                                    data=data,
                                    method='PUT'
                                    )

        return AzureVirtualPrivateGateway(r.object["id"],
                                          r.object["name"],
                                          public_ip)

    def ex_create_virtual_network_gateway_connection(self, name, resource_group, shared_key,
                                                     location=None, local_network_gateway=None,
                                                     virtual_network_gateway=None):

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/connections/%s" \
                 % (self.subscription_id, resource_group, name)

        data = {
            "location": location.id,
            "tags": {},
            "properties": {
                "sharedKey": shared_key,
                "virtualNetworkGateway1": {
                    "id": virtual_network_gateway.id
                },
                "localNetworkGateway2": {
                    "id": local_network_gateway.id
                },
                "connectionType": "Ipsec"
            }
        }

        r = self.connection.request(target,
                                    params={"api-version": "2017-03-01"},
                                    data=data,
                                    method='PUT'
                                    )

        return AzureConnection(r.object["id"],
                               r.object["name"])

    def ex_get_virtual_network_gateway_state(self, name, resource_group):

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/virtualNetworkGateways/%s" \
                 % (self.subscription_id, resource_group, name)

        r = self.connection.request(target,
                                    params={"api-version": "2017-03-01"},
                                    method='GET'
                                    )

        return r.object["properties"]["ipConfigurations"][0]["properties"]["provisioningState"]

    def ex_delete_network_interface(self, name, resource_group):

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Network/networkInterfaces/%s" \
                 % (self.subscription_id, resource_group, name)

        r = self.connection.request(target,
                                    params={"api-version": "2017-09-01"},
                                    method='DELETE'
                                    )

    def ex_attach_network_interface(self, vm_name, nic_id, resource_group, location_id):

        target = "/subscriptions/%s/resourceGroups/%s/providers" \
                 "/Microsoft.Compute/virtualMachines/%s" \
                 % (self.subscription_id, resource_group, vm_name)

        data = {
            "location": location_id,
            "properties": {
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": nic_id,
                            "properties": {
                                "primary": "true"
                            }
                        }
                    ]
                }
            }
        }

        r = self.connection.request(target,
                                    params={"api-version": "2017-12-01"},
                                    data=data,
                                    method='PUT'
                                    )
