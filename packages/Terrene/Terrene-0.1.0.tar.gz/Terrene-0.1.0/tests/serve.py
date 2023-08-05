import unittest


class ServeTestCases(unittest.TestCase):
    def test_predictive_endpoint_creation_and_deletion(self):
        from terrene.apps import WorkspaceManager
        from terrene.enrich import PredictiveModelManager
        from terrene.serve import ModelEndpointManager

        workspace_manager = WorkspaceManager()
        workspace = workspace_manager.create(
            name="My Workspace", description="A workspace for Terrene's tutorial")

        predictive_model_manager = PredictiveModelManager(workspace=workspace)

        model = predictive_model_manager.create(
            name="my predictive model", description="predictive model",
            input_variables="Sex, Pclass, Fare, Parch, SibSp, Age", output_variables="Survived")

        model_endpoint_manager = ModelEndpointManager(workspace=workspace)
        endpoint = model_endpoint_manager.create(
            enrich=model, name="my endpoint", description="used to make predictions")

        endpoint.delete()
        model.delete()
        workspace.delete()
