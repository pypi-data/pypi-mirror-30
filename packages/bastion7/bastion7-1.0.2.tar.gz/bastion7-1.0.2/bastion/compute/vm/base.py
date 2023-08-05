# Clases base


class VirtualMachine:

    def __init__(self, id, name, size, image, compute, primary_network_interface=None, subnet=None):
        self.id = id
        self.name = name
        self.size = size
        self.image = image
        self.compute = compute
        self.public_ips = []
        self.private_ips = []
        self.primary_network_interface = primary_network_interface
        self.subnet = subnet

    def start(self):
        raise NotImplementedError(
            'start not implemented for this driver')

    def stop(self):
        raise NotImplementedError(
            'stop not implemented for this driver')

    def restart(self):
        raise NotImplementedError(
            'restart not implemented for this driver')

    def attach_nic(self, nic):
        raise NotImplementedError (
            'attach_nic not implemented for this driver')

    def provision(self, playbook_path, additional_options=[], parameters=None, user=None):
        raise NotImplementedError(
            'provision not implemented for this driver')

    def delete(self):
        raise NotImplementedError(
            'delete not implemented for this driver')

    def add_hostname(self, hostname, domain=None):
        raise NotImplementedError(
            'add_hostname not implemented for this driver')
