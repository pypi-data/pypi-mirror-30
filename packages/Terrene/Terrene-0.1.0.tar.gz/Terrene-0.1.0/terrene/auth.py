from .api import CoreAPI, CoreAPIMixin, BaseModel, BaseModelManager
from .config import api

import coreapi


class User(BaseModel):
    def add_role(self, role):
        return self.act(['roles', 'create'], {
            'object_id': self.object_id, 'role': role})

    def remove_role(self, role):
        return self.act(['roles', 'partial_update'], {
            'object_id': self.object_id, 'role': role})

    def reset_secret_key(self):
        return self.act(['reset_secret_key'], {
            'object_id': self.object_id})

    def set_password(self, new_password, old_password):
        return self.act(['set_password'], {
            'object_id': self.object_id, 'new_password': new_password,
            'old_password': old_password})


class UserManager(BaseModelManager):
    model = User
    namespace = ['users']
    credentials = None

    def create(self, params):
        # update the coreapi attribute and credentials attribute to
        # authenticate the newly created user
        user = self.act(['create'], params)
        EmailPasswordCredentials(
            email=params['email'], password=params['password'])
        return self.model(
            user['object_id'], self.namespace, self.coreapi)


class BaseCredentials(CoreAPIMixin):
    namespace = ['users', 'actions', 'login']
    headers = {}

    def __init__(self, *args, **kwargs):
        self.coreapi = CoreAPI()
        object_id = self._authenticate(*args, **kwargs)

        # attempt to update the coreapi document, and client with the authenticated
        # headers created by the _authenticate method
        self.coreapi.client = coreapi.Client(
            transports=[coreapi.transports.HTTPTransport(headers=self.headers)])
        self.coreapi.document = self.coreapi.client.get(api() + '/schema/')

        # retrieve current_user
        if object_id is not None:
            self.current_user = User(object_id, UserManager.namespace, self.coreapi)

    def _authenticate(self, *args, **kwargs):
        raise NotImplementedError()


class EmailPasswordCredentials(BaseCredentials):
    def _authenticate(self, *args, **kwargs):
        for kwarg in ['email', 'password']:
            if kwargs.get(kwarg, None) is None:
                raise AssertionError(
                    "{} kwarg is required for all the UserPassCredentials instances.".format(
                        kwarg))
        results = self.act(['obtain_token'], {
            'email': kwargs.get('email'), 'password': kwargs.get('password')})
        self.headers['Authorization'] = 'JWT {}'.format(results['token'])
        return results['user']['object_id']


class TokenCredential(BaseCredentials):
    def _authenticate(self, *args, **kwargs):
        for kwarg in ['token']:
            if kwargs.get(kwarg, None) is None:
                raise AssertionError(
                    "{} kwarg is required for all the TokenCredential instances.".format(
                        kwarg))
        results = self.act(['verify_token'], {
            'token': kwargs.get('token')})
        self.headers['Authorization'] = 'JWT {}'.format(results['token'])
        return None
