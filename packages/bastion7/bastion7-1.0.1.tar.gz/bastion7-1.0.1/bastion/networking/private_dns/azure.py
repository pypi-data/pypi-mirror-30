import json
import os

from bastion.networking.private_dns.base import PrivateDns
from bastion.component import Component


class AzurePrivateDns(PrivateDns, Component):

    hostnames = []

    def __init__(self, dns_server, network):
        super(AzurePrivateDns, self).__init__(dns_server, network)
        hostname_element = {
            'name': 'ns1',
            'ip': dns_server.private_ips[0]
        }
        self.hostnames.append(hostname_element)

    def get_cloud_driver(self):
        return self.network.get_cloud_driver()

    def add_hostname(self, hostname, vm):

        hostname_element = {
            'name': hostname,
            'ip': vm.private_ips[0]
        }

        self.hostnames.append(hostname_element)

        dns_parameters = \
            {
                'dns_server_ip': self.dns_server.private_ips[0],
                'domain': self.domain,
                'hostnames': self.hostnames,
            }

        this_file_path = os.path.abspath(os.path.dirname(__file__))
        bind_playbook_path = os.path.join(this_file_path, "../../playbooks/bertvv-bind.yml")

        self.dns_server.provision(playbook_path=bind_playbook_path,
                                  parameters=json.dumps(dns_parameters))
