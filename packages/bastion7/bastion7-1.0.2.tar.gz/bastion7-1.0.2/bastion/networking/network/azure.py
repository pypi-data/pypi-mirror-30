# Network para Azure

import json
import ipaddress

from bastion.networking.network.base import Network
from bastion.networking.subnet.azure import AzureSubnet
from bastion.networking.private_dns.azure import AzurePrivateDns
from bastion.component import Component
from libcloud.compute.drivers.azure_arm import AzureNetwork


class AzureNetwork(Network, Component):

    dns_subnet = None

    def get_cloud_driver(self):
        return self.networking.get_cloud_driver()

    def list_route_tables(self):
        raise NotImplementedError('list_route_tables not implemented for this driver')

    def list_security_groups(self):
        raise NotImplementedError ('list_security_groups not implemented for this driver')

    def create_private_dns(self):
        cloud_driver = self.get_cloud_driver()
        # Create Private DNS Server
        dns_server = self.networking.driver.baseCompute.create_vm(name=self.name+"-ns1",
                                                                  image_id=self.networking.driver.prop.dns_image_id,
                                                                  subnet=self.dns_subnet)

        cloud_driver.ex_update_network(cidr_block=self.cidr,
                                       name=self.name,
                                       resource_group=self.networking.driver.prop.resource_group,
                                       location_id=self.networking.driver.prop.location_id,
                                       dns_server=dns_server.private_ips[0])

        self.private_dns = AzurePrivateDns(dns_server, self)
        return self.private_dns

    def create_subnet(self, cidr, name=None):

        print "Creando Subred en Red Virtual Azure {} ...".format(self.name)

        cloud_driver = self.get_cloud_driver()

        subnet = cloud_driver.ex_create_subnet(resource_group=self.networking.driver.prop.resource_group,
                                               cidr_block=cidr,
                                               name=name,
                                               network_name=self.name)

        azure_subnet = AzureSubnet(subnet.id,
                                   subnet.name,
                                   cidr,
                                   self)

        print "Subred creada con nombre='{0}', cidr='{1}'.".format(
            subnet.name,
            cidr)

        return azure_subnet

    def create_dns_subnet(self):
        # TODO: Create a file with the harcoded data
        network_mask_length = ipaddress.ip_network(self.cidr).prefixlen
        subnet_ip = ipaddress.ip_network(self.cidr).network_address + (2**(28-network_mask_length) - 2) * 2**(32-28)
        subnet = ipaddress.ip_network((subnet_ip, 28))
        dns_subnet_name = "%s-dns-subnet" % self.name
        self.dns_subnet = self.create_subnet(str(subnet), dns_subnet_name)
        self.create_private_dns()

    def create_vpn_subnet(self):
        # TODO: Create a file with the harcoded data
        network_mask_length = ipaddress.ip_network(self.cidr).prefixlen
        subnet_ip = ipaddress.ip_network(self.cidr).network_address + (2**(28-network_mask_length) - 1) * 2**(32-28)
        subnet = ipaddress.ip_network((subnet_ip, 28))

        self.vpn_subnet = self.create_subnet(str(subnet), "GatewaySubnet")

    def get_vpn_public_ip(self):
        return self.vpn_gateway.public_ip

    def prepare_vpn_connection(self):
        cloud_driver = self.get_cloud_driver()

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.networking.driver.prop.location_id][0]

        vpn_vng_public_ip_name = "%s-vpn-vng-public-ip" % self.name
        self.vpn_gateway_ip = cloud_driver.ex_create_public_ip(name=vpn_vng_public_ip_name,
                                                               resource_group=self.networking.driver.prop.resource_group,
                                                               location=location)

        vpn_vng_name = "%s-vpn-vng" % self.name
        self.vpn_gateway\
            = cloud_driver.ex_create_virtual_network_gateway(name=vpn_vng_name, subnet=self.vpn_subnet,
                                                             resource_group=self.networking.driver.prop.resource_group,
                                                             location=location, public_ip=self.vpn_gateway_ip)

    def get_vpn_connection_public_ip(self):
        cloud_driver = self.get_cloud_driver()

        self.vpn_gateway_ip = cloud_driver.wait_until_public_ip_running(self.vpn_gateway_ip.id,
                                                                        wait_period=30, timeout=3600)

        return self.vpn_gateway_ip.extra.get("ipAddress")

    def connect_to_vpn_network(self, cidr, public_ip, shared_key):
        cloud_driver = self.get_cloud_driver()

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.networking.driver.prop.location_id][0]

        vpn_lng_name = "%s-vpn-lng" % self.name
        vpn_lng = cloud_driver.ex_create_local_network_gateway(name=vpn_lng_name, address_space=cidr,
                                                               gateway_ip_address=public_ip,
                                                               resource_group=self.networking.driver.prop.resource_group,
                                                               location=location)

        vpn_conn_name = "%s-vpn-conn" % self.name
        cloud_driver.ex_create_virtual_network_gateway_connection(name=vpn_conn_name, shared_key=shared_key,
                                                                  resource_group=self.networking.driver.prop.resource_group,
                                                                  location=location, local_network_gateway=vpn_lng,
                                                                  virtual_network_gateway=self.vpn_gateway)

    def start_vpn_connection(self):
        pass

    def list_subnets(self):
        result = []

        cloud_driver = self.get_cloud_driver()

        n = AzureNetwork(self.id,
                         None,
                         None,
                         None)

        subnets = cloud_driver.ex_list_subnets(network=n)

        for subnet in subnets:
            result.append(AzureSubnet(subnet.id,
                                      subnet.name,
                                      subnet.extra["addressPrefix"],
                                      self))

        return result

    def delete(self):
        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_delete_network(resource_group=self.driver.prop.res.resource_group,
                                       name=self.name)

    def attach_gateway(self, gateway):
        raise NotImplementedError('attach_gateway not implemented for this driver')

    def refresh_dns_entries(self):
        self.private_dns.refresh_entries()
