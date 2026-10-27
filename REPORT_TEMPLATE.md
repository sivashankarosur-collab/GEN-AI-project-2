# TalentVerse — Skills & Career Intelligence
**Course:** CSB312 — Generative AI  |  **Assessment:** CA3 Mini Project 2 (Option 9)
**Student:** G Tharun  |  **Deployed URL:** [paste your Render URL here]  |  **GitHub:** https://github.com/Tharun2005x/TalentVerse

## 1. Objective
Build a full-stack Generative AI application that converts unstructured career text into validated, structured data and stores it in a database.

## 2. Problem statement
Students rarely know which skills they have, which they lack for a target job, or how to prepare. Resumes, goals and job descriptions are unstructured text that is slow to analyse by hand.

## 3. Selected automation ideas (Option 9)
1. Resume/profile text → structured skills & experience profile.
2. Career goal → skill-gap map and milestone learning plan.
3. Candidate profile vs job description → match percentage, matched and missing skills.

## 4. Technology stack
HTML/CSS/JavaScript frontend · Python FastAPI backend · Pydantic validation · SQLite database · OpenAI-compatible LLM API (optional) with a local rule-based fallback · unittest/pytest.

## 5. Architecture / workflow
```
Browser form → POST /api/analyze → schema-guided AI (or local analyzer)
→ Pydantic validation → SQLite INSERT → JSON response (record id)
→ frontend shows structured result + "Saved to database" confirmation
```

## 6. Schema (validated by Pydantic)
`profile_summary, skills[], education[], experience[{role, organization, duration, highlights[]}], target_role, skill_gaps[], milestones[{title, timeframe, actions[]}], job_match{matched_skills[], missing_skills[], match_percent, match_summary}, missing_info[]`

## 7. Prompt design
System prompt fixes the JSON schema, forbids inventing employers/degrees/skills, requires empty values when evidence is absent, and asks the model to list what is missing in `missing_info`. Temperature 0.2 and JSON-object response mode are used; the reply is parsed and validated before saving. On any failure the local analyzer is used and a warning is shown.

## 8. Database design
Table `profiles(id, mode, target_role, input_text, profile_text, result_json, processing_mode, created_at)`. Each successful analysis performs one INSERT; records can be listed, viewed and deleted.

## 9. Error handling
Empty/too-short input (client and server, HTTP 422 with readable message) · invalid mode · Job Match without profile text · AI API failure (fallback + warning) · database errors (HTTP 500) · unknown record (HTTP 404).

## 10. Testing
Automated: `python -m pytest -q` (analyzer, database CRUD, API success/validation/delete).
Manual screenshots to add: (a) successful analysis with "Saved to database", (b) empty-input error, (c) Saved records list, (d) Career Plan, (e) Job Match.

## 11. Screenshots
[Insert screenshots here]

## 12. Limitations
The local analyzer is keyword-based (known skills only) and is not a language model; AI mode needs an API key and network; results need human review and are not hiring decisions; free-tier hosting may reset the database.

## 13. Conclusion
TalentVerse implements the required input → AI extraction → validation → backend → database → frontend-confirmation workflow for all three Option 9 ideas.
