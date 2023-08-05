# Clases base


class NetworkInterface:

    def __init__(self, id, name, private_ip, subnet):
        self.id = id
        self.name = name
        self.private_ip = private_ip
        self.subnet = subnet

    def delete(self):
            raise NotImplementedError('delete not implemented for this driver')