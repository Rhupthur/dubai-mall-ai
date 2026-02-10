console.log("app.js loaded");

let chart = null;
let radar = null;

let PROFILES = [];
let LAST_FILE = null;

// Palette FIXE (mêmes couleurs partout)
const CLUSTER_COLOR_MAP = {
  0: "#60a5fa",
  1: "#34d399",
  2: "#fbbf24",
  3: "#f87171",
};

function colorForCluster(cid) {
  const k = Number(cid);
  return Object.prototype.hasOwnProperty.call(CLUSTER_COLOR_MAP, k) ? CLUSTER_COLOR_MAP[k] : "#a78bfa";
}

function setText(id, txt) {
  const el = document.getElementById(id);
  if (el) el.textContent = txt;
}

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`GET ${url} failed`);
  return res.json();
}

async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

/* =========================
   Résumé KPI Cards
========================= */
function renderSummaryCards(nRows, counts) {
  const el = document.getElementById("summaryCards");
  if (!el) return;

  el.innerHTML = "";

  const total = document.createElement("div");
  total.className = "scard";
  total.innerHTML = `
    <div class="t">Total lignes</div>
    <div class="n">${nRows ?? "—"}</div>
  `;
  el.appendChild(total);

  const entries = Object.entries(counts || {}).sort((a, b) => Number(a[0]) - Number(b[0]));
  entries.forEach(([cid, v]) => {
    const c = colorForCluster(cid);
    const pct = nRows ? Math.round((Number(v) / Number(nRows)) * 100) : null;

    const card = document.createElement("div");
    card.className = "scard";
    card.innerHTML = `
      <div class="t">
        <span class="dot" style="background:${c};"></span>
        Cluster ${cid}
      </div>
      <div class="n">
        ${v} ${pct !== null ? `<span class="pct">(${pct}%)</span>` : ``}
      </div>
    `;
    el.appendChild(card);
  });
}

/* =========================
   Chart (bar) — couleurs fixes
========================= */
function renderChart(counts) {
  const labels = Object.keys(counts).sort((a, b) => Number(a) - Number(b));
  const values = labels.map((k) => counts[k]);
  const colors = labels.map((cid) => colorForCluster(cid));

  const ctx = document.getElementById("distChart");
  if (!ctx) return;

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Clients",
        data: values,
        backgroundColor: colors,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } }
    }
  });
}

function renderProfiles(profiles) {
  const container = document.getElementById("profiles");
  if (!container) return;

  container.innerHTML = "";
  if (!profiles?.length) {
    container.innerHTML = `<div class="hint">Aucun profil disponible.</div>`;
    return;
  }

  profiles.forEach(p => {
    const c = colorForCluster(p.cluster_id);
    const div = document.createElement("div");
    div.className = "profile";
    div.innerHTML = `
      <h4><span class="dot" style="background:${c}; margin-right:8px;"></span>Cluster ${p.cluster_id} — ${p.label}</h4>
      <div class="small">Taille: <b>${p.size}</b> (${Math.round(p.pct*100)}%)</div>
      <div class="small">Âge moyen: <b>${p.mean_age.toFixed(1)}</b></div>
      <div class="small">Income moyen (k$): <b>${p.mean_income.toFixed(1)}</b></div>
      <div class="small">Spending moyen: <b>${p.mean_spending.toFixed(1)}</b></div>
    `;
    container.appendChild(div);
  });
}

