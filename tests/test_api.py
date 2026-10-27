"""End-to-end API tests (skipped automatically if FastAPI is not installed)."""
import os
import tempfile
import unittest

os.environ["TALENTVERSE_DB"] = os.path.join(tempfile.mkdtemp(), "api.db")
os.environ["OPENAI_API_KEY"] = ""  # force the local analyzer so tests are offline

try:
    from fastapi.testclient import TestClient
    from app.main import app
    HAVE_FASTAPI = True
except ImportError:
    HAVE_FASTAPI = False


@unittest.skipUnless(HAVE_FASTAPI, "fastapi not installed")
class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ctx = TestClient(app)
        cls.client = cls._ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    def test_health_and_frontend(self):
        self.assertEqual(self.client.get("/api/health").json()["status"], "ok")
        self.assertIn("TalentVerse", self.client.get("/").text)
        self.assertEqual(self.client.get("/static/app.js").status_code, 200)

    def test_profile_saved_and_retrievable(self):
        body = {"mode": "profile", "input_text": "I am a Python developer with SQL and machine learning experience."}
        res = self.client.post("/api/analyze", json=body)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["saved"])
        self.assertIn("Python", data["result"]["skills"])
        got = self.client.get(f"/api/profiles/{data['id']}")
        self.assertEqual(got.status_code, 200)
        self.assertIn(data["id"], [i["id"] for i in self.client.get("/api/profiles").json()["items"]])

    def test_empty_input_rejected(self):
        res = self.client.post("/api/analyze", json={"mode": "profile", "input_text": "   "})
        self.assertEqual(res.status_code, 422)
        self.assertIn("empty", res.json()["detail"].lower())

    def test_bad_mode_rejected(self):
        res = self.client.post("/api/analyze", json={"mode": "nope", "input_text": "Python developer here"})
        self.assertEqual(res.status_code, 422)

    def test_job_match_requires_profile(self):
        res = self.client.post("/api/analyze", json={"mode": "job_match", "input_text": "Need Python and Docker skills"})
        self.assertEqual(res.status_code, 422)

    def test_career_plan_and_delete(self):
        res = self.client.post("/api/analyze", json={
            "mode": "career_plan", "input_text": "I know Python and want to grow.", "target_role": "Data Scientist"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["result"]["milestones"])
        rid = res.json()["id"]
        self.assertEqual(self.client.delete(f"/api/profiles/{rid}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/profiles/{rid}").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/profiles/{rid}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
