from io import StringIO

import requests
import yaml


class OpenAPISpecs:

    def __init__(self, location):
        self._location = location
        self._specs = self._load()

    def exists(self, method, path):
        p = self._get_path(path)
        if not p:
            return False
        info = self._specs['paths'][p]
        return method.lower() in info

    def _load(self):
        if self._location.startswith('http'):
            return self._load_from_url()
        return self._load_from_fs()

    def _load_from_url(self):
        res = requests.get(self._location, stream=True)
        if res.status_code == 200:
            result = StringIO()
            for chunk in res.iter_content(chunk_size=8192):
                result.write(str(chunk, encoding='utf-8'))
            result.seek(0)
            return yaml.safe_load(result)
        res.raise_for_status()

    def _load_from_fs(self):
        with open(self._location, 'r') as f:
            return yaml.safe_load(f)

    def _get_path(self, path):
        if '?' in path:
            path, _ = path.split('?', 1)
        components = path.split('/')
        for p in self._specs['paths'].keys():
            cmps = p[1:].split('/')
            if len(cmps) != len(components):
                continue
            for idx, comp in enumerate(components):
                if cmps[idx].startswith('{'):
                    continue
                if cmps[idx] != comp:
                    break
            else:
                return p
