# Compute Driver para Azure
import os

from bastion.component import Component
from bastion.compute.base import BaseCompute
from bastion.compute.common.size import Size
from bastion.compute.common.image import Image
from libcloud.compute.base import NodeAuthSSHKey
from bastion.compute.vm.azure import AzureVirtualMachine


class AzureBaseCompute(BaseCompute, Component):

    def get_cloud_driver(self):
        return self.driver.get_cloud_driver()

    def create_vm(self, name=None, image_id=None, size_id=None, subnet=None, add_public_ip=True):

        print "Creando Maquina Virtual Azure ..."

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

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.driver.prop.location_id][0]

        if add_public_ip is True:
            public_ip_name = "%s-public-ip" % name
            public_ip = cloud_driver.ex_create_public_ip(public_ip_name,
                                                         resource_group=self.driver.prop.resource_group,
                                                         location=location)
        else:
            public_ip = None

        nic_name = "%s-nic" % name
        nic = cloud_driver.ex_create_network_interface(name=nic_name,
                                                       subnet=subnet,
                                                       resource_group=self.driver.prop.resource_group,
                                                       location=location,
                                                       public_ip=public_ip)

        sizes = cloud_driver.list_sizes(location=location)
        size = [s for s in sizes if s.id == size_id][0]

        image = cloud_driver.get_image(image_id=image_id,
                                       location=location)

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
                                      size=size,
                                      image=image,
                                      auth=auth,
                                      location=location,
                                      ex_resource_group=self.driver.prop.resource_group,
                                      ex_storage_account=self.driver.prop.storage_account,
                                      ex_nic=nic)

        nodes_ips_tuples = cloud_driver.wait_until_running([vm],
                                                           wait_period=5,
                                                           timeout=1000,
                                                           ssh_interface='public_ips',
                                                           force_ipv4=True,
                                                           ex_list_nodes_kwargs={"ex_resource_group": self.driver.prop.resource_group})

        node_ip_tuple = nodes_ips_tuples[0]

        azure_vm = AzureVirtualMachine(vm.id,
                                       vm.name,
                                       sz,
                                       img,
                                       self, subnet=subnet)
        azure_vm.public_ips.append(node_ip_tuple[1][0])
        azure_vm.private_ips.append(node_ip_tuple[0].private_ips[0])

        print "Maquina Virtual Azure creada con nombre='{0}', ip_privada='{1}', ip_publica='{2}'.".format(
            azure_vm.name,
            azure_vm.private_ips[0],
            azure_vm.public_ips[0])

        return azure_vm

    def list_vms(self):
        cloud_driver = self.get_cloud_driver()

        nodes = cloud_driver.list_nodes()
        result = list()
        for node in nodes:
            size = self.get_size(node.extra["properties"]["hardwareProfile"]["vmSize"])
            image_ref = node.extra["properties"]["storageProfile"]["imageReference"]
            publisher = image_ref["publisher"]
            offer = image_ref["offer"]
            sku = image_ref["sku"]
            version = image_ref["version"]
            image_id = publisher + ":" + offer + ":" + sku + ":" + version
            image = self.get_image(image_id)
            result.append(AzureVirtualMachine(node.id,
                                              node.name,
                                              size,
                                              image,
                                              self))
        return result

    def list_images(self):
        cloud_driver = self.get_cloud_driver()

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.driver.prop.location_id][0]

        images = cloud_driver.list_images(location=location)
        result = list()
        for image in images:
            result.append(Image(image.id,
                                image.name))
        return result

    def get_image(self, image_id):
        cloud_driver = self.get_cloud_driver()

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.driver.prop.location_id][0]

        image = cloud_driver.get_image(image_id=image_id,
                                       location=location)

        return Image(image.id,
                     image.name)

    def list_sizes(self):
        cloud_driver = self.get_cloud_driver()

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.driver.prop.location_id][0]

        sizes = cloud_driver.list_sizes(location=location)
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

        locations = cloud_driver.list_locations()
        location = [l for l in locations if l.name == self.driver.prop.location_id][0]

        sizes = cloud_driver.list_sizes(location=location)
        size = [s for s in sizes if s.id == size_id][0]

        return Size(size.id,
                    size.name,
                    size.ram,
                    size.disk,
                    size.bandwidth,
                    size.price)
