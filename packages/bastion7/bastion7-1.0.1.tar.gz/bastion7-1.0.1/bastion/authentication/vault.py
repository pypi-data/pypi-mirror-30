import os
import hvac

from bastion.provider_types import Providers
from base import BaseAuthDriver, AWSProviderInfo, AzureProviderInfo


class VaultAuthDriver(BaseAuthDriver):
    _client = None

    def __init__(self, token):
        self._client = hvac.Client(url=os.environ['VAULT_ADDR'])
        self._client.token = token

    def get_provider_info(self, path):
        secret = self._client.read(path)
        provider_info = None

        if secret["data"]["cloud_provider"] == Providers.AWS:
            provider_info = AWSProviderInfo(secret["data"])
        if secret["data"]["cloud_provider"] == Providers.AZURE:
            provider_info = AzureProviderInfo(secret["data"])

        return provider_info

    def get_providers_info(self, path):
        providers_info = []

        secret_lists = self._client.list(path)

        # Iterar sobre la lista de secrets
        for key in secret_lists["data"]["keys"]:
            provider_info = self.get_provider_info(path + '/' + key)
            if provider_info is not None:
                providers_info.append(provider_info)

        return providers_info
