# Clases base


class Subnet:

    def __init__(self, id, name, cidr, network):
        self.id = id
        self.name = name
        self.cidr = unicode(cidr)
        self.network = network

    def create_nic(self, private_ip, name=None):
        raise NotImplementedError('create_nic not implemented for this driver')

    def list_nics(self):
            raise NotImplementedError('list_nics not implemented for this driver')

    def delete(self):
            raise NotImplementedError('delete not implemented for this driver')