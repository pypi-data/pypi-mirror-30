import sys

from libcloud.compute.drivers.ec2 import EC2NodeDriver as LibCloudEC2NodeDriver
from libcloud.compute.drivers.ec2 import NAMESPACE
from libcloud.utils.xml import fixxpath, findtext


class EC2VPNGateway(object):
    """
    Class which stores information about VPN Gateways.

    Note: This class is VPC specific.
    """

    def __init__(self, id, name, state, extra=None):
        self.id = id
        self.name = name
        self.state = state
        self.extra = extra or {}

    def __repr__(self):
        return '<VPNGateway: id=%s>' % self.id


class EC2NodeDriver(LibCloudEC2NodeDriver):

    def ex_create_vpn_gateway(self, name=None):

        params = {'Action': 'CreateVpnGateway', 'Type': 'ipsec.1'}

        resp = self.connection.request(self.path, params=params).object

        element = resp.findall(fixxpath(xpath='vpnGateway',
                                        namespace=NAMESPACE))

        gateway = self._to_vpn_gateway(element[0], name)

        if name and self.ex_create_tags(gateway, {'Name': name}):
            gateway.extra['tags']['Name'] = name

        return gateway

    def _to_vpn_gateways(self, object, xpath):
        return [self._to_vpn_gateway(el)
                for el in object.findall(fixxpath(xpath=xpath,
                                                  namespace=NAMESPACE))]

    def _to_vpn_gateway(self, element, name=None):
        id = findtext(element=element,
                      xpath='vpnGatewayId',
                      namespace=NAMESPACE)

        state = findtext(element=element,
                         xpath='attachmentSet/item/state',
                         namespace=NAMESPACE)

        # If there's no attachment state, let's
        # set it to available
        if not state:
            state = 'available'

        # Get our tags
        tags = self._get_resource_tags(element)

        # If name was not passed into the method then
        # fall back then use the gateway id
        name = name if name else tags.get('Name', id)

        return EC2VPNGateway(id=id, name=name,
                             state=state,
                             extra={'tags': tags})

    def ex_attach_vpn_gateway(self, vpn_gateway, network):
        params = {'Action': 'AttachVpnGateway',
                  'VpnGatewayId': vpn_gateway.id,
                  'VpcId': network.id}

        res = self.connection.request(self.path, params=params).object

        return self._get_boolean(res)

    def ex_network_enable_dns_hostnames(self, network):
        params = {
            'Action': 'ModifyVpcAttribute',
            'VpcId': network.id,
            'EnableDnsHostnames.Value': True}
        res = self.connection.request(self.path, params=params).object
        return self._get_boolean(res)

    def ex_authorize_security_group_by_id(self, group_id, from_port, to_port, cidr_ip, protocol='tcp'):
        params = {'Action': 'AuthorizeSecurityGroupIngress',
                  'GroupId': group_id,
                  'IpProtocol': protocol,
                  'FromPort': str(from_port),
                  'ToPort': str(to_port),
                  'CidrIp': cidr_ip}
        try:
            res = self.connection.request(
                self.path, params=params.copy()).object
            return self._get_boolean(res)
        except Exception:
            e = sys.exc_info()[1]
            if e.args[0].find('InvalidPermission.Duplicate') == -1:
                raise e
