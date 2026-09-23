"""
Student Career Roadmap Generator
---------------------------------
A small Flask app that takes a student's target career, current skills,
and experience level, and returns:
  - the full required-skill curriculum for that career
  - which skills they already have
  - which skills are missing
  - a phased learning roadmap with a suggested project per skill
  - a progress percentage

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import json
import os
from difflib import SequenceMatcher

from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "careers.json")

app = Flask(__name__)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    CAREERS = json.load(f)


def normalize(text):
    """Lowercase and strip a skill name for loose comparison."""
    return text.strip().lower()


def is_match(user_skill, required_skill):
    """
    True if a skill the user typed should count as satisfying a required
    skill. Exact/substring match first, then a fuzzy fallback so close
    spellings ("java script", "react.js") still count.
    """
    u, r = normalize(user_skill), normalize(required_skill)
    if not u:
        return False
    if u == r or u in r or r in u:
        return True
    return SequenceMatcher(None, u, r).ratio() > 0.8


def compute_roadmap(career_id, current_skills, experience_level):
    career = CAREERS[career_id]
    current_skills = [s for s in current_skills if s.strip()]

    all_required = [
        skill["name"]
        for stage in career["stages"]
        for skill in stage["skills"]
    ]

    phases = []
    known_count = 0

    for stage in career["stages"]:
        stage_skills = []
        for skill in stage["skills"]:
            known = any(is_match(u, skill["name"]) for u in current_skills)
            if known:
                known_count += 1
            stage_skills.append(
                {
                    "name": skill["name"],
                    "project": skill["project"],
                    "known": known,
                }
            )
        phases.append({"stage": stage["stage"], "skills": stage_skills})

    total = len(all_required)
    missing = [
        s["name"]
        for phase in phases
        for s in phase["skills"]
        if not s["known"]
    ]
    known = [
        s["name"]
        for phase in phases
        for s in phase["skills"]
        if s["known"]
    ]

    progress = round((known_count / total) * 100) if total else 0

    level_notes = {
        "beginner": "Start from Foundations, even for skills that feel familiar — the projects build on each other.",
        "intermediate": "You can likely move through Foundations quickly and spend most of your time in Core.",
        "advanced": "Skim Foundations and Core for gaps only, and focus your effort on the Advanced stage.",
    }

    return {
        "career": career["title"],
        "tagline": career["tagline"],
        "route_color": career["route_color"],
        "experience_level": experience_level,
        "level_note": level_notes.get(experience_level, ""),
        "total_skills": total,
        "known_skills": known,
        "missing_skills": missing,
        "progress": progress,
        "phases": phases,
    }


@app.route("/")
def index():
    careers = [{"id": cid, "title": c["title"]} for cid, c in CAREERS.items()]
    return render_template("index.html", careers=careers)


@app.route("/api/careers")
def api_careers():
    return jsonify(
        [{"id": cid, "title": c["title"], "tagline": c["tagline"]} for cid, c in CAREERS.items()]
    )


@app.route("/api/generate-roadmap", methods=["POST"])
def api_generate_roadmap():
    data = request.get_json(silent=True) or {}
    career_id = data.get("career_id")
    current_skills = data.get("current_skills", [])
    experience_level = data.get("experience_level", "beginner")

    if career_id not in CAREERS:
        return jsonify({"error": "Unknown career_id"}), 400
    if not isinstance(current_skills, list):
        return jsonify({"error": "current_skills must be a list"}), 400
    if experience_level not in ("beginner", "intermediate", "advanced"):
        return jsonify({"error": "experience_level must be beginner, intermediate, or advanced"}), 400

    result = compute_roadmap(career_id, current_skills, experience_level)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
