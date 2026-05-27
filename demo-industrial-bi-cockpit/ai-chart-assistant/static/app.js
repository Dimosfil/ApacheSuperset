const form = document.querySelector("#prompt-form");
const promptInput = document.querySelector("#prompt");
const generateButton = document.querySelector("#generate-button");
const copyButton = document.querySelector("#copy-button");
const copyStatus = document.querySelector("#copy-status");
const provider = document.querySelector("#provider");
const confidence = document.querySelector("#confidence");
const params = document.querySelector("#params");
const routeBase = window.location.pathname.startsWith("/ai-chart-assistant")
  ? "/ai-chart-assistant"
  : "";

document.querySelector("#catalog-link").href = `${routeBase}/api/datasets`;
document.querySelector("#superset-link").href = routeBase ? "/" : "http://localhost:8088";

const fields = {
  title: document.querySelector("#draft-title"),
  dataset: document.querySelector("#dataset"),
  chartType: document.querySelector("#chart-type"),
  metric: document.querySelector("#metric"),
  dimension: document.querySelector("#dimension"),
  timeRange: document.querySelector("#time-range"),
  explanation: document.querySelector("#explanation"),
};

let latestParams = {};

function setLoading(isLoading) {
  generateButton.disabled = isLoading;
  generateButton.textContent = isLoading ? "Генерация..." : "Сгенерировать";
}

function setStatus(text, isWarning = false) {
  provider.textContent = text;
  provider.classList.toggle("warning", isWarning);
}

function renderDraft(draft) {
  latestParams = draft.superset_params || {};
  fields.title.textContent = draft.title || "Draft preview";
  fields.dataset.textContent = draft.dataset || "-";
  fields.chartType.textContent = draft.viz_type || draft.chart_type || "-";
  fields.metric.textContent = draft.metric || "-";
  fields.dimension.textContent = draft.dimension || "-";
  fields.timeRange.textContent = draft.time_range || "-";
  fields.explanation.textContent = draft.explanation || "";
  confidence.textContent = draft.confidence
    ? `Уверенность ${Math.round(draft.confidence * 100)}%`
    : "";
  setStatus(
    draft.fallback_used ? "Fallback rules" : draft.provider || "Ready",
    Boolean(draft.fallback_used),
  );
  params.textContent = JSON.stringify(latestParams, null, 2);
}

async function generateDraft(prompt) {
  setLoading(true);
  copyStatus.textContent = "";
  try {
    const response = await fetch(`${routeBase}/api/text-to-chart`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Request failed");
    }
    renderDraft(payload);
  } catch (error) {
    setStatus("Error", true);
    fields.explanation.textContent = error.message;
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const prompt = promptInput.value.trim();
  if (prompt) {
    generateDraft(prompt);
  }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    promptInput.value = button.dataset.prompt;
    generateDraft(button.dataset.prompt);
  });
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(JSON.stringify(latestParams, null, 2));
  copyStatus.textContent = "Copied";
  window.setTimeout(() => {
    copyStatus.textContent = "";
  }, 1600);
});

generateDraft(promptInput.value.trim());
