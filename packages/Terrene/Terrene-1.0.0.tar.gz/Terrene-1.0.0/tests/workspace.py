import unittest


class WorkspaceTestCases(unittest.TestCase):
    def test_workspace_creation_and_deletion(self):
        from terrene.apps import WorkspaceManager

        workspace_manager = WorkspaceManager()
        workspace = workspace_manager.create(
            name="My Workspace", description="A workspace for Terrene's tutorial")

        workspace.delete()
