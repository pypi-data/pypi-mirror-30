

class PrivateDns:

    domain = None
    dns_server = None
    network = None

    def __init__(self, dns_server, network):
        self.dns_server = dns_server
        self.network = network

    def add_hostname(self, hostname, vm):
        raise NotImplementedError('add_hostname not implemented for this driver')

