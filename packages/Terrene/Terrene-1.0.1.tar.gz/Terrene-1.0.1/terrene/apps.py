from .api import BaseModelManager, BaseModel


class BaseApp(BaseModel):
    @property
    def connection_credentials(self):
        return self.act(['credentials', 'read'], {'object_id': self.object_id})


class BaseAppManager(BaseModelManager):
    model = BaseApp
    namespace = ['apps']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace = kwargs.pop('workspace', None)

        if self.workspace is None:
            raise AssertionError("Missing workspace parameter on initialization")

    def pre_create(self, **params):
        params['workspace'] = self.workspace.object_id
        return params

    def pre_save(self, **params):
        if not isinstance(self.workspace, str):
            params['workspace'] = params['workspace'].object_id

    def query(self, query_params):
        query_params = {**query_params, **{
            'workspace__object_id': self.workspace.object_id}}
        return super().query(query_params)


class Workspace(BaseModel):
    predictive_model_manager = None
    model_endpoint_manager = None
    sql_database_manager = None
    file_input_manager = None
    file_output_manager = None
    warehouse_query_input_manager = None
    data_parser_manager = None

    def __init__(self, *args, **kwargs):
        super(Workspace, self).__init__(*args, **kwargs)

        from .enrich import PredictiveModelManager
        from .serve import ModelEndpointManager
        from .store import SQLDatabaseManager
        from .transfer import FileInputManager, WarehouseQueryInputManager,\
            FileOutputManager, DataParserManager

        self.predictive_model_manager = PredictiveModelManager(
            workspace=self, credentials=self.credentials)
        self.model_endpoint_manager = ModelEndpointManager(
            workspace=self, credentials=self.credentials)
        self.sql_database_manager = SQLDatabaseManager(
            workspace=self, credentials=self.credentials)
        self.file_input_manager = FileInputManager(
            workspace=self, credentials=self.credentials)
        self.warehouse_query_input_manager = WarehouseQueryInputManager(
            workspace=self, credentials=self.credentials)
        self.file_output_manager = FileOutputManager(
            workspace=self, credentials=self.credentials)
        self.data_parser_manager = DataParserManager(
            credentials=self.credentials)

    def add_owner(self, email):
        return self.act(['owners', 'create'], {
            'object_id': self.object_id, 'user': email})

    def remove_owner(self, email):
        return self.act(['owners', 'partial_update'], {
            'object_id': self.object_id, 'user': email})

    def add_contributor(self, email):
        return self.act(['contributors', 'create'], {
            'object_id': self.object_id, 'user': email})

    def remove_contributor(self, email):
        return self.act(['contributors', 'partial_update'], {
            'object_id': self.object_id, 'user': email})

    def set_payment_method(self, payment_method_object_id):
        return self.act(['set_payment_method'], {
            'object_id': self.object_id, 'method': payment_method_object_id})

    def notify(self, subject, content):
        return self.act(['notify'], {
            'object_id': self.object_id, 'subject': subject, 'content': content})


class WorkspaceManager(BaseModelManager):
    model = Workspace
    namespace = ['workspaces']
