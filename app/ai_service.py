"""Schema-guided AI extraction. Uses an OpenAI-compatible API when OPENAI_API_KEY is set,
otherwise (or on any failure) the local analyzer. Output is always validated with Pydantic."""
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

from . import fallback
from .schemas import AnalysisResult, AnalyzeRequest

SYSTEM_PROMPT = """You are TalentVerse, a careful career-intelligence assistant.
Return ONLY one JSON object (no markdown) with exactly these keys:
{
  "profile_summary": string (2-3 sentences, based only on the supplied text),
  "skills": [string],
  "education": [string],
  "experience": [{"role": string, "organization": string, "duration": string, "highlights": [string]}],
  "target_role": string,
  "skill_gaps": [string],
  "milestones": [{"title": string, "timeframe": string, "actions": [string]}],
  "job_match": {"matched_skills": [string], "missing_skills": [string], "match_percent": integer 0-100 or null, "match_summary": string},
  "missing_info": [string]
}
Rules: use ONLY evidence in the supplied text; never invent employers, degrees or skills the person did not mention;
use empty lists / empty strings / null when information is absent and describe what is missing in "missing_info".
Mode "profile": extract skills, education, experience; fill skill_gaps only if a target role is given.
Mode "career_plan": identify skill_gaps for the target role and write 3-5 milestones with concrete actions.
Mode "job_match": input_text is the job description and profile_text is the candidate; fill job_match and set skill_gaps to the missing skills."""


def _call_llm(request: AnalyzeRequest, api_key: str) -> Dict[str, Any]:
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    user_payload = {"mode": request.mode, "target_role": request.target_role,
                    "input_text": request.input_text, "profile_text": request.profile_text}
    body = json.dumps({
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": json.dumps(user_payload)}],
    }).encode("utf-8")
    req = urllib.request.Request(
        base + "/chat/completions", data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")[:200]
        raise RuntimeError(f"AI API returned HTTP {exc.code}: {detail}") from exc
    content = data["choices"][0]["message"]["content"].strip()
    content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.MULTILINE).strip()
    return json.loads(content)


def run_analysis(request: AnalyzeRequest) -> Tuple[Dict[str, Any], str, Optional[str]]:
    """Returns (validated_result_dict, processing_mode, warning)."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    warning: Optional[str] = None
    if api_key:
        try:
            raw = _call_llm(request, api_key)
            result = AnalysisResult.model_validate(raw)
            return result.model_dump(), f"AI ({os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')})", None
        except Exception as exc:  # network error, bad JSON, schema mismatch ...
            warning = f"AI call failed ({str(exc)[:160]}); used the local analyzer instead."
    raw = fallback.analyze(request.mode, request.input_text, request.profile_text, request.target_role)
    result = AnalysisResult.model_validate(raw)
    return result.model_dump(), "Local analyzer (no AI key)" if not api_key else "Local analyzer (AI fallback)", warning
