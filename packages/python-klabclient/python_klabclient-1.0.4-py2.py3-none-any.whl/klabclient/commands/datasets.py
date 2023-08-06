
from klabclient.commands import models


class Catalog(models.Catalog):
    """List datasets from catalog"""

    @property
    def _catalog_function(self):
        client = self.app.client
        return client.datasets.catalog
