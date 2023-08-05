# Compute Driver para AWS
import os

from libcloud.compute.base import NodeAuthSSHKey
from bastion.component import Component
from bastion.compute.base import BaseCompute
from bastion.compute.common.image import Image
from bastion.compute.common.size import Size
from bastion.compute.vm.aws import AWSVirtualMachine
from bastion.networking.network_interface.aws import AWSNetworkInterface


class AWSBaseCompute(BaseCompute, Component):
    def get_cloud_driver(self):
        return self.driver.get_cloud_driver()

    def create_vm(self, name=None, image_id=None, size_id=None, subnet=None):

        print "Creando Maquina Virtual EC2 ..."

        cloud_driver = self.get_cloud_driver()

        if image_id is None:
            image_id = self.driver.prop.image_id

        if size_id is None:
            size_id = self.driver.prop.size_id

        if name is None:
            name = 'bas7ion-node'

        if subnet is None:
            network_name = "%s-network" % name
            network_cidr = "10.0.0.0/16"
            subnet_name = "%s-subnet" % name
            subnet_cidr = "10.0.0.0/24"
            net = self.driver.networking.create_network(name=network_name,
                                                        cidr=network_cidr)
            subnet = net.create_subnet(name=subnet_name,
                                       cidr=subnet_cidr)

        image = cloud_driver.get_image(image_id)

        sizes = cloud_driver.list_sizes()
        size = [s for s in sizes if s.id == size_id][0]

        img = Image(image.id,
                    image.name)

        sz = Size(size.id,
                  size.name,
                  size.ram,
                  size.disk,
                  size.bandwidth,
                  size.price)

        key_file_path = os.path.expanduser(self.driver.cred.public_key_path)

        with open(key_file_path, 'r') as fp:
            key_material = fp.read()

        auth = NodeAuthSSHKey(key_material)

        vm = cloud_driver.create_node(name=name,
                                      image=image,
                                      size=size,
                                      ex_subnet=subnet,
                                      ex_assign_public_ip=True,
                                      auth=auth)

        nodes_ips_tuples = cloud_driver.wait_until_running([vm],
                                                           wait_period=4,
                                                           timeout=600,
                                                           ssh_interface='public_ips',
                                                           force_ipv4=True)

        node_ip_tuple = nodes_ips_tuples[0]

        primary_network_interface = vm.extra['network_interfaces'][0]
        private_ip = primary_network_interface.extra['private_ips'][0][
            'private_ip']
        primary_network_interface = AWSNetworkInterface(id=primary_network_interface.id,
                                                        name=primary_network_interface.name,
                                                        private_ip=private_ip, subnet=None)
        aws_vm = AWSVirtualMachine(vm.id, vm.name, sz, img, self, primary_network_interface, subnet)
        aws_vm.public_ips.append(node_ip_tuple[1][0])
        aws_vm.private_ips.append(private_ip)

        print "Maquina Virtual EC2 creada con nombre='{0}', ip_privada='{1}', ip_publica='{2}'.".format(
            aws_vm.name,
            aws_vm.private_ips[0],
            aws_vm.public_ips[0])

        return aws_vm

    def list_vms(self):
        cloud_driver = self.get_cloud_driver()

        nodes = cloud_driver.list_nodes()
        result = list()
        for node in nodes:
            primary_network_interface = node.extra['network_interfaces'][0]
            private_ip = primary_network_interface.extra['private_ips'][0]['private_ip']
            primary_network_interface = AWSNetworkInterface(id=primary_network_interface.id,
                                                            name=primary_network_interface.name,
                                                            private_ip=private_ip, subnet=None)
            image = self.get_image(node.extra["image_id"])
            size = self.get_size(node.extra["instance_type"])
            result.append(AWSVirtualMachine(node.id,
                                            node.name,
                                            size,
                                            image,
                                            self,
                                            primary_network_interface))
        return result

    def list_images(self):
        cloud_driver = self.get_cloud_driver()

        images = cloud_driver.list_images()
        result = list()
        for image in images:
            result.append(Image(image.id,
                                image.name))
        return result

    def get_image(self, image_id):
        cloud_driver = self.get_cloud_driver()

        image = cloud_driver.list_images(ex_image_ids=[image_id])[0]
        return Image(image.id,
                     image.name)

    def list_sizes(self):
        cloud_driver = self.get_cloud_driver()

        sizes = cloud_driver.list_sizes()
        result = list()
        for size in sizes:
            result.append(Size(size.id,
                               size.name,
                               size.ram,
                               size.disk,
                               size.bandwidth,
                               size.price))
        return result

    def get_size(self, size_id):
        cloud_driver = self.get_cloud_driver()

        sizes = cloud_driver.list_sizes()
        size = [s for s in sizes if s.id == size_id][0]
        return Size(size.id,
                    size.name,
                    size.ram,
                    size.disk,
                    size.bandwidth,
                    size.price)
