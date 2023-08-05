from datadog.api.resources import SearchableAPIResource


class Infrastructure(SearchableAPIResource):
    """
    A wrapper around Infrastructure HTTP API.
    """
    _resource_name = 'search'

    @classmethod
    def search(cls, **params):
        """
        Search for entities in Datadog.

        :param q: a query to serch for host and metrics
        :type q: string query

        :returns: Dictionary representing the API's JSON response
        """
        return super(Infrastructure, cls)._search(**params)
