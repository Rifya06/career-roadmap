# Routeline — Student Career Roadmap Generator

A small full-stack app that takes a student's target career, current skills,
and experience level, and generates a phased learning roadmap with a
suggested project at each step — styled like a transit/wayfinding map.

## Stack

- **Backend:** Python (Flask) — serves the page and one JSON API endpoint
- **Frontend:** HTML, CSS, vanilla JavaScript (no build step, no frameworks)
- **Data:** a static JSON file of career curricula (`data/careers.json`)

## Project structure

```
career_roadmap/
├── app.py                  # Flask app: routes + skill-gap logic
├── requirements.txt
├── data/
│   └── careers.json        # Career curricula: stages → skills → projects
├── templates/
│   └── index.html          # Page shell, rendered by Flask
└── static/
    ├── style.css            # All styling
    └── script.js             # Form submit → API call → render roadmap
```

## Setup

```bash
cd career_roadmap
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in a browser.

## How it works

1. The student picks a career, types their current skills (comma-separated),
   and picks an experience level.
2. The frontend POSTs that to `/api/generate-roadmap`.
3. The backend (`compute_roadmap` in `app.py`):
   - Loads the full curriculum for that career from `careers.json`
   - Matches each typed skill against the required skills (exact/substring
     match, with a fuzzy fallback for near-spellings like "java script")
   - Splits skills into **known** vs **missing**
   - Returns the full roadmap grouped into stages (Foundations → Core →
     Advanced), each skill tagged `known: true/false` with its project,
     plus an overall progress percentage
4. The frontend renders the roadmap as a route line: filled stations are
   skills the student already has, hollow stations are what's next, each
   with its suggested project.

## API

`POST /api/generate-roadmap`

```json
{
  "career_id": "web-developer",
  "current_skills": ["HTML", "CSS", "basic Python"],
  "experience_level": "beginner"
}
```

Returns the career title, progress percentage, known/missing skill lists,
and the full phased roadmap (see `app.py` for the exact shape).

`GET /api/careers` — lists all available careers with id/title/tagline.

## Included careers

Web Developer, UI/UX Designer, Data Analyst, Data Scientist — each with a
3-stage, ~12-skill curriculum and one hands-on project per skill.

## Extending it

- **Add a career:** add a new top-level entry to `data/careers.json`
  following the same `stages → skills → {name, project}` shape. No code
  changes needed.
- **Progress tracking across visits:** the app is currently stateless
  (no login, nothing saved). To persist progress you'd add a small
  database (SQLite is enough) with a `users` and `completed_skills` table,
  plus simple session-based auth.
- **Smarter skill matching:** swap `is_match()` in `app.py` for a proper
  synonym map (e.g. "JS" → "JavaScript", "React.js" → "A Frontend
  Framework (React)") if you find students' free-text answers aren't
  matching well.
- **Export:** add a route that renders the roadmap to PDF/Markdown so
  students can save it outside the browser.
