location :-src/test/test_base.py



#""""""""""
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import your router
from src.routes.base import baseRouter


class TestBaseRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a temporary FastAPI app and mount the router once for all tests."""
        app = FastAPI()
        app.include_router(baseRouter)
        cls.client = TestClient(app)

    def test_root_endpoint_status_code(self):
        """Test that GET / returns HTTP 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_root_endpoint_response_body(self):
        """Test that GET / returns the expected JSON response."""
        response = self.client.get("/")
        self.assertEqual(response.json(), {"message": "Welcome To CSAB APP"})


if __name__ == "__main__":
    unittest.main()
