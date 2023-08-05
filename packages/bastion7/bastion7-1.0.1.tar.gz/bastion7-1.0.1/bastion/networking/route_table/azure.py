from bastion.networking.route_table.base import RouteTable


class AzureRouteTable(RouteTable):

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

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
