import unittest


class EnrichTestCases(unittest.TestCase):
    def test_predictive_model_creation_and_deletion(self):
        import os
        from terrene.apps import WorkspaceManager
        from terrene.enrich import PredictiveModelManager

        workspace_manager = WorkspaceManager()
        workspace = workspace_manager.create(
            name="My Workspace", description="A workspace for Terrene's tutorial")

        predictive_model_manager = PredictiveModelManager(workspace=workspace)

        model = predictive_model_manager.create(
            name="my predictive model", description="predictive model",
            input_variables="Sex, Pclass, Fare, Parch, SibSp, Age", output_variables="Survived")

        model.delete()
        workspace.delete()
