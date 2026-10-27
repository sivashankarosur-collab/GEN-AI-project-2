"use strict";

const MODES = {
  profile: {
    roleLabel: "Target role (optional)", rolePlaceholder: "e.g. AI/ML Engineer",
    mainLabel: "Resume / profile text",
    placeholder: "Paste your resume or a short introduction: education, skills, internships, projects...",
    sample: "O.Sivashankar\nB.Tech CSE (Generative AI) at Lovely Professional University, CGPA 7.5\nData Analysis Intern at Bluestock Fintech (Jan-Feb 2026)\nProjects: RAG chatbot with Streamlit, LangChain and ChromaDB; candidate screening system with FastAPI\nSkills: Python, Java, C++, PyTorch, TensorFlow, scikit-learn, LangChain, SQL, AWS, Git",
    sampleRole: "Generative AI Developer",
  },
  career_plan: {
    roleLabel: "Target role", rolePlaceholder: "e.g. AI Engineer, Data Scientist, Full Stack Developer",
    mainLabel: "Career goal and your current skills",
    placeholder: "Describe your goal and what you already know...",
    sample: "I want to become an AI Engineer. I know Python, SQL and basic machine learning with scikit-learn.",
    sampleRole: "AI/ML Engineer",
  },
  job_match: {
    roleLabel: "Job title (optional)", rolePlaceholder: "e.g. Backend Developer",
    mainLabel: "Job description",
    placeholder: "Paste the job description / requirements...",
    sample: "We are hiring a Backend Developer. Requirements: Python, FastAPI, SQL, Docker, AWS, Git and REST APIs. Knowledge of CI/CD is a plus.",
    sampleRole: "Backend Developer",
    sampleProfile: "Python Developer at Acme Corp, 2 years. Skills: Python, Flask, SQL, Git, REST APIs.",
  },
};

let mode = "profile";
const $ = (id) => document.getElementById(id);

function h(tag, props, ...children) {
  const el = document.createElement(tag);
  if (props) {
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") el.className = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v);
    }
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    el.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  }
  return el;
}

function setStatus(kind, text) {
  const s = $("status");
  s.className = "status " + (kind || "");
  s.textContent = text || "";
}

function setMode(m) {
  mode = m;
  const cfg = MODES[m];
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.mode === m));
  $("roleLabel").textContent = cfg.roleLabel;
  $("targetRole").placeholder = cfg.rolePlaceholder;
  $("mainLabel").textContent = cfg.mainLabel;
  $("mainText").placeholder = cfg.placeholder;
  $("profileBox").classList.toggle("hidden", m !== "job_match");
  setStatus("", "");
}

function chips(items, cls) {
  if (!items || !items.length) return h("p", { class: "muted" }, "None");
  return h("div", { class: "chips" }, items.map((s) => h("span", { class: "chip " + (cls || "") }, s)));
}

function renderResult(data, saved) {
  const r = data.result;
  const card = $("resultCard");
  card.replaceChildren();
  card.classList.remove("hidden");

  card.appendChild(h("div", { class: "row-between" },
    h("h2", null, "Result"),
    h("div", null,
      h("span", { class: "badge" }, "Mode: " + data.mode),
      h("span", { class: "badge" }, data.processing_mode),
      h("span", { class: "badge" }, "Record #" + data.id))));

  if (data.warning) card.appendChild(h("div", { class: "status warn" }, data.warning));
  card.appendChild(h("p", null, r.profile_summary || ""));

  if (r.target_role) card.appendChild(h("p", null, h("strong", null, "Target role: "), r.target_role));

  card.appendChild(h("h3", null, "Skills"));
  card.appendChild(chips(r.skills));

  if (r.education && r.education.length) {
    card.appendChild(h("h3", null, "Education"));
    card.appendChild(h("ul", null, r.education.map((e) => h("li", null, e))));
  }

  if (r.experience && r.experience.length) {
    card.appendChild(h("h3", null, "Experience"));
    r.experience.forEach((e) => card.appendChild(h("div", { class: "item" },
      h("strong", null, e.role || "Role"),
      e.organization ? " · " + e.organization : "",
      e.duration ? h("span", { class: "muted" }, " · " + e.duration) : null,
      e.highlights && e.highlights.length ? h("ul", null, e.highlights.map((x) => h("li", null, x))) : null)));
  }

  const jm = r.job_match || {};
  if (data.mode === "job_match") {
    card.appendChild(h("h3", null, "Job match"));
    if (jm.match_percent !== null && jm.match_percent !== undefined) {
      card.appendChild(h("strong", null, jm.match_percent + "% match"));
      card.appendChild(h("div", { class: "bar" }, h("div", { style: "width:" + jm.match_percent + "%" })));
    }
    card.appendChild(h("p", null, jm.match_summary || ""));
    card.appendChild(h("p", { class: "muted" }, "Matched skills"));
    card.appendChild(chips(jm.matched_skills, "good"));
    card.appendChild(h("p", { class: "muted" }, "Missing skills"));
    card.appendChild(chips(jm.missing_skills, "bad"));
  } else if (r.skill_gaps && r.skill_gaps.length) {
    card.appendChild(h("h3", null, "Skill gaps"));
    card.appendChild(chips(r.skill_gaps, "bad"));
  }

  if (r.milestones && r.milestones.length) {
    card.appendChild(h("h3", null, "Learning milestones"));
    r.milestones.forEach((m) => card.appendChild(h("div", { class: "item" },
      h("strong", null, m.title), m.timeframe ? h("span", { class: "muted" }, " · " + m.timeframe) : null,
      h("ul", null, (m.actions || []).map((a) => h("li", null, a))))));
  }

  if (r.missing_info && r.missing_info.length) {
    card.appendChild(h("h3", null, "Missing information"));
    card.appendChild(h("ul", null, r.missing_info.map((m) => h("li", null, m))));
  }
  if (saved) card.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function api(path, options) {
  const res = await fetch(path, options);
  let body = null;
  try { body = await res.json(); } catch (_) { /* non-JSON error page */ }
  if (!res.ok) {
    const detail = body && body.detail ? (typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail)) : "Request failed (" + res.status + ")";
    throw new Error(detail);
  }
  return body;
}

