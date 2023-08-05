# Virtual Machine para Azure
import subprocess

from bastion.compute.vm.base import VirtualMachine


class AzureVirtualMachine(VirtualMachine):

    def get_cloud_driver(self):
        return self.compute.get_cloud_driver()

    def start(self):
        cloud_driver = self.get_cloud_driver()

        vm = cloud_driver.list_nodes(ex_node_ids=[self.id])[0]
        cloud_driver.ex_start_node(vm)

    def stop(self):
        cloud_driver = self.get_cloud_driver()

        vm = cloud_driver.list_nodes(ex_node_ids=[self.id])[0]
        cloud_driver.ex_stop_node(vm)

    def restart(self):
        cloud_driver = self.get_cloud_driver()

        vm = cloud_driver.list_nodes(ex_node_ids=[self.id])[0]
        cloud_driver.reboot_node(vm)

    def attach_nic(self, nic):

        cloud_driver = self.get_cloud_driver()
        cloud_driver.ex_attach_network_interface(self.name, nic.id, self.compute.driver.prop.resource_group, self.compute.driver.prop.location_id)

    def provision(self, playbook_path, additional_options=[], parameters=None, user='azureuser'):

        if parameters is None:
            cmd = ['ansible-playbook', '-i', self.public_ips[0] + ',', playbook_path,
                   '--private-key=' + self.compute.driver.cred.private_key_path,
                   '-u', user]
        else:
            cmd = ['ansible-playbook', '-i', self.public_ips[0] + ',', playbook_path,
                   '-e', parameters,
                   '--private-key=' + self.compute.driver.cred.private_key_path,
                   '-u', user]

        cmd.extend(additional_options)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in iter(p.stdout.readline, b''):
            print(">>> " + line.rstrip())

    def delete(self):
        cloud_driver = self.get_cloud_driver()

        vm = cloud_driver.list_nodes(ex_node_ids=[self.id])[0]
        cloud_driver.destroy_node(vm)

    def add_hostname(self, hostname, domain=None):
        private_dns = self.subnet.network.private_dns
        if domain is None and private_dns.domain is None:
            raise NotImplementedError(
                'domain is required')
        if domain is not None and private_dns.domain is not None and domain != private_dns.domain:
            raise NotImplementedError(
                'domain must be the same default domain of the dns created')
        private_dns.domain = domain
        private_dns.add_hostname(hostname, self)
