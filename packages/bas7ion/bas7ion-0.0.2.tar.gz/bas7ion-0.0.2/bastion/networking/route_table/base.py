# Clases base


class RouteTable:

    def __init__(self, id, name, routes, subnet_associations,
                 propagating_gateway_ids, network, extra=None):
        self.id = id
        self.name = name
        self.routes = routes
        self.subnet_associations = subnet_associations
        self.propagating_gateway_ids = propagating_gateway_ids
        self.network = network
        self.extra = extra or {}

    def list_routes(self):
            raise NotImplementedError('list_routes not implemented for this driver')

    def create_route(self, cidr, internet_gateway=None):
            raise NotImplementedError('create_route not implemented for this driver')

    def list_subnet_associations(self):
            raise NotImplementedError('list_subnet_associations not implemented for this driver')

    def create_subnet_association(self, subnet):
            raise NotImplementedError('create_subnet_associations not implemented for this driver')

    def delete(self):
            raise NotImplementedError('delete not implemented for this driver')
