# Clases base


class SecurityGroup:

    def __init__(self, id, name, network):
        self.id = id
        self.name = name
        self.network = network

    def allow_inbound_traffic(self, port):
        raise NotImplementedError('allow_inbound_traffic not implemented for this driver')

    def delete(self):
        raise NotImplementedError('delete not implemented for this driver')
