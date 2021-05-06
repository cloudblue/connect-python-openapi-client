from connect.client.utils import get_values, parse_content_range


class AbstractIterator:
    def __init__(self, client, path, query, config, **kwargs):
        self._client = client
        self._path = path
        self._query = query
        self._config = config
        self._kwargs = kwargs
        self._results, self._cr = self._execute_request()

    def get_item(self, item):
        raise NotImplementedError('get_item must be implemented in subclasses.')

    def __next__(self):
        if self._results is None:
            raise StopIteration
        try:
            item = next(self._results)
        except StopIteration:
            if self._cr is None or self._cr.last >= self._cr.count - 1:
                raise
            self._config['params']['offset'] += self._config['params']['limit']
            self._results, self._cr = self._execute_request()
            if not self._results:
                raise
            item = next(self._results)

        return self.get_item(item)

    def _execute_request(self):
        results = self._client.get(
            f'{self._path}?{self._query}',
            **self._config,
        )
        content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return iter(results), content_range


class ResourceIterator(AbstractIterator):

    def get_item(self, item):
        return item


class ValuesListIterator(AbstractIterator):

    def get_item(self, item):
        return get_values(item, self._kwargs['fields'])
