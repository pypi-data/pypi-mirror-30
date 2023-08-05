from .apps import BaseApp, BaseAppManager
from .config import api

from coreapi.utils import File
import json
import uuid
import requests


class ModelEndpoint(BaseApp):
    def predict(self, params=None, file=None, parser=None):
        if params is not None:
            params = {str(key): str(value) for key, value in params.items()}
            res = requests.post(
                api() + '/' + '/'.join(self.namespace) + '/{}/predict/'.format(self.object_id),
                data=json.dumps({'input_json': params}), headers={
                    **{'Content-Type': 'application/json'}, **self.headers})
            return res.json()
        elif file is not None and parser is not None:
            return self.act(['predict', 'create'], {
                'object_id': self.object_id,
                'input_file': File(str(uuid.uuid4()), file.read()),
                'input_file_parser': parser.object_id})
        else:
            raise ValueError("Both params OR file and parser can not be None")

    def pre_save(self):
        for param in ['enrich', 'store', 'workspace']:
            if self._data.get(param, None) is not None and \
                    not isinstance(self._data[param], str):
                self._data[param] = self._data[param].object_id


class ModelEndpointManager(BaseAppManager):
    model = ModelEndpoint
    namespace = ['serve']

    def pre_create(self, **params):
        params['workspace'] = self.workspace.object_id
        params['enrich'] = params['enrich'].object_id
        if params.get('store', None) is not None:
            params['store'] = params['store'].object_id
        return params
