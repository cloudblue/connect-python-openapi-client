from connect.client.utils import get_values, parse_content_range


class aiter:
    def __init__(self, values):
        self._values = iter(values)

    async def __anext__(self):
        try:
            return next(self._values)
        except StopIteration:
            raise StopAsyncIteration


class AbstractBaseIterator:
    def __init__(self, client, path, query, config, **kwargs):
        self._client = client
        self._path = path
        self._query = query
        self._config = config
        self._kwargs = kwargs
        self._results = None
        self._cr = None
        self._loaded = False

    def get_item(self, item):
        raise NotImplementedError('get_item must be implemented in subclasses.')


class AbstractIterator(AbstractBaseIterator):

    def _load(self):
        if not self._loaded:
            self._results, self._cr = self._execute_request()
            self._loaded = True

    def __next__(self):
        self._load()

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


class AbstractAsyncIterator(AbstractBaseIterator):

    async def _load(self):
        if not self._loaded:
            self._results, self._cr = await self._execute_request()
            self._loaded = True

    async def __anext__(self):
        await self._load()

        if self._results is None:
            raise StopAsyncIteration
        try:
            item = next(self._results)
        except StopIteration:
            if self._cr is None or self._cr.last >= self._cr.count - 1:
                raise StopAsyncIteration
            self._config['params']['offset'] += self._config['params']['limit']
            self._results, self._cr = await self._execute_request()
            if not self._results:
                raise StopAsyncIteration
            item = next(self._results)

        return self.get_item(item)

    async def _execute_request(self):
        results = await self._client.get(
            f'{self._path}?{self._query}',
            **self._config,
        )
        content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return iter(results), content_range


class ResourceMixin:
    def get_item(self, item):
        return item


class ValueListMixin:
    def get_item(self, item):
        return get_values(item, self._kwargs['fields'])


class ResourceIterator(ResourceMixin, AbstractIterator):
    pass


class ValuesListIterator(ValueListMixin, AbstractIterator):
    pass


class AsyncResourceIterator(ResourceMixin, AbstractAsyncIterator):
    pass


class AsyncValuesListIterator(ValueListMixin, AbstractAsyncIterator):
    pass
