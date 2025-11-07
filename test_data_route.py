#location:-tests/test_data_route.py




###
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import your router
from src.routes.data import dataRouter


class TestDataRoute(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Create test FastAPI app and mocked dependencies."""
        app = FastAPI()
        app.include_router(dataRouter)
        # mock app dependencies
        app.db_client = MagicMock()
        app.llmService = MagicMock()
        self.client = TestClient(app)
        self.app = app

    async def test_missing_admin_credentials_returns_403(self):
        """If admin name or password not provided → 403"""
        response = self.client.get("/data/start/MyCompany")
        self.assertEqual(response.status_code, 403)
        self.assertIn("AUTHENTICATION_FAILED", response.json()["Message"])

    @patch("src.routes.data.AdminModel")
    async def test_invalid_admin_returns_403(self, MockAdminModel):
        """If admin credentials invalid → 403"""
        mock_admin = AsyncMock()
        mock_admin.check_if_admin_exists.return_value = False
        MockAdminModel.create_instance = AsyncMock(return_value=mock_admin)

        response = self.client.get("/data/start/MyCompany?Admin_name=admin&Admin_password=wrong")
        self.assertEqual(response.status_code, 403)
        self.assertIn("AUTHENTICATION_FAILED", response.json()["Message"])

    @patch("src.routes.data.AdminModel")
    @patch("src.routes.data.CompanyModel")
    @patch("src.routes.data.DataController")
    async def test_no_company_chunks_returns_404(self, MockDataController, MockCompanyModel, MockAdminModel):
        """If company chunks list empty → 404"""
        mock_admin = AsyncMock()
        mock_admin.check_if_admin_exists.return_value = True
        MockAdminModel.create_instance = AsyncMock(return_value=mock_admin)

        mock_company = MagicMock()
        mock_company.Name = "MyCompany"
        mock_company.id = "123"
        MockCompanyModel.create_instance = AsyncMock(return_value=MagicMock(get_company_or_create_one=AsyncMock(return_value=mock_company)))

        mock_controller = MagicMock()
        mock_controller.get_company_chunks.return_value = []
        MockDataController.return_value = mock_controller

        response = self.client.get("/data/start/MyCompany?Admin_name=admin&Admin_password=1234")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Company data does not exist", response.json()["Message"])

    @patch("src.routes.data.ChunkModel")
    @patch("src.routes.data.DataController")
    @patch("src.routes.data.CompanyModel")
    @patch("src.routes.data.AdminModel")
    async def test_successful_flow_returns_201(self, MockAdminModel, MockCompanyModel, MockDataController, MockChunkModel):
        """Full successful flow → 201"""
        # Mock admin
        mock_admin = AsyncMock()
        mock_admin.check_if_admin_exists.return_value = True
        MockAdminModel.create_instance = AsyncMock(return_value=mock_admin)

        # Mock company
        mock_company = MagicMock()
        mock_company.Name = "MyCompany"
        mock_company.id = "123"
        MockCompanyModel.create_instance = AsyncMock(return_value=MagicMock(get_company_or_create_one=AsyncMock(return_value=mock_company)))

        # Mock controller to return chunks
        mock_controller = MagicMock()
        mock_controller.get_company_chunks.return_value = ["chunk_1", "chunk_2"]
        MockDataController.return_value = mock_controller

        # Mock ChunkModel
        mock_chunk_model = AsyncMock()
        mock_chunk_model.add_and_delete_chunks.return_value = True
        MockChunkModel.create_instance = AsyncMock(return_value=mock_chunk_model)

        # Mock LLM service to return list-like object
        self.app.llmService.embed_text.return_value = MagicMock(toList=lambda: [1, 2, 3])

        response = self.client.get("/data/start/MyCompany?Admin_name=admin&Admin_password=1234")
        self.assertEqual(response.status_code, 201)
        self.assertIn("ADDED_TO_DATA_BASE", response.json()["message"])


if __name__ == "__main__":
    unittest.main()