function renderPreview(rows) {
  const preview = document.getElementById("preview");
  if (!preview) return;

  preview.innerHTML = "";
  if (!rows?.length) return;

  const cols = Object.keys(rows[0]);
  const table = document.createElement("table");

  const thead = document.createElement("thead");
  const trh = document.createElement("tr");
  cols.forEach(c => {
    const th = document.createElement("th");
    th.textContent = c;
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  rows.forEach(r => {
    const tr = document.createElement("tr");
    cols.forEach(c => {
      const td = document.createElement("td");
      td.textContent = r[c];
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  preview.appendChild(table);
}

/* =========================
   Radar — même couleurs
========================= */
function renderRadarForCluster(cid) {
  const prof = PROFILES.find(p => Number(p.cluster_id) === Number(cid));
  if (!prof) return;

  const maxAge = Math.max(...PROFILES.map(p => p.mean_age));
  const maxInc = Math.max(...PROFILES.map(p => p.mean_income));
  const maxSp  = Math.max(...PROFILES.map(p => p.mean_spending));

  const values = [
    (prof.mean_age / maxAge) * 100,
    (prof.mean_income / maxInc) * 100,
    (prof.mean_spending / maxSp) * 100,
  ];

  const ctx = document.getElementById("radarChart");
  if (!ctx) return;

  if (radar) radar.destroy();

  const c = colorForCluster(cid);

  radar = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Age", "Income", "Spending"],
      datasets: [{
        label: `Cluster ${cid}`,
        data: values,
        borderColor: c,
        backgroundColor: c + "33",
        pointBackgroundColor: c
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: { r: { suggestedMin: 0, suggestedMax: 100 } }
    }
  });
}

async function init() {
  console.log("init() start");

  // status
  try {
    await getJSON("/api/health");
    const pill = document.getElementById("apiStatus");
    if (pill) {
      pill.textContent = "API: OK";
      pill.style.borderColor = "rgba(34,197,94,.5)";
      pill.style.color = "#bbf7d0";
    }
  } catch {
    const pill = document.getElementById("apiStatus");
    if (pill) pill.textContent = "API: KO";
  }

  // metadata
  const fmt = (x) => (typeof x === "number" ? x.toFixed(4) : "—");

  try {
    const meta = await getJSON("/api/metadata");
    setText("modelName", meta.model_name);
    setText("kValue", String(meta.params?.n_clusters ?? "—"));
    setText("silhouette", fmt(meta.metrics?.silhouette));
    setText("dbi", fmt(meta.metrics?.davies_bouldin));
    setText("chi", fmt(meta.metrics?.calinski_harabasz));
  } catch (e) {
    console.error("metadata load failed", e);
  }

  // profiles (for radar + labels)
  try {
    const p = await getJSON("/api/profiles");
    PROFILES = p.profiles || [];
  } catch (e) {
    console.error("profiles load failed", e);
  }

  // simulation (✅ plus de JSON visible)
  document.getElementById("btnSim")?.addEventListener("click", async () => {
    const payload = {
      Gender: document.getElementById("gender").value,
      Age: Number(document.getElementById("age").value),
      "Annual Income (k$)": Number(document.getElementById("income").value),
      "Spending Score (1-100)": Number(document.getElementById("spending").value),
    };

    const debug = document.getElementById("simOut");      // caché
    const human = document.getElementById("simHuman");    // visible
    const badge = document.getElementById("simBadge");

    if (human) human.textContent = "Processing...";
    if (debug) debug.textContent = "";
    if (badge) badge.innerHTML = "";

    try {
      const data = await postJSON("/api/cluster/row", payload);

      const cid = data.cluster_id;
      const label = data.cluster_label || "—";
      const pct = (typeof data.cluster_pct === "number") ? Math.round(data.cluster_pct * 100) : null;

      const c = colorForCluster(cid);

      if (badge) {
        badge.innerHTML = `
          <span class="badge">
            <span class="dot" style="background:${c}"></span>
            <b>Cluster ${cid}</b>
            <span>${label}</span>
            ${pct !== null ? `<span>(${pct}%)</span>` : ``}
          </span>
        `;
      }

      if (human) {
        const w = (data.warnings && data.warnings.length)
          ? ` ${data.warnings.join(", ")}`
          : " OK";

        human.innerHTML = `
          <div><b>Segment:</b> Cluster ${cid} ${pct !== null ? `(${pct}%)` : ""}</div>
          <div><b>Profil:</b> ${label}</div>
          <div><b>Qualité entrée:</b> ${w}</div>
        `;
      }

      renderRadarForCluster(cid);

      // Debug optionnel (caché)
      if (debug) debug.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      if (human) human.textContent = `Error: ${e.message}`;
    }
  });

  // upload CSV
  document.getElementById("btnUpload")?.addEventListener("click", async () => {
    const fileInput = document.getElementById("csvFile");
    const debugOut = document.getElementById("fileOut"); // caché
    const exportBtn = document.getElementById("btnExport");

    const summary = document.getElementById("summaryCards");
    if (summary) summary.innerHTML = "";

    if (debugOut) debugOut.textContent = "Uploading...";
    renderPreview([]);
    renderProfiles([]);

    if (!fileInput?.files?.length) {
      if (debugOut) debugOut.textContent = "Choisis un CSV.";
      return;
    }

    LAST_FILE = fileInput.files[0];

    const form = new FormData();
    form.append("file", LAST_FILE);

    try {
      const res = await fetch("/api/cluster/file", { method: "POST", body: form });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "API error");
      }
      const data = await res.json();

      // Résumé en cards
      renderSummaryCards(data.n_rows, data.cluster_counts);

      // Debug caché
      if (debugOut) {
        debugOut.textContent = JSON.stringify(
          { n_rows: data.n_rows, cluster_counts: data.cluster_counts },
          null,
          2
        );
      }

      renderChart(data.cluster_counts || {});
      renderProfiles(data.profiles || []);
      renderPreview(data.preview || []);

      if (exportBtn) exportBtn.disabled = false;
    } catch (e) {
      if (debugOut) debugOut.textContent = `Error: ${e.message}`;
      if (exportBtn) exportBtn.disabled = true;
    }
  });

  // export CSV
  document.getElementById("btnExport")?.addEventListener("click", async () => {
    if (!LAST_FILE) return;

    const form = new FormData();
    form.append("file", LAST_FILE);

    const res = await fetch("/api/cluster/file/export", { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Export failed");
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = (LAST_FILE.name.replace(/\.csv$/i, "") + "_clustered.csv");
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);
  });
}

init();
