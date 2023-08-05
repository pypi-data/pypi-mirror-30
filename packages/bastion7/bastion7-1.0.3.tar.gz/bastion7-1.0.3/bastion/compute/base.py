# Clases base


class BaseCompute:

    def __init__(self, driver):
        self.driver = driver

    def create_vm(self, name=None, image_id=None, size_id=None, subnet=None):
        """
        :param name:   String with a name for this new node
        :type name:   ``str``

        :param size_id:   The size identifier of resources allocated to this node.
        :type size_id:   ``str``

        :param image_id:   OS image identifier to boot on node.
        :type image_id:   ``str``

        :param subnet:   The subnet for this new node.
        :type subnet:   ``Subnet``

        """
        raise NotImplementedError(
            'create_vm not implemented for this driver')

    def list_vms(self):
        raise NotImplementedError(
            'list_vms not implemented for this driver')

    def list_images(self):
        raise NotImplementedError(
            'list_images not implemented for this driver')

    def get_image(self, image_id):
        raise NotImplementedError(
            'get_image not implemented for this driver')

    def list_sizes(self):
        raise NotImplementedError(
            'list_sizes not implemented for this driver')

    def get_size(self, size_id):
        raise NotImplementedError(
            'get_size not implemented for this driver')
