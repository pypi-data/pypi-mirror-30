# NetworkInterface para AWS

from bastion.networking.network_interface.base import NetworkInterface
from bastion.component import Component


class AzureNetworkInterface (NetworkInterface, Component):

    def get_cloud_driver(self):
        return self.subnet.get_cloud_driver()

    def delete(self):
        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_delete_network_interface(resource_group=self.driver.prop.res.resource_group,
                                                 name=self.name)
