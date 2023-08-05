# Clases base


class Network:

    private_dns = None

    vpn_subnet = None
    vpn_gateway = None
    # TODO Crear componente VPN Gateway
    vpn_gateway_ip = None


    def __init__(self, id, name, cidr, networking):
        self.id = id
        self.name = name
        self.cidr = unicode(cidr)
        self.networking = networking

    def list_route_tables(self):
            raise NotImplementedError('list_route_tables not implemented for this driver')

    def list_security_groups(self):
        raise NotImplementedError('list_security_groups not implemented for this driver')

    def create_private_dns(self, domain):
        raise NotImplementedError('create_private_dns not implemented for this driver')

    def create_subnet(self, cidr, name=None):
            raise NotImplementedError('create_subnet not implemented for this driver')

    def list_subnets(self):
            raise NotImplementedError('list_subnets not implemented for this driver')

    def delete(self):
            raise NotImplementedError('delete not implemented for this driver')

    def attach_gateway(self, gateway):
            raise NotImplementedError('attach_gateway not implemented for this driver')

    def prepare_vpn_connection(self):
        raise NotImplementedError('prepare_vpn_connection not implemented for this driver')

    def get_vpn_connection_public_ip(self):
        raise NotImplementedError('get_vpn_connection_public_ip not implemented for this driver')

    def connect_to_vpn_network(self, cidr, public_ip, shared_key):
        raise NotImplementedError('connect_to_network not implemented for this driver')

    def start_vpn_connection(self):
        raise NotImplementedError('start_vpn_connection not implemented for this driver')

    # def refresh_dns_entries(self):
    #         raise NotImplementedError('refresh not implemented for this driver')
