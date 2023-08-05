# Networking para AWS

from bastion.component import Component
from bastion.networking.base import Networking
from bastion.networking.network.aws import AWSNetwork
from bastion.networking.gateway.aws import AWSGateway


class AWSNetworking (Networking, Component):

    def get_cloud_driver(self):
        return self.driver.get_cloud_driver()

    def create_network(self, cidr, name=None, dns=False):

        print "Creando Red Virtual EC2 ..."

        cloud_driver = self.get_cloud_driver()
        network = cloud_driver.ex_create_network(name=name, cidr_block=cidr)
        n = AWSNetwork(network.id,
                       network.name,
                       network.cidr_block,
                       self)

        # TODO: Improve this! (Provisioning)
        gateway_name = "%s-gateway" % name
        gateway = self.create_gateway(gateway_name)
        n.attach_gateway(gateway)
        route_table = n.list_route_tables()[0]
        route_table.create_route('0.0.0.0/0', gateway)
        security_group = n.list_security_groups()[0]
        security_group.allow_inbound_traffic(22)

        # Create the VPN Subnet
        n.create_vpn_subnet()

        # Create the DNS Subnet
        if dns:
            n.create_dns_subnet()

        # EnableDnsHostnames
        cloud_driver.ex_network_enable_dns_hostnames(n)

        print "Red Virtual EC2 creada con nombre='{0}', cidr='{1}'.".format(
            network.name,
            cidr)

        return n

    def get_network(self, network_id):
        cloud_driver = self.get_cloud_driver()
        networks = cloud_driver.ex_list_networks(network_ids=[network_id])

        if networks:
            return AWSNetwork(networks[0].id,
                              networks[0].name,
                              networks[0].cidr_block,
                              self)

        return None

    def list_networks(self):
        cloud_driver = self.get_cloud_driver()
        networks = cloud_driver.ex_list_networks()
        result = list()
        for n in networks:
            result.append(AWSNetwork(n.id,
                                     n.name,
                                     n.cidr_block,
                                     self))
        return result

    def create_gateway(self, name=None):
        cloud_driver = self.get_cloud_driver()
        cloud_gateway = cloud_driver.ex_create_internet_gateway(name)
        return AWSGateway(cloud_gateway.id, name, self)