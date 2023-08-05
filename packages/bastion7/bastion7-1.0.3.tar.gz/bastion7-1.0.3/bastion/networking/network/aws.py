# Network para AWS
import ipaddress
import json
import os
from libcloud.compute.drivers.ec2 import VPCInternetGateway, EC2Network

from bastion.component import Component
from bastion.libcloudbastion.ec2 import EC2VPNGateway
from bastion.networking.network.base import Network
from bastion.networking.private_dns.aws import AWSPrivateDns
from bastion.networking.route_table.aws import AWSRouteTable
from bastion.networking.security_group.aws import AWSSecurityGroup
from bastion.networking.subnet.aws import AWSSubnet


class AWSNetwork(Network, Component):

    vpn_gateway_private_ip = None

    def get_cloud_driver(self):
        return self.networking.get_cloud_driver()

    def list_route_tables(self):
        cloud_driver = self.get_cloud_driver()
        all_route_tables = cloud_driver.ex_list_route_tables()
        vpc_route_tables = []

        for lib_route_table in all_route_tables:
            if lib_route_table.extra['vpc_id'] == self.id:
                route_table = AWSRouteTable(lib_route_table.id, lib_route_table.name, lib_route_table.routes,
                                            lib_route_table.subnet_associations,
                                            lib_route_table.propagating_gateway_ids,
                                            self, extra=lib_route_table.extra)
                vpc_route_tables.append(route_table)

        return vpc_route_tables

    def list_security_groups(self):
        cloud_driver = self.get_cloud_driver()
        all_security_groups = cloud_driver.ex_get_security_groups()
        vpc_security_groups = []

        for lib_security_group in all_security_groups:
            if lib_security_group.extra['vpc_id'] == self.id:
                vpc_security_groups.append(AWSSecurityGroup(lib_security_group.id,
                                                            lib_security_group.name,
                                                            self))
        return vpc_security_groups

    def create_private_dns(self, domain):
        # Create Private Zone
        dns_server = self.networking.driver.dns_driver.ex_create_private_zone(domain=domain,
                                                                              vpc_id=self.id,
                                                                              region=self.networking.driver.cred.region)
        self.private_dns = AWSPrivateDns(domain, dns_server, self)
        return self.private_dns

    def create_subnet(self, cidr, name=None):

        print "Creando Subred en Red Virtual EC2 {} ...".format(self.name)

        cloud_driver = self.get_cloud_driver()

        availability_zones = cloud_driver.ex_list_availability_zones()
        zone = [az for az in availability_zones][0]

        subnet = cloud_driver.ex_create_subnet(vpc_id=self.id,
                                               name=name,
                                               cidr_block=cidr,
                                               availability_zone=zone.name)

        print "Subred creada con nombre='{0}', cidr='{1}'.".format(
            subnet.name,
            cidr)

        return AWSSubnet(subnet.id,
                         subnet.name,
                         cidr,
                         self)

    def create_vpn_subnet(self):
        network_mask_length = ipaddress.ip_network(self.cidr).prefixlen
        subnet_ip = ipaddress.ip_network(self.cidr).network_address + (2 ** (28 - network_mask_length) - 1) * 2 ** (
            32 - 28)
        subnet = ipaddress.ip_network((subnet_ip, 28))
        vpn_subnet_name = "%s-vpn-subnet" % self.name
        self.vpn_subnet = self.create_subnet(str(subnet), vpn_subnet_name)

    def prepare_vpn_connection(self):
        # Create VPN Terminal VM
        self.vpn_gateway = self.networking.driver.baseCompute.create_vm(name=self.name + "-vpn",
                                                                        image_id=self.networking.driver.prop.vpn_image_id,
                                                                        subnet=self.vpn_subnet)
        self.vpn_gateway.set_source_dest_check(False)
        self.vpn_gateway_ip = self.vpn_gateway.public_ips[0]
        self.vpn_gateway_private_ip = self.vpn_gateway.private_ips[0]

    def get_vpn_connection_public_ip(self):
        return self.vpn_gateway_ip

    def connect_to_vpn_network(self, cidr, public_ip, shared_key):

        vpn_parameters =\
            {
                'local_ip': self.vpn_gateway_private_ip,
                'local_public_ip': self.vpn_gateway_ip,
                'local_subnet': self.cidr,
                'remote_public_ip': public_ip,
                'remote_subnet': cidr,
                'psk': shared_key
            }

        route_table = self.list_route_tables()[0]
        route_table.create_route(cidr, internet_gateway=None, network_interface=self.vpn_gateway.primary_network_interface)

        cloud_driver = self.get_cloud_driver()
        default_security_group = self.list_security_groups()[0]

        cloud_driver.ex_authorize_security_group_by_id(default_security_group.id, 0, 65535, public_ip + '/32',
                                                       protocol='-1')

        this_file_path = os.path.abspath(os.path.dirname(__file__))
        strongswan_playbook_path = os.path.join(this_file_path, "../../playbooks/torian-strongswan.yml")

        self.vpn_gateway.provision(playbook_path=strongswan_playbook_path,
                                   parameters=json.dumps(vpn_parameters),
                                   user='ubuntu')

    def start_vpn_connection(self):
        this_file_path = os.path.abspath(os.path.dirname(__file__))
        ipsec_restart_path = os.path.join(this_file_path, "../../playbooks/ipsec-restart.yml")

        self.vpn_gateway.provision(playbook_path=ipsec_restart_path,
                                   user='ubuntu')

    def create_dns_subnet(self):
        network_mask_length = ipaddress.ip_network(self.cidr).prefixlen
        subnet_ip = ipaddress.ip_network(self.cidr).network_address + (2 ** (28 - network_mask_length) - 2) * 2 ** (
            32 - 28)
        subnet = ipaddress.ip_network((subnet_ip, 28))
        dns_subnet_name = "%s-dns-subnet" % self.name
        self.dns_subnet = self.create_subnet(str(subnet), dns_subnet_name)

    def list_subnets(self):
        cloud_driver = self.get_cloud_driver()
        all_subnets = cloud_driver.ex_list_subnets()
        vpc_subnets = []

        for lib_subnet in all_subnets:
            if lib_subnet.extra['vpc_id'] == self.id:
                vpc_subnet = AWSSubnet(lib_subnet.id,
                                       lib_subnet.name,
                                       lib_subnet.extra['cidr_block'],
                                       self)
                vpc_subnets.append(vpc_subnet)

        return vpc_subnets

    def delete(self):
        cloud_driver = self.get_cloud_driver()
        networks = cloud_driver.ex_list_networks(network_ids=[self.id])
        network = [n for n in networks][0]
        cloud_driver.ex_delete_network(network)

    def attach_gateway(self, gateway):
        cloud_driver = self.get_cloud_driver()
        cloud_gateway = VPCInternetGateway(id=gateway.id, name=None, vpc_id=None, state=None, driver=None)
        cloud_network = EC2Network(id=self.id, name=None, cidr_block=None)
        cloud_driver.ex_attach_internet_gateway(gateway=cloud_gateway, network=cloud_network)

    def attach_vpn_gateway(self, vpn_gateway):
        cloud_driver = self.get_cloud_driver()
        cloud_vpn_gateway = EC2VPNGateway(id=vpn_gateway.id, name=None, state=None)
        cloud_network = EC2Network(id=self.id, name=None, cidr_block=None)
        cloud_driver.ex_attach_vpn_gateway(vpn_gateway=cloud_vpn_gateway, network=cloud_network)
