const form = document.getElementById("roadmap-form");
const resultsSection = document.getElementById("results");
const resultsEmpty = document.getElementById("results-empty");
const routeEl = document.getElementById("route");

const DIAL_CIRCUMFERENCE = 2 * Math.PI * 52; // r=52, matches the SVG circle

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const careerId = document.getElementById("career").value;
  const skillsRaw = document.getElementById("skills").value;
  const level = form.querySelector('input[name="level"]:checked').value;

  const currentSkills = skillsRaw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const submitBtn = form.querySelector(".depart-btn span");
  const originalLabel = submitBtn.textContent;
  submitBtn.textContent = "Laying out the route…";

  try {
    const res = await fetch("/api/generate-roadmap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        career_id: careerId,
        current_skills: currentSkills,
        experience_level: level,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "Something went wrong generating the roadmap.");
    }

    const data = await res.json();
    renderResults(data);
  } catch (err) {
    routeEl.innerHTML = "";
    resultsSection.hidden = true;
    resultsEmpty.hidden = false;
    resultsEmpty.textContent = err.message;
  } finally {
    submitBtn.textContent = originalLabel;
  }
});

function renderResults(data) {
  resultsEmpty.hidden = true;
  resultsSection.hidden = false;
  resultsSection.style.setProperty("--route-color", data.route_color);

  document.getElementById("summary-kicker").textContent =
    `Route to · ${capitalize(data.experience_level)} level`;
  document.getElementById("summary-title").textContent = data.career;
  document.getElementById("summary-note").textContent = data.level_note;

  document.getElementById("progress-percent").textContent = data.progress;
  const dialFill = document.getElementById("dial-fill");
  const offset = DIAL_CIRCUMFERENCE * (1 - data.progress / 100);
  dialFill.style.stroke = data.route_color;
  // reset then set so the CSS transition animates on every generate
  dialFill.style.strokeDashoffset = DIAL_CIRCUMFERENCE;
  requestAnimationFrame(() => {
    dialFill.style.strokeDashoffset = offset;
  });

  routeEl.innerHTML = "";
  data.phases.forEach((phase) => {
    const stageWrap = document.createElement("div");
    stageWrap.className = "route-stage";

    const title = document.createElement("h3");
    title.className = "route-stage-title";
    title.textContent = phase.stage;
    stageWrap.appendChild(title);

    phase.skills.forEach((skill) => {
      stageWrap.appendChild(buildStation(skill, data.route_color));
    });

    routeEl.appendChild(stageWrap);
  });

  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildStation(skill, routeColor) {
  const station = document.createElement("div");
  station.className = `station${skill.known ? " known" : ""}`;
  station.style.setProperty("--route-color", routeColor);

  const track = document.createElement("div");
  track.className = "station-track";
  const dot = document.createElement("div");
  dot.className = "station-dot";
  track.appendChild(dot);

  const content = document.createElement("div");
  content.className = "station-content";

  const name = document.createElement("p");
  name.className = "station-name";
  const status = document.createElement("span");
  status.className = "station-status";
  status.textContent = skill.known ? "Have it" : "To learn";
  name.append(skill.name, status);

  const project = document.createElement("p");
  project.className = "station-project";
  project.innerHTML = `<strong>Project:</strong> ${escapeHtml(skill.project)}`;

  content.append(name, project);
  station.append(track, content);
  return station;
}

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
