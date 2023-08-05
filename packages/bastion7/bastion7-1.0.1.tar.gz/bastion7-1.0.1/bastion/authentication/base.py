# Clases base
import os
from bastion.provider_types import Providers


class BaseAuthDriver:
    _token = None
    _project_id = None

    def __init__(self, token, project_id):
        self._token = token
        self._project_id = project_id

    def get_provider_info(self, path):
        raise NotImplementedError(
            'get_providers_info not implemented for this driver')

    def get_providers_info(self, path):
        raise NotImplementedError(
            'get_providers_info not implemented for this driver')


class ProviderInfo:
    type = None
    cred = None
    prop = None

    def __init__(self):
        pass


class AWSProviderCred:

    access_key = None
    secret_key = None
    region = None
    public_key_path = None
    private_key_path = None

    def __init__(self, secret_aws):
        self.access_key = secret_aws['access_key']
        self.secret_key = secret_aws['secret_key']
        self.region = secret_aws['region']
        self.public_key_path = os.path.abspath(secret_aws['public_key_path'])
        self.private_key_path = os.path.abspath(secret_aws['private_key_path'])


class AWSProviderProp:

    image_id = None
    vpn_image_id = None
    size_id = None

    def __init__(self, secret_aws):
        self.image_id = secret_aws['image_id']
        self.vpn_image_id = secret_aws['vpn_image_id']
        self.size_id = secret_aws['size_id']


class AWSProviderInfo(ProviderInfo):

    def __init__(self, secret_aws):
        self.type = Providers.AWS
        self.cred = AWSProviderCred(secret_aws)
        self.prop = AWSProviderProp(secret_aws)


class AzureProviderCred:

    tenant_id = None
    subscription_id = None
    application_id = None
    password = None
    public_key = None
    private_key = None

    def __init__(self, secret_azure):
        self.tenant_id = secret_azure['tenant_id']
        self.subscription_id = secret_azure['subscription_id']
        self.application_id = secret_azure['application_id']
        self.password = secret_azure['password']
        self.public_key_path = secret_azure['public_key_path']
        self.private_key_path = secret_azure['private_key_path']


class AzureProviderProp:

    location_id = None
    resource_group = None
    storage_account = None
    image_id = None
    dns_image_id = None
    size_id = None

    def __init__(self, secret_azure):
        self.location_id = secret_azure['location_id']
        self.resource_group = secret_azure['resource_group']
        self.storage_account = secret_azure['storage_account']
        self.image_id = secret_azure['image_id']
        self.dns_image_id = secret_azure['dns_image_id']
        self.size_id = secret_azure['size_id']


class AzureProviderInfo(ProviderInfo):
    def __init__(self, secret_azure):
        self.type = Providers.AZURE
        self.cred = AzureProviderCred(secret_azure)
        self.prop = AzureProviderProp(secret_azure)
