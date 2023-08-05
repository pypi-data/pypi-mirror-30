# NetworkInterface para AWS

from bastion.networking.network_interface.base import NetworkInterface
from libcloud.compute.drivers.ec2 import EC2NetworkInterface
from bastion.component import Component


class AWSNetworkInterface (NetworkInterface, Component):

    def get_cloud_driver(self):
        return self.subnet.get_cloud_driver()

    def delete(self):
        cloud_driver = self.get_cloud_driver()
        cloud_nic = EC2NetworkInterface(id=self.id, name=None, state=None, extra=None)
        cloud_driver.ex_delete_network_interface(cloud_nic)
