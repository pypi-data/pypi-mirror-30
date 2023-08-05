from .auth import *
from .workspace import *
from .enrich import *
from .transfer import *
from .store import *
from .serve import *

import unittest


class EndToEndTestCases(unittest.TestCase):
    def test_titanic_dataset(self):
        import os
        import time
        from terrene.apps import WorkspaceManager
        from terrene.transfer import DataParserManager

        workspace = WorkspaceManager().create(
            name="My Workspace", description="A workspace for Terrene's tutorial")

        with open('tests/dist/train.csv', 'r') as input_file:
            csv_file_input = workspace.file_input_manager.create(
                name="my file", description="training dataset",
                file=input_file, parser=DataParserManager().CSVParser)

        model = workspace.predictive_model_manager.create(
            name="my predictive model", description="predictive model",
            input_variables="Sex, Pclass, Fare, Parch, SibSp, Age, Cabin",
            output_variables="Survived")
        model.train(transfer=csv_file_input, epochs=100)
        # retrain
        model.train(transfer=csv_file_input, epochs=500)

        endpoint = workspace.model_endpoint_manager.create(
            enrich=model, name="my endpoint", description="used to make predictions")

        time.sleep(10)  # wait until model is available is done

        print(endpoint.predict({
            "Pclass": 1, "Age": 24, "Sex": "male",
            "Embarked": "S", "SibSp": 0, "Parch": 0,
            "Fare": 14.25, "Cabin": "C30"}))
        print(endpoint.predict({
            "Pclass": 1, "Age": 24, "Sex": "male",
            "Embarked": "S", "SibSp": 0, "Parch": 0,
            "Fare": 14.25, "Cabin": "C30"}))

        endpoint.predict(
            file=open('tests/dist/train.csv', 'r'),
            parser=DataParserManager().CSVParser)

        time.sleep(10)  # wait until processing is done
        endpoint_output = workspace.file_output_manager.query({})[0]
        endpoint_output.save_content('tests/dist/output.csv')

        workspace.delete()
