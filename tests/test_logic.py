"""Tests for the analyzer and database layer (no web framework needed)."""
import os
import tempfile
import unittest

os.environ["TALENTVERSE_DB"] = os.path.join(tempfile.mkdtemp(), "logic.db")

from app import database, fallback  # noqa: E402


class FallbackTests(unittest.TestCase):
    def test_extracts_skills_without_false_positives(self):
        skills = fallback.extract_skills("Python developer who knows JavaScript, C++ and SQL.")
        self.assertIn("Python", skills)
        self.assertIn("JavaScript", skills)
        self.assertIn("C++", skills)
        self.assertNotIn("Java", skills)  # 'JavaScript' must not count as Java

    def test_profile_mode(self):
        text = "Data Analysis Intern at Bluestock Fintech (Jan-Feb 2026)\nSkills: Python, SQL, LangChain, RAG"
        r = fallback.analyze("profile", text, "", "Generative AI Developer")
        self.assertIn("LangChain", r["skills"])
        self.assertEqual(r["experience"][0]["organization"], "Bluestock Fintech")
        self.assertEqual(r["target_role"], "Generative AI Developer")
        self.assertNotIn("Python", r["skill_gaps"])

    def test_career_plan_creates_milestones(self):
        r = fallback.analyze("career_plan", "I want to become an AI Engineer. I know Python and SQL.", "", "")
        self.assertEqual(r["target_role"], "AI/ML Engineer")
        self.assertTrue(r["skill_gaps"])
        self.assertGreaterEqual(len(r["milestones"]), 2)

    def test_unknown_role_is_reported_not_guessed(self):
        r = fallback.analyze("career_plan", "I want to become an astronaut someday soon", "", "")
        self.assertEqual(r["skill_gaps"], [])
        self.assertTrue(r["missing_info"])

    def test_job_match(self):
        r = fallback.analyze("job_match", "Need Python, Docker, AWS, SQL", "I know Python and SQL. Git too.", "")
        jm = r["job_match"]
        self.assertEqual(jm["matched_skills"], ["Python", "SQL"])
        self.assertEqual(jm["missing_skills"], ["Docker", "AWS"])
        self.assertEqual(jm["match_percent"], 50)

    def test_no_skills_reports_missing_info(self):
        r = fallback.analyze("profile", "Hello there, this is just a greeting.", "", "")
        self.assertEqual(r["skills"], [])
        self.assertTrue(r["missing_info"])


class DatabaseTests(unittest.TestCase):
    def test_crud(self):
        database.init_db()
        saved = database.insert_record("profile", "AI Engineer", "text", "", {"profile_summary": "hi"}, "local")
        rid = saved["id"]
        self.assertIn(rid, [x["id"] for x in database.list_records()])
        self.assertEqual(database.get_record(rid)["result"]["profile_summary"], "hi")
        self.assertTrue(database.delete_record(rid))
        self.assertIsNone(database.get_record(rid))
        self.assertFalse(database.delete_record(rid))


if __name__ == "__main__":
    unittest.main()
