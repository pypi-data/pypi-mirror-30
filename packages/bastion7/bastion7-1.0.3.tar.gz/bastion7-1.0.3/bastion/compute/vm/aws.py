# Virtual Machine para AWS
import subprocess

from libcloud.compute.drivers.ec2 import EC2NetworkInterface
from bastion.compute.vm.base import VirtualMachine
from libcloud.compute.base import Node
from bastion.component import Component


class AWSVirtualMachine(VirtualMachine, Component):

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

        i = EC2NetworkInterface(nic.id,
                                nic.name,
                                None)

        n = Node(self.id,
                 self.name,
                 None,
                 [],
                 [],
                 None)

        nodes = cloud_driver.list_nodes(ex_node_ids=[self.id])
        cloud_driver.wait_until_running(nodes=nodes)

        device_index = 0
        nics = nodes[0].extra["network_interfaces"]
        index_list = list()
        for n in nics:
            if n.extra["attachment"]:
                index_list.append(n.extra["attachment"]["device_index"])
        if len(index_list) > 0:
            device_index = max(index_list) + 1

        attachment_id = cloud_driver.ex_attach_network_interface_to_node(network_interface=i,
                                                                         node=self,
                                                                         device_index=device_index)

        print attachment_id

    def provision(self, playbook_path, additional_options=[], parameters=None, user='ec2-user'):

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
        return cloud_driver.destroy_node(vm)

    def set_source_dest_check(self, enabled):
        cloud_driver = self.get_cloud_driver()

        n = Node(self.id,
                 self.name,
                 None,
                 [],
                 [],
                 None)
        cloud_driver.ex_modify_instance_attribute(n, {'SourceDestCheck.Value': enabled})

    def add_hostname(self, hostname, domain=None):
        private_dns = self.subnet.network.private_dns
        if private_dns is None:
            if domain is None:
                raise NotImplementedError(
                    'domain is required')
            private_dns = self.subnet.network.create_private_dns(domain)
        if domain is not None and domain != private_dns.domain:
            raise NotImplementedError(
                'domain must be the same default domain of the dns created')
        private_dns.add_hostname(hostname, self)
