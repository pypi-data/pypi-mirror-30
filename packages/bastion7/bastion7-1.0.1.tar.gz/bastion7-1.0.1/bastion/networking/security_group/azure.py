# Security Group para Amazon


from bastion.networking.security_group.base import SecurityGroup
from bastion.component import Component


class AmazonSecurityGroup (SecurityGroup, Component):

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def allow_inbound_traffic(self, port):
        raise NotImplementedError('allow_inbound_traffic not implemented for this driver')

    def delete(self):
        raise NotImplementedError('delete not implemented for this driver')
