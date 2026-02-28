const API_BASE =
  location.hostname === "localhost" || location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "";

function el(id) {
  return document.getElementById(id);
}

async function postJSON(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }

  return res.json();
}

function renderScores(data) {
  el("overallScore").innerText =
    data.overall_score ?? data.overallScore ?? "--";

  const breakdown = el("breakdown");
  breakdown.innerHTML = "";

  const items = [
    ["Readability", data.readability],
    ["Performance", data.performance],
    ["Security", data.security],
    ["Maintainability", data.maintainability],
    ["Time", data.time_complexity],
    ["Space", data.space_complexity],
  ];

  for (const [label, val] of items) {
    const d = document.createElement("div");
    d.innerText = `${label}: ${val ?? "--"}`;
    breakdown.appendChild(d);
  }
}

function renderIssues(issues) {
  const container = el("analysis");
  container.innerHTML = "";

  if (!issues) {
    container.innerText = "No issues found.";
    return;
  }

  for (const sev of ["critical", "high", "medium", "low"]) {
    const arr = issues[sev] || [];

    const h = document.createElement("h4");
    h.innerText = `${sev.charAt(0).toUpperCase() + sev.slice(1)} (${arr.length})`;
    h.className = "font-semibold";
    container.appendChild(h);

    const ul = document.createElement("ul");

    for (const it of arr) {
      const li = document.createElement("li");
      if (typeof it === "string") {
        li.innerText = it;
      } else {
        li.innerText = `${
          it.line ? "Line " + it.line + ": " : ""
        }${it.message || JSON.stringify(it)}`;
      }
      ul.appendChild(li);
    }

    container.appendChild(ul);
  }
}

function setImprovement(percent) {
  const bar = el("improveBar");
  const text = el("improveText");

  if (!bar || !text) return;

  let p = 0;

  if (typeof percent === "number") {
    p = percent;
  } else if (!isNaN(Number(percent))) {
    p = Number(percent);
  }

  p = Math.max(-100, Math.min(100, p));

  bar.style.width = `${Math.abs(p)}%`;
  bar.style.backgroundColor = p >= 0 ? "#34d399" : "#f87171";

  text.innerText =
    p >= 0
      ? `Code Quality Improved by ${p}%`
      : `Code Quality Changed by ${p}%`;
}

document.addEventListener("DOMContentLoaded", () => {
  el("reviewBtn").addEventListener("click", async () => {
    const code = el("codeInput").value;
    const language = el("language").value;

    try {
      const data = await postJSON("/review", { code, language });

      const normalized = {
        overall_score: data.overall_score ?? data.overallScore,
        used_stub: data.used_stub ?? data.usedStub ?? false,
        _debug_error: data._debug_error ?? data._debugError ?? null,
        readability: data.readability,
        performance: data.performance,
        security: data.security,
        maintainability: data.maintainability,
        time_complexity: data.time_complexity ?? data.timeComplexity,
        space_complexity: data.space_complexity ?? data.spaceComplexity,
        issues: data.issues,
        improvement_suggestion:
          data.improvement_suggestion ?? data.improvementSuggestion,
        rewritten_code: data.rewritten_code ?? data.rewrittenCode,
      };

      const banner = el("stubBanner");

      if (normalized.used_stub) {
        banner.classList.remove("hidden");
        banner.innerText =
          "Warning: Response is a local stub. " +
          (normalized._debug_error
            ? "Debug: " + normalized._debug_error
            : "");
      } else {
        banner.classList.add("hidden");
        banner.innerText = "";
      }

      renderScores(normalized);
      renderIssues(normalized.issues);

      el("rewrittenCode").textContent =
        normalized.rewritten_code || "";

      hljs.highlightAll();

      setImprovement(0);
    } catch (e) {
      alert("Review error: " + e.message);
    }
  });

  el("rewriteBtn").addEventListener("click", async () => {
    const code = el("codeInput").value;
    const language = el("language").value;

    const origScore = Number(el("overallScore").innerText) || 0;

    try {
      const data = await postJSON("/rewrite", {
        code,
        language,
        original_score: origScore,
      });

      const normalized = {
        overall_score: data.overall_score ?? data.overallScore,
        used_stub: data.used_stub ?? data.usedStub ?? false,
        _debug_error: data._debug_error ?? data._debugError ?? null,
        readability: data.readability,
        performance: data.performance,
        security: data.security,
        maintainability: data.maintainability,
        time_complexity: data.time_complexity ?? data.timeComplexity,
        space_complexity: data.space_complexity ?? data.spaceComplexity,
        issues: data.issues,
        improvement_suggestion:
          data.improvement_suggestion ?? data.improvementSuggestion,
        rewritten_code: data.rewritten_code ?? data.rewrittenCode,
        improvement_percentage:
          data.improvement_percentage ?? data.improvementPercentage,
      };

      const banner = el("stubBanner");

      if (normalized.used_stub) {
        banner.classList.remove("hidden");
        banner.innerText =
          "Warning: Response is a local stub. " +
          (normalized._debug_error
            ? "Debug: " + normalized._debug_error
            : "");
      } else {
        banner.classList.add("hidden");
        banner.innerText = "";
      }

      renderScores(normalized);
      renderIssues(normalized.issues);

      const codeEl = el("rewrittenCode");

      const rawCode = normalized.rewritten_code || "";
      const fixedCode = rawCode.replace(/\\n/g, "\n");

      codeEl.textContent = fixedCode;
      codeEl.className = `hljs language-${language}`;
      hljs.highlightElement(codeEl);

      // ✅ SAFE IMPROVEMENT HANDLING
      let percent = 0;

      if (typeof normalized.improvement_percentage === "number") {
        percent = normalized.improvement_percentage;
      } else if (!isNaN(Number(normalized.improvement_percentage))) {
        percent = Number(normalized.improvement_percentage);
      }

      setImprovement(percent);
    } catch (e) {
      alert("Rewrite error: " + e.message);
    }
  });
});