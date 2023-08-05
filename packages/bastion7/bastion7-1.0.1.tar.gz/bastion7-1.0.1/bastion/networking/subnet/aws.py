# Subnet para AWS

from bastion.networking.network_interface.aws import AWSNetworkInterface
from bastion.networking.subnet.base import Subnet
from bastion.component import Component


class AWSSubnet (Subnet, Component):

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def create_nic(self, private_ip, name=None):

        cloud_driver = self.get_cloud_driver()

        subnets = cloud_driver.ex_list_subnets(subnet_ids=[self.id])
        subnet = [s for s in subnets][0]
        nic = cloud_driver.ex_create_network_interface(subnet,
                                                       name=name,
                                                       private_ip_address=private_ip)
        return AWSNetworkInterface(nic.id,
                                   nic.name,
                                   private_ip,
                                   self)

    def list_nics(self):
        cloud_driver = self.get_cloud_driver()
        all_nics = cloud_driver.ex_list_network_interfaces()
        subnet_nics = []
        for lib_nic in all_nics:
            if lib_nic.extra['subnet_id'] == self.id:
                private_ip = lib_nic.extra['private_ips'][0]['private_ip']
                subnet_nic = AWSNetworkInterface(lib_nic.id,
                                                 lib_nic.name,
                                                 private_ip,
                                                 self)
                subnet_nics.append(subnet_nic)
        return subnet_nics

    def delete(self):
        cloud_driver = self.get_cloud_driver ()
        subnets = cloud_driver.ex_list_subnets(subnet_ids=[self.id])
        subnet = [s for s in subnets][0]
        cloud_driver.ex_delete_subnet(subnet)