const form = document.querySelector("#vibe-form");
const input = document.querySelector("#vibe");
const status = document.querySelector("#status");
const result = document.querySelector("#result");
const notes = document.querySelector("#notes");
const tags = document.querySelector("#tags");
const themeName = document.querySelector("#theme-name");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const vibe = input.value.trim();
  if (!vibe) return;

  status.textContent = "finding the feeling...";
  result.hidden = true;
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vibe }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Something went quiet.");
    render(data);
    status.textContent = "";
  } catch (error) {
    status.textContent = error.message;
  }
});

function render(data) {
  const { theme } = data;
  document.documentElement.style.setProperty("--background", theme.background);
  document.documentElement.style.setProperty("--surface", theme.surface);
  document.documentElement.style.setProperty("--accent", theme.accent);
  document.documentElement.style.setProperty("--text", theme.text);
  document.documentElement.style.setProperty("--glow", theme.glow);
  themeName.textContent = theme.name;
  tags.replaceChildren(...data.matched_tags.slice(0, 6).map(tagChip));
  notes.replaceChildren(...data.notes.map(noteCard));
  result.hidden = false;
}

function tagChip(tag) {
  const element = document.createElement("span");
  element.textContent = tag;
  return element;
}

function noteCard(note) {
  const card = document.createElement("article");
  card.className = "note";
  card.innerHTML = '<p class="role"></p><h3></h3><p class="description"></p>';
  card.querySelector(".role").textContent = note.role;
  card.querySelector("h3").textContent = note.name;
  card.querySelector(".description").textContent = note.description;
  return card;
}