async function analyze() {
  const input_text = $("mainText").value.trim();
  const profile_text = $("profileText").value.trim();
  const target_role = $("targetRole").value.trim();

  if (!input_text) return setStatus("err", "Please enter text before analyzing — the input cannot be empty.");
  if (input_text.length < 10) return setStatus("err", "The text is too short (minimum 10 characters).");
  if (mode === "job_match" && profile_text.length < 10) return setStatus("err", "Job Match also needs your profile/skills text.");

  const btn = $("analyzeBtn");
  btn.disabled = true;
  setStatus("info", "Analyzing...");
  try {
    const data = await api("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, input_text, profile_text, target_role }),
    });
    renderResult(data, true);
    setStatus("ok", "Saved to database ✓  (record #" + data.id + ")");
    loadRecords();
  } catch (err) {
    setStatus("err", err.message || "Something went wrong.");
  } finally {
    btn.disabled = false;
  }
}

async function loadRecords() {
  const box = $("records");
  try {
    const data = await api("/api/profiles");
    box.replaceChildren();
    if (!data.items.length) { box.appendChild(h("p", { class: "muted" }, "No saved records yet.")); return; }
    data.items.forEach((it) => box.appendChild(h("div", { class: "rec" },
      h("div", { class: "meta" },
        h("div", null, h("strong", null, "#" + it.id), " ", h("span", { class: "badge" }, it.mode),
          it.target_role ? h("span", { class: "badge" }, it.target_role) : null),
        h("div", { class: "muted" }, it.summary || "")),
      h("div", { class: "actions" },
        h("button", { class: "ghost", onclick: () => viewRecord(it.id) }, "View"),
        h("button", { class: "ghost danger", onclick: () => removeRecord(it.id) }, "Delete")))));
  } catch (err) {
    box.replaceChildren(h("p", { class: "muted" }, "Could not load records: " + err.message));
  }
}

async function viewRecord(id) {
  try {
    const rec = await api("/api/profiles/" + id);
    renderResult({ id: rec.id, mode: rec.mode, processing_mode: rec.processing_mode, warning: null, result: rec.result }, true);
  } catch (err) { setStatus("err", err.message); }
}

async function removeRecord(id) {
  if (!confirm("Delete record #" + id + "?")) return;
  try {
    await api("/api/profiles/" + id, { method: "DELETE" });
    setStatus("ok", "Record #" + id + " deleted.");
    loadRecords();
  } catch (err) { setStatus("err", err.message); }
}

document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => setMode(t.dataset.mode)));
$("analyzeBtn").addEventListener("click", analyze);
$("refreshBtn").addEventListener("click", loadRecords);
$("clearBtn").addEventListener("click", () => {
  $("mainText").value = ""; $("profileText").value = ""; $("targetRole").value = ""; setStatus("", "");
});
$("sampleBtn").addEventListener("click", () => {
  const cfg = MODES[mode];
  $("mainText").value = cfg.sample;
  $("targetRole").value = cfg.sampleRole || "";
  $("profileText").value = cfg.sampleProfile || "";
  setStatus("", "");
});

setMode("profile");
loadRecords();
