from connect.client.models.resourceset import _ResourceSetBase


class ResourceSetMock(_ResourceSetBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._count = None

    def __getitem__(self, key):  # noqa: CCR001
        self._validate_key(key)

        if isinstance(key, int):
            copy = self._copy()
            copy._limit = 1
            copy._offset = key
            return copy

        copy = self._copy()
        copy._offset = key.start
        copy._slice = key
        if copy._slice.stop - copy._slice.start < copy._limit:
            copy._limit = copy._slice.stop - copy._slice.start

        return copy

    def count(self, return_value=0, status_code=200, headers=None):
        headers = headers or {}
        if self._count is None:
            request_kwargs = self._get_request_kwargs()
            url = self._build_full_url(
                0,
                0,
                request_kwargs['params'].get('search'),
            )
            if status_code == 200:
                if not isinstance(return_value, int):
                    raise TypeError('return_value must be an integer')
                headers['Content-Range'] = f'items 0-0/{return_value}'
                self._client.get(
                    url,
                    return_value=[],
                    headers=headers,
                )
                self._count = return_value
            else:
                headers['Content-Range'] = f'items 0-0/{return_value}'
                self._client.get(
                    url,
                    status_code=status_code,
                    headers=headers,
                )

    def first(self):
        copy = self._copy()
        copy._limit = 1
        copy._offset = 0
        return copy

    def mock(
        self,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        if status_code != 200:
            request_kwargs = self._get_request_kwargs()
            url = self._build_full_url(
                request_kwargs['params']['limit'],
                request_kwargs['params']['offset'],
                request_kwargs['params'].get('search'),
            )
            self._client.get(
                url,
                status_code=status_code,
                return_value=return_value,
                headers=headers,
            )
            return

        if not isinstance(return_value, list):
            raise TypeError('return_value must be a list of objects')

        if not self._slice:
            self._mock_iteration(return_value, headers)
        else:
            self._mock_slicing(return_value, headers)

    def _mock_iteration(self, return_value, extra_headers):
        request_kwargs = self._get_request_kwargs()
        total = len(return_value)
        self._count = 0

        if total == 0:
            url = self._build_full_url(
                request_kwargs['params']['limit'],
                0,
                request_kwargs['params'].get('search'),
            )
            headers = {'Content-Range': 'items 0-0/0'}

            if extra_headers:
                headers.update(extra_headers)
            self._client.get(
                url,
                return_value=[],
                headers=headers,
            )
            return

        def pages_iterator():
            for i in range(0, total, self._limit):
                yield return_value[i : i + self._limit], i

        for page, offset in pages_iterator():
            url = self._build_full_url(
                request_kwargs['params']['limit'],
                offset,
                request_kwargs['params'].get('search'),
            )
            headers = {'Content-Range': f'items {offset}-{offset + len(page) - 1}/{total}'}
            if extra_headers:
                headers.update(extra_headers)
            self._client.get(
                url,
                return_value=page,
                headers=headers,
            )
            self._count += len(page)

    def _mock_slicing(self, return_value, extra_headers):
        request_kwargs = self._get_request_kwargs()
        total = len(return_value)
        self._count = 0

        if total == 0:
            url = self._build_full_url(
                request_kwargs['params']['limit'],
                0,
                request_kwargs['params'].get('search'),
            )
            headers = {'Content-Range': 'items 0-0/0'}

            if extra_headers:
                headers.update(extra_headers)
            self._client.get(
                url,
                return_value=[],
                headers=headers,
            )
            return

        def pages_iterator():
            limit = request_kwargs['params']['limit']
            offset = request_kwargs['params']['offset']
            last = offset - 1
            remaining = 0
            while True:
                page = return_value[offset : offset + limit]
                if not page or limit == 0:
                    return
                yield page, limit, offset
                last += len(page)
                remaining = self._slice.stop - last - 1
                offset += limit
                if remaining < limit:
                    limit = remaining

        for page, limit, offset in pages_iterator():
            url = self._build_full_url(
                limit,
                offset,
                request_kwargs['params'].get('search'),
            )
            headers = {'Content-Range': f'items {offset}-{offset + len(page) - 1}/{total}'}
            if extra_headers:
                headers.update(extra_headers)
            self._client.get(
                url,
                return_value=page,
                headers=headers,
            )
            self._count += len(page)

    def _build_full_url(self, limit, offset, search=None):
        url = self._get_request_url()
        start = '&' if '?' in url else '?'
        params = f'{start}limit={limit}&offset={offset}'
        if search:
            params = f'{params}&search={search}'

        return f'{url}{params}'

    def _copy(self):
        rs = super()._copy()
        rs._count = self._count
        return rs
