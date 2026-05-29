(function () {
  var path = window.location.pathname.replace(/\/+$/, "");
  if (
    window.__industrialBiAssistMounted ||
    path.startsWith("/ai-chart-assistant") ||
    path.endsWith("/login") ||
    path.endsWith("/logout")
  ) {
    return;
  }
  window.__industrialBiAssistMounted = true;

  function createElement(tagName, className, text) {
    var element = document.createElement(tagName);
    if (className) {
      element.className = className;
    }
    if (text) {
      element.textContent = text;
    }
    return element;
  }

  function setMessage(text, tone) {
    var status = document.querySelector(".industrial-ai-assist__status");
    if (!status) {
      return;
    }
    status.textContent = text;
    status.dataset.tone = tone || "neutral";
  }

  async function importAiData(button) {
    var defaultLabel = button.textContent;
    button.disabled = true;
    button.textContent = "Импорт...";
    setMessage("Готовлю AI-строки...", "neutral");

    try {
      var response = await fetch("/ai-chart-assistant/api/import-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: "Generate industrial BI demo data for maintenance and quality signals",
        }),
      });
      var payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Import failed");
      }
      window.location.assign(payload.list_url || "/chart/list/");
    } catch (error) {
      setMessage(error.message || "Импорт не выполнен", "warning");
    } finally {
      button.disabled = false;
      button.textContent = defaultLabel;
    }
  }

  function mountAssist() {
    if (document.querySelector(".industrial-ai-assist")) {
      return;
    }

    var panel = createElement("aside", "industrial-ai-assist");
    panel.setAttribute("aria-label", "AI Assist");

    var title = createElement("h2", "industrial-ai-assist__title", "AI Assist");
    var text = createElement("p", "industrial-ai-assist__copy", "AI assist для демо-данных и чартов.");
    var actions = createElement("div", "industrial-ai-assist__actions");

    var openLink = createElement("a", "industrial-ai-assist__primary", "Сгенерить");
    openLink.href = "/ai-chart-assistant/";
    openLink.target = "_self";

    var importButton = createElement("button", "industrial-ai-assist__secondary", "Импортировать");
    importButton.type = "button";
    importButton.addEventListener("click", function () {
      importAiData(importButton);
    });

    var status = createElement("p", "industrial-ai-assist__status", "Готово");
    status.dataset.tone = "neutral";

    actions.append(openLink, importButton);
    panel.append(title, text, actions, status);
    document.body.appendChild(panel);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountAssist, { once: true });
  } else {
    mountAssist();
  }
})();
