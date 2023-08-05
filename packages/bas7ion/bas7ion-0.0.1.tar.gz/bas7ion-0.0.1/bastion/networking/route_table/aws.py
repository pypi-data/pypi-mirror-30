from bastion.networking.route_table.base import RouteTable


class AWSRouteTable(RouteTable):
    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def list_routes(self):
        return self.routes

    def create_route(self, cidr, internet_gateway=None, network_interface=None):
        cloud_driver = self.get_cloud_driver()
        route = cloud_driver.ex_create_route(self, cidr, internet_gateway=internet_gateway,
                                             network_interface=network_interface)

        return route

    def list_subnet_associations(self):
        return self.subnet_associations

    def create_subnet_association(self, subnet):
        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_associate_route_table(self, subnet)

    def delete(self):
        raise NotImplementedError('delete not implemented for this driver')
