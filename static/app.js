/**
 * ScholarForge AI - Production Client Application Logic (v2.0)
 * SQLite Drafts Persistence, Mermaid Diagram Generation, Custom .docx Template Injection, AI Prompt Revisions
 */

let appState = {
  currentProjectId: null,
  currentStep: 1,
  metadata: {
    title: "AI-Powered Disease Prediction System",
    domain: "Machine Learning & Cloud Computing",
    degree: "Bachelor of Technology in Computer Science & Engineering",
    department: "Department of Computer Science & Engineering",
    college_name: "Institute of Technology & Science",
    university_name: "State Technological University",
    academic_year: "2024 - 2026",
    guide_name: "Dr. Amit K. Sharma",
    guide_designation: "Associate Professor",
    hod_name: "Dr. R. V. Patel",
    principal_name: "Dr. M. K. Nair",
    students: [
      { name: "Aarav Sharma", roll_no: "21BCSE042" }
    ]
  },
  code_source: {
    github_url: "",
    local_path: "",
    code_text: "",
    detected_tech_stack: ["Python", "FastAPI", "Machine Learning", "React", "PostgreSQL"],
    readme_content: "",
    file_tree_summary: "",
    sample_code: ""
  },
  format_config: {
    preset: "btech_standard",
    custom_guidelines: "",
    font_family: "Times New Roman",
    line_spacing: 1.5
  },
  custom_template_filename: null,
  screenshots: [],
  diagrams: {},
  activeDiagramTab: "architecture",
  llm_config: {
    provider: "offline",
    api_key: "",
    model_name: "",
    custom_prompt: ""
  },
  current_report: null
};

let autoSaveTimer = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  loadSavedSettings();
  renderTechBadges();
  renderScreenshots();
  refreshDraftsCount();
  setupDragAndDrop();
});

// Setup drag and drop for screenshots
function setupDragAndDrop() {
  const dropZone = document.getElementById("dropZone");
  if (!dropZone) return;

  ["dragenter", "dragover"].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.add("border-indigo-400", "bg-indigo-950/30");
    });
  });

  ["dragleave", "drop"].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.remove("border-indigo-400", "bg-indigo-950/30");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length) {
      handleScreenshotUpload({ target: { files } });
    }
  });
}

// Step Switching
function switchStep(stepNum) {
  appState.currentStep = stepNum;

  for (let i = 1; i <= 5; i++) {
    const tab = document.getElementById(`stepTab${i}`);
    const sec = document.getElementById(`stepSection${i}`);

    if (tab && sec) {
      if (i === stepNum) {
        tab.classList.add("active");
        sec.classList.remove("hidden");
      } else {
        tab.classList.remove("active");
        sec.classList.add("hidden");
        if (i < stepNum) {
          tab.classList.add("completed");
        } else {
          tab.classList.remove("completed");
        }
      }
    }
  }

  if (stepNum === 4 && (!appState.diagrams || !Object.keys(appState.diagrams).length)) {
    loadProjectDiagrams();
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
  lucide.createIcons();
}

// Student Team Rows
function addStudentRow() {
  const container = document.getElementById("studentsContainer");
  const row = document.createElement("div");
  row.className = "student-row flex flex-col sm:flex-row gap-3 items-center";
  row.innerHTML = `
    <input type="text" class="glass-input student-name" placeholder="Student Name (e.g. Priyanshu Roy)" onchange="triggerAutoSave()">
    <input type="text" class="glass-input student-roll" placeholder="University Roll No / USN (e.g. 21BCSE088)" onchange="triggerAutoSave()">
    <button type="button" onclick="removeStudentRow(this)" class="btn-secondary text-red-400 p-2 hover:bg-red-500/20">
      <i data-lucide="trash-2" class="w-4 h-4"></i>
    </button>
  `;
  container.appendChild(row);
  lucide.createIcons();
  triggerAutoSave();
}

function removeStudentRow(btn) {
  const row = btn.closest(".student-row");
  if (document.querySelectorAll(".student-row").length > 1) {
    row.remove();
    triggerAutoSave();
  } else {
    alert("At least one student candidate is required.");
  }
}

function collectMetadata() {
  const students = [];
  document.querySelectorAll(".student-row").forEach(row => {
    const name = row.querySelector(".student-name").value.trim();
    const roll = row.querySelector(".student-roll").value.trim();
    if (name) {
      students.push({ name, roll_no: roll || "N/A" });
    }
  });

  appState.metadata = {
    title: document.getElementById("metaTitle").value.trim() || "Project Report",
    domain: document.getElementById("metaDomain").value.trim() || "Computer Science",
    degree: document.getElementById("metaDegree").value.trim() || "Bachelor of Technology",
    department: document.getElementById("metaDepartment").value.trim() || "Department of CSE",
    college_name: document.getElementById("metaCollege").value.trim() || "Institute of Technology",
    university_name: document.getElementById("metaUniversity").value.trim() || "State University",
    academic_year: document.getElementById("metaYear").value.trim() || "2024 - 2026",
    guide_name: document.getElementById("metaGuide").value.trim() || "Dr. S. K. Sharma",
    guide_designation: "Associate Professor",
    hod_name: document.getElementById("metaHOD").value.trim() || "HOD",
    principal_name: "Principal",
    students: students.length ? students : [{ name: "Candidate Name", roll_no: "21BCSE001" }]
  };
}

// Auto-Save System (Debounced)
function triggerAutoSave() {
  const indicator = document.getElementById("autoSaveIndicator");
  if (indicator) {
    indicator.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-spin"></span> Saving...`;
    indicator.classList.remove("text-emerald-400", "border-emerald-500/30", "bg-emerald-950/40");
    indicator.classList.add("text-amber-400", "border-amber-500/30", "bg-amber-950/40");
  }

  clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(async () => {
    collectMetadata();
    try {
      const payload = {
        id: appState.currentProjectId,
        metadata: appState.metadata,
        code_source: appState.code_source,
        format_config: appState.format_config,
        screenshots: appState.screenshots,
        report_data: appState.current_report,
        diagrams: appState.diagrams
      };

      const res = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok && data.project_id) {
        appState.currentProjectId = data.project_id;
        refreshDraftsCount();
        if (indicator) {
          indicator.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Auto-Saved`;
          indicator.classList.remove("text-amber-400", "border-amber-500/30", "bg-amber-950/40");
          indicator.classList.add("text-emerald-400", "border-emerald-500/30", "bg-emerald-950/40");
        }
      }
    } catch (e) {
      console.log("Auto-save sync error:", e);
    }
  }, 1200);
}

// GitHub & Code Analysis
async function analyzeGithubRepo() {
  const url = document.getElementById("githubUrl").value.trim();
  if (!url) {
    alert("Please enter a valid GitHub repository URL.");
    return;
  }

  const btn = document.getElementById("btnAnalyze");
  const origHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Analyzing...`;
  btn.disabled = true;

  try {
    const res = await fetch("/api/analyze-repo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ github_url: url })
    });
    const data = await res.json();

    if (res.ok) {
      if (data.detected_tech_stack && data.detected_tech_stack.length) {
        appState.code_source.detected_tech_stack = data.detected_tech_stack;
        renderTechBadges();
      }
      appState.code_source.readme_content = data.readme_content || "";
      appState.code_source.file_tree_summary = data.file_tree_summary || "";
      appState.code_source.sample_code = data.sample_code || "";
      appState.code_source.github_url = url;
      appState.code_source.files = data.files || [];
      appState.code_source.extracted_symbols = data.extracted_symbols || {};

      if (data.repo_name && (!document.getElementById("metaTitle").value || document.getElementById("metaTitle").value.includes("Disease Prediction"))) {
        document.getElementById("metaTitle").value = data.repo_name.replace(/-/g, " ").replace(/_/g, " ").toUpperCase();
      }

      const sumBox = document.getElementById("repoSummaryBox");
      const sumText = document.getElementById("repoSummaryText");
      sumBox.classList.remove("hidden");
      sumText.textContent = `Repository: ${data.repo_name}\nDescription: ${data.description || 'N/A'}\nTechnologies: ${data.detected_tech_stack.join(', ')}\n\nFiles detected:\n${data.file_tree_summary || 'N/A'}`;
      
      renderRepoCodeExplorer();
      triggerAutoSave();
    } else {
      alert("Analysis error: " + (data.detail || "Could not fetch repository."));
    }
  } catch (err) {
    alert("Failed to connect to server: " + err.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

async function analyzeLocalPath() {
  const path = document.getElementById("localPath").value.trim();
  if (!path) {
    alert("Please enter a local directory path.");
    return;
  }

  try {
    const res = await fetch("/api/analyze-repo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ local_path: path })
    });
    const data = await res.json();
    if (res.ok) {
      if (data.detected_tech_stack) {
        appState.code_source.detected_tech_stack = data.detected_tech_stack;
        renderTechBadges();
      }
      appState.code_source.local_path = path;
      appState.code_source.readme_content = data.readme_content || "";
      appState.code_source.sample_code = data.sample_code || "";
      appState.code_source.files = data.files || [];
      appState.code_source.extracted_symbols = data.extracted_symbols || {};

      const sumBox = document.getElementById("repoSummaryBox");
      const sumText = document.getElementById("repoSummaryText");
      sumBox.classList.remove("hidden");
      sumText.textContent = `Local Folder: ${data.repo_name}\nTechnologies: ${data.detected_tech_stack.join(', ')}\n\nFiles:\n${data.file_tree_summary}`;
      renderRepoCodeExplorer();
      triggerAutoSave();
    } else {
      alert("Error scanning local folder: " + (data.detail || "Path not found"));
    }
  } catch (e) {
    alert("Connection error: " + e.message);
  }
}

function renderRepoCodeExplorer() {
  const explorerCard = document.getElementById("repoCodeExplorerCard");
  const filesList = document.getElementById("repoFilesList");
  if (!explorerCard || !filesList) return;

  const files = appState.code_source.files || [];
  const symbols = appState.code_source.extracted_symbols || { classes: [], functions: [], endpoints: [] };

  if (!files.length) {
    explorerCard.classList.add("hidden");
    return;
  }

  explorerCard.classList.remove("hidden");
  const clsCount = document.getElementById("symbolClassesCount");
  const fnCount = document.getElementById("symbolFunctionsCount");
  const epCount = document.getElementById("symbolEndpointsCount");
  if (clsCount) clsCount.textContent = symbols.classes ? symbols.classes.length : 0;
  if (fnCount) fnCount.textContent = symbols.functions ? symbols.functions.length : 0;
  if (epCount) epCount.textContent = symbols.endpoints ? symbols.endpoints.length : 0;

  filesList.innerHTML = "";
  files.forEach((f, idx) => {
    const item = document.createElement("div");
    item.className = `p-2 rounded-lg cursor-pointer flex items-center justify-between text-xs transition-all ${idx === 0 ? 'bg-indigo-950/60 border border-indigo-500/40 text-white' : 'hover:bg-white/5 text-slate-300'}`;
    item.id = `fileItem-${idx}`;
    item.onclick = () => showFilePreview(f.path, idx);

    item.innerHTML = `
      <div class="flex items-center gap-2 truncate">
        <input type="checkbox" ${f.selected !== false ? 'checked' : ''} onclick="event.stopPropagation(); toggleFileSelection('${f.path}')" class="rounded accent-indigo-500">
        <span class="truncate font-mono">${f.name || f.path}</span>
      </div>
      <span class="text-[10px] text-slate-400 font-mono">${f.line_count || 0}L</span>
    `;
    filesList.appendChild(item);
  });

  if (files.length > 0) {
    showFilePreview(files[0].path, 0);
  }
}

function showFilePreview(filePath, activeIdx = -1) {
  const files = appState.code_source.files || [];
  const file = files.find(f => f.path === filePath);
  if (!file) return;

  const activeName = document.getElementById("activeCodeFileName");
  const activeMeta = document.getElementById("activeCodeMeta");
  const codeBox = document.getElementById("activeCodeSnippet");

  if (activeName) activeName.textContent = file.path;
  if (activeMeta) activeMeta.textContent = `${file.language.toUpperCase()} • ${file.line_count} lines • ${(file.size_bytes / 1024).toFixed(1)} KB`;
  if (codeBox) codeBox.textContent = file.content || file.preview || "No content available.";

  if (activeIdx >= 0) {
    document.querySelectorAll("[id^='fileItem-']").forEach(el => {
      el.className = "p-2 rounded-lg cursor-pointer flex items-center justify-between text-xs transition-all hover:bg-white/5 text-slate-300";
    });
    const selectedEl = document.getElementById(`fileItem-${activeIdx}`);
    if (selectedEl) {
      selectedEl.className = "p-2 rounded-lg cursor-pointer flex items-center justify-between text-xs transition-all bg-indigo-950/60 border border-indigo-500/40 text-white";
    }
  }
}

function toggleFileSelection(filePath) {
  const files = appState.code_source.files || [];
  const file = files.find(f => f.path === filePath);
  if (file) {
    file.selected = !file.selected;
    triggerAutoSave();
  }
}

function renderTechBadges() {
  const container = document.getElementById("techBadgesContainer");
  container.innerHTML = "";
  appState.code_source.detected_tech_stack.forEach(tech => {
    const span = document.createElement("span");
    span.className = "badge-tag cursor-pointer hover:bg-red-500/20";
    span.innerHTML = `${tech} <i data-lucide="x" class="w-3 h-3" onclick="removeTech('${tech}')"></i>`;
    container.appendChild(span);
  });
  lucide.createIcons();
}

function addCustomTech() {
  const input = document.getElementById("newTechInput");
  const val = input.value.trim();
  if (val && !appState.code_source.detected_tech_stack.includes(val)) {
    appState.code_source.detected_tech_stack.push(val);
    renderTechBadges();
    input.value = "";
    triggerAutoSave();
  }
}

function removeTech(tech) {
  appState.code_source.detected_tech_stack = appState.code_source.detected_tech_stack.filter(t => t !== tech);
  renderTechBadges();
  triggerAutoSave();
}

// Format Presets
function selectFormatPreset(presetKey) {
  appState.format_config.preset = presetKey;

  document.querySelectorAll(".format-card").forEach(c => {
    c.classList.remove("border-indigo-500", "bg-indigo-950/20");
    c.classList.add("border-white/10", "bg-slate-900/40");
  });

  const selected = document.getElementById(`card-${presetKey}`);
  if (selected) {
    selected.classList.remove("border-white/10", "bg-slate-900/40");
    selected.classList.add("border-indigo-500", "bg-indigo-950/20");
  }

  const customBox = document.getElementById("customGuidelinesBox");
  if (presetKey === "custom") {
    customBox.classList.remove("hidden");
  }
  triggerAutoSave();
}

// Custom Template .docx Upload Handler
async function handleCustomTemplateUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/upload-template-docx", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.success) {
      appState.custom_template_filename = data.template_filename;
      const statusBox = document.getElementById("uploadedTemplateStatus");
      const nameSpan = document.getElementById("uploadedTemplateName");
      statusBox.classList.remove("hidden");
      nameSpan.textContent = `Using custom template: ${data.original_filename}`;
      triggerAutoSave();
    } else {
      alert("Template upload error: " + (data.detail || "Only .docx allowed"));
    }
  } catch (err) {
    alert("Template upload failed: " + err.message);
  }
}

// Screenshot Upload Handler
async function handleScreenshotUpload(event) {
  const files = event.target.files;
  if (!files || !files.length) return;

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  try {
    const res = await fetch("/api/upload-screenshots", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (res.ok && data.screenshots) {
      appState.screenshots.push(...data.screenshots);
      renderScreenshots();
      triggerAutoSave();
    } else {
      alert("Screenshot upload failed: " + (data.detail || "Invalid format"));
    }
  } catch (err) {
    alert("Upload error: " + err.message);
  }
}

function renderScreenshots() {
  const container = document.getElementById("screenshotsListContainer");
  if (!appState.screenshots.length) {
    container.innerHTML = `<p class="text-xs text-slate-500 italic text-center">No screenshots uploaded yet. Upload at least 1-2 UI/Output pictures to make the report look 100% authentic.</p>`;
    return;
  }

  container.innerHTML = "";
  appState.screenshots.forEach((s, idx) => {
    const card = document.createElement("div");
    card.className = "flex flex-col sm:flex-row items-center gap-4 p-4 rounded-xl bg-slate-900/50 border border-white/10";
    card.innerHTML = `
      <img src="/uploads/${s.filename}" class="w-32 h-20 object-cover rounded-lg border border-white/10" alt="Screenshot ${idx+1}">
      <div class="flex-1 w-full">
        <label class="block text-[11px] font-semibold text-slate-400 uppercase mb-1">Figure Caption</label>
        <input type="text" class="glass-input text-xs" value="${s.caption}" onchange="updateScreenshotCaption('${s.id}', this.value)">
      </div>
      <button type="button" onclick="removeScreenshot('${s.id}')" class="btn-secondary text-red-400 p-2 hover:bg-red-500/20">
        <i data-lucide="trash-2" class="w-4 h-4"></i>
      </button>
    `;
    container.appendChild(card);
  });
  lucide.createIcons();
}

function updateScreenshotCaption(id, newCaption) {
  const item = appState.screenshots.find(s => s.id === id);
  if (item) {
    item.caption = newCaption;
    triggerAutoSave();
  }
}

function removeScreenshot(id) {
  appState.screenshots = appState.screenshots.filter(s => s.id !== id);
  renderScreenshots();
  triggerAutoSave();
}

// Diagram Engine (Mermaid.js)
async function loadProjectDiagrams() {
  collectMetadata();
  const title = appState.metadata.title;
  const tech = appState.code_source.detected_tech_stack;
  const domain = appState.metadata.domain;

  const btn = document.getElementById("btnGenDiagrams");
  if (btn) btn.disabled = true;

  try {
    const res = await fetch("/api/generate-diagrams", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, tech_stack: tech, domain })
    });
    const data = await res.json();
    if (res.ok && data.diagrams) {
      appState.diagrams = data.diagrams;
      renderCurrentDiagram();
      triggerAutoSave();
    }
  } catch (e) {
    console.error("Diagram generation failed:", e);
  } finally {
    if (btn) btn.disabled = false;
  }
}

function switchDiagramTab(tabKey) {
  appState.activeDiagramTab = tabKey;
  ["architecture", "dfd", "sequence", "erd", "flowchart"].forEach(k => {
    const tab = document.getElementById(`dtab-${k}`);
    if (tab) {
      if (k === tabKey) {
        tab.className = "py-1 px-3 rounded-lg bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30";
      } else {
        tab.className = "py-1 px-3 rounded-lg hover:bg-white/10 text-slate-400";
      }
    }
  });
  renderCurrentDiagram();
}

async function renderCurrentDiagram() {
  const container = document.getElementById("mermaidRenderContainer");
  if (!container) return;

  const code = appState.diagrams[appState.activeDiagramTab];
  if (!code) {
    container.innerHTML = `<p class="text-xs text-slate-500 italic">Diagram not compiled yet.</p>`;
    return;
  }

  container.innerHTML = `<div class="mermaid text-xs w-full flex justify-center">${code}</div>`;
  try {
    await mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
  } catch (err) {
    console.error("Mermaid rendering error:", err);
  }
}

// Generate Full Production Report
async function startReportGeneration() {
  collectMetadata();
  appState.code_source.code_text = document.getElementById("pastedCode").value.trim();
  appState.format_config.custom_guidelines = document.getElementById("customFormatText").value.trim();

  const btn = document.getElementById("btnGenerateReport");
  const origHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Synthesizing Humanized Dissertation...`;
  btn.disabled = true;

  const payload = {
    metadata: appState.metadata,
    code_source: appState.code_source,
    screenshots: appState.screenshots,
    format_config: appState.format_config,
    llm_config: appState.llm_config
  };

  try {
    const res = await fetch("/api/generate-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.success) {
      appState.current_report = data.report;
      switchStep(5);
      renderDocumentPaper(data.report);
      triggerAutoSave();
    } else {
      alert("Report generation failed: " + (data.detail || "Server error"));
    }
  } catch (err) {
    alert("Generation connection error: " + err.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

// Render Document Paper View
function renderDocumentPaper(report) {
  const paper = document.getElementById("documentPaper");
  const meta = report.metadata;
  const tocNav = document.getElementById("tocNav");

  let navHtml = `
    <a href="#sectionCover" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300">Cover Page</a>
    <a href="#sectionCert" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300">Certificate</a>
    <a href="#sectionDecl" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300">Declaration</a>
    <a href="#sectionAck" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300">Acknowledgement</a>
    <a href="#sectionAbstract" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300">Abstract</a>
  `;

  report.chapters.forEach(ch => {
    navHtml += `<a href="#ch_${ch.id}" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300 truncate">${ch.title}</a>`;
  });
  navHtml += `<a href="#sectionRef" class="block py-1.5 px-2.5 rounded hover:bg-white/10 text-slate-300">References</a>`;
  tocNav.innerHTML = navHtml;

  let html = `
    <!-- COVER PAGE -->
    <div id="sectionCover" class="text-center py-10 border-b-2 border-slate-200 mb-12">
      <h1 id="paperTitle" class="text-3xl font-bold uppercase tracking-wider text-slate-900 mb-4 focus:outline-none focus:ring-2 focus:ring-amber-400 p-1 rounded">${meta.title}</h1>
      <p class="text-sm font-bold tracking-widest text-slate-700 uppercase mb-2">A PROJECT REPORT</p>
      <p class="text-xs italic text-slate-600 mb-2">Submitted in partial fulfillment of the requirements for the award of the degree of</p>
      <p class="text-base font-bold text-slate-900 uppercase mb-8">${meta.degree}</p>

      <div class="my-6">
        <p class="text-xs font-bold uppercase text-slate-700 mb-2">Submitted by:</p>
        <div class="inline-block border border-slate-300 rounded overflow-hidden text-xs">
          <table class="min-w-[320px] text-left">
            <thead class="bg-slate-100 font-bold border-b border-slate-300">
              <tr>
                <th class="p-2">Candidate Name</th>
                <th class="p-2">Roll No. / USN</th>
              </tr>
            </thead>
            <tbody>
              ${meta.students.map(s => `<tr><td class="p-2 border-b border-slate-200">${s.name}</td><td class="p-2 border-b border-slate-200 font-mono">${s.roll_no}</td></tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <div class="my-6">
        <p class="text-xs italic text-slate-600">Under the Guidance of</p>
        <p class="text-sm font-bold text-slate-900">${meta.guide_name}</p>
        <p class="text-xs text-slate-600">${meta.guide_designation}</p>
      </div>

      <div class="mt-8 pt-4 border-t border-slate-200">
        <p id="paperDept" class="text-sm font-bold uppercase text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-400 p-0.5 rounded">${meta.department}</p>
        <p id="paperCollege" class="text-sm font-bold uppercase text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-400 p-0.5 rounded">${meta.college_name}</p>
        <p class="text-xs italic text-slate-600 mb-1">(Affiliated to ${meta.university_name || 'State Technological University'})</p>
        <p class="text-xs font-bold text-slate-700">Academic Year: ${meta.academic_year}</p>
      </div>
    </div>

    <!-- CERTIFICATE -->
    <div id="sectionCert" class="py-8 border-b border-slate-200 mb-10">
      <h2 class="text-xl font-bold uppercase text-center mb-6">CERTIFICATE</h2>
      <p class="text-justify text-sm leading-relaxed mb-8">
        This is to certify that the project report entitled <strong>"${meta.title}"</strong>, submitted by 
        <strong>${meta.students.map(s => `${s.name} (${s.roll_no})`).join(', ')}</strong> in partial fulfillment 
        of the requirements for the award of the degree of <strong>${meta.degree}</strong> from 
        <strong>${meta.college_name}</strong>, is a bona fide record of work carried out by them under my supervision and guidance.
      </p>
      <div class="grid grid-cols-3 text-center text-xs mt-12 gap-4">
        <div>
          <p class="border-t border-slate-400 pt-2 font-bold">${meta.guide_name}</p>
          <p class="text-slate-600">Guide Signature</p>
        </div>
        <div>
          <p class="border-t border-slate-400 pt-2 font-bold">${meta.hod_name || 'Head of Dept'}</p>
          <p class="text-slate-600">HOD Signature</p>
        </div>
        <div>
          <p class="border-t border-slate-400 pt-2 font-bold">${meta.principal_name || 'Principal'}</p>
          <p class="text-slate-600">Principal Signature</p>
        </div>
      </div>
    </div>

    <!-- ABSTRACT -->
    <div id="sectionAbstract" class="py-8 border-b border-slate-200 mb-10">
      <h2 class="text-xl font-bold uppercase text-center mb-6">ABSTRACT</h2>
      <div id="paperAbstract" class="text-justify text-sm leading-relaxed whitespace-pre-line mb-4 focus:outline-none focus:ring-2 focus:ring-amber-400 p-2 rounded">${report.abstract}</div>
      <p class="text-xs font-bold mt-4">Keywords: <span class="italic font-normal">${report.keywords.join(', ')}</span></p>
    </div>
  `;

  let figCount = 1;
  report.chapters.forEach(ch => {
    html += `
      <div id="ch_${ch.id}" class="py-8 border-b border-slate-200 mb-10">
        <h2 data-ch-title="${ch.id}" class="text-xl font-bold uppercase text-slate-900 mb-4 pb-2 border-b-2 border-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-400 p-1 rounded">${ch.title}</h2>
        ${ch.summary ? `<p class="text-sm italic text-slate-700 mb-6">${ch.summary}</p>` : ''}
    `;

    ch.subsections.forEach((sub, subIdx) => {
      html += `
        <div class="mb-6">
          <h3 class="text-base font-bold text-slate-900 mb-2">${sub.heading}</h3>
          <div data-ch-sub-content="${ch.id}" data-sub-idx="${subIdx}" class="text-sm text-justify leading-relaxed whitespace-pre-line mb-3 focus:outline-none focus:ring-2 focus:ring-amber-400 p-2 rounded">${sub.content}</div>
      `;

      if (sub.code_snippet) {
        html += `
          <div class="my-4 p-3 bg-slate-100 border border-slate-300 rounded font-mono text-xs overflow-x-auto text-slate-800">
            <pre>${sub.code_snippet}</pre>
          </div>
        `;
      }

      if (sub.table_data && sub.table_data.headers) {
        html += `
          <div class="my-4 overflow-x-auto">
            <table class="w-full text-xs border border-slate-300 border-collapse">
              <thead class="bg-slate-200 font-bold">
                <tr>${sub.table_data.headers.map(h => `<th class="border border-slate-300 p-2 text-left">${h}</th>`).join('')}</tr>
              </thead>
              <tbody>
                ${sub.table_data.rows.map(r => `<tr>${r.map(c => `<td class="border border-slate-300 p-2">${c}</td>`).join('')}</tr>`).join('')}
              </tbody>
            </table>
          </div>
        `;
      }

      html += `</div>`;
    });

    const isResults = ch.title.toLowerCase().includes("result") || ch.title.toLowerCase().includes("screenshot") || ch.title.toLowerCase().includes("experiment");
    if (isResults && report.screenshots && report.screenshots.length) {
      report.screenshots.forEach(sc => {
        html += `
          <div class="my-6 text-center">
            <img src="/uploads/${sc.filename}" class="max-w-[85%] mx-auto rounded border border-slate-300 shadow-sm" alt="${sc.caption}">
            <p class="text-xs italic font-bold text-slate-600 mt-2">Figure ${ch.id}.${figCount++}: ${sc.caption}</p>
          </div>
        `;
      });
    }

    html += `</div>`;
  });

  html += `
    <div id="sectionRef" class="py-8">
      <h2 class="text-xl font-bold uppercase text-center mb-6">REFERENCES</h2>
      <div class="space-y-3 text-xs text-justify">
        ${report.references.map((r, i) => `<p class="pl-6 -indent-6">${r.startsWith('[') ? r : `[${i+1}] ${r}`}</p>`).join('')}
      </div>
    </div>
  `;

  paper.innerHTML = html;

  // Re-apply direct edit mode if active
  if (isDirectEditOn) {
    paper.contentEditable = "true";
  }
}

// Direct In-Place Edit Mode State
let isDirectEditOn = false;

function toggleDirectEditMode() {
  isDirectEditOn = !isDirectEditOn;
  const paper = document.getElementById("documentPaper");
  const btn = document.getElementById("btnToggleEdit");
  const label = document.getElementById("editModeLabel");

  if (isDirectEditOn) {
    paper.contentEditable = "true";
    paper.classList.add("ring-4", "ring-amber-400/50");
    btn.classList.add("border-amber-400", "text-amber-300");
    label.textContent = "Direct Edit: ON";

    const noticeBox = document.getElementById("revisionNoticeBox");
    const noticeText = document.getElementById("revisionNoticeText");
    noticeBox.classList.remove("hidden");
    noticeText.textContent = "✏️ Direct Edit Mode is ON! Click and edit any title, abstract, or paragraph directly. All edits save to PDF & DOCX instantly!";
  } else {
    paper.contentEditable = "false";
    paper.classList.remove("ring-4", "ring-amber-400/50");
    btn.classList.remove("border-amber-400", "text-amber-300");
    label.textContent = "Direct Edit: OFF";
    syncDirectEditsToReport();

    const noticeBox = document.getElementById("revisionNoticeBox");
    const noticeText = document.getElementById("revisionNoticeText");
    noticeBox.classList.remove("hidden");
    noticeText.textContent = "✓ In-place edits saved to memory & database.";
  }
}

function syncDirectEditsToReport() {
  if (!appState.current_report) return;

  const titleEl = document.getElementById("paperTitle");
  if (titleEl && titleEl.innerText.trim()) {
    appState.current_report.metadata.title = titleEl.innerText.trim();
  }

  const deptEl = document.getElementById("paperDept");
  if (deptEl && deptEl.innerText.trim()) {
    appState.current_report.metadata.department = deptEl.innerText.trim();
  }

  const collegeEl = document.getElementById("paperCollege");
  if (collegeEl && collegeEl.innerText.trim()) {
    appState.current_report.metadata.college_name = collegeEl.innerText.trim();
  }

  const absEl = document.getElementById("paperAbstract");
  if (absEl && absEl.innerText.trim()) {
    appState.current_report.abstract = absEl.innerText.trim();
  }

  // Chapter titles
  document.querySelectorAll("[data-ch-title]").forEach(el => {
    const chId = parseInt(el.getAttribute("data-ch-title"));
    const ch = appState.current_report.chapters.find(c => c.id === chId);
    if (ch && el.innerText.trim()) {
      ch.title = el.innerText.trim();
    }
  });

  // Subsection contents
  document.querySelectorAll("[data-ch-sub-content]").forEach(el => {
    const chId = parseInt(el.getAttribute("data-ch-sub-content"));
    const subIdx = parseInt(el.getAttribute("data-sub-idx"));
    const ch = appState.current_report.chapters.find(c => c.id === chId);
    if (ch && ch.subsections && ch.subsections[subIdx] && el.innerText.trim()) {
      ch.subsections[subIdx].content = el.innerText.trim();
    }
  });

  triggerAutoSave();
}

// Prompt Revision Engine
function setPromptSuggestion(text) {
  document.getElementById("userRevisionPrompt").value = text;
}

async function submitPromptRevision() {
  const promptInput = document.getElementById("userRevisionPrompt");
  const promptText = promptInput.value.trim();
  if (!promptText) {
    alert("Please enter a prompt describing the changes you want.");
    return;
  }

  if (!appState.current_report) {
    alert("No report has been generated yet.");
    return;
  }

  // Sync any on-screen edits before sending revision prompt
  syncDirectEditsToReport();

  const btn = document.getElementById("btnRevise");
  const origHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Revising with AI...`;
  btn.disabled = true;

  const payload = {
    report: appState.current_report,
    prompt: promptText,
    target_section: "all",
    llm_config: appState.llm_config
  };

  try {
    const res = await fetch("/api/revise-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.success) {
      appState.current_report = data.updated_report;
      renderDocumentPaper(data.updated_report);

      const noticeBox = document.getElementById("revisionNoticeBox");
      const noticeText = document.getElementById("revisionNoticeText");
      noticeBox.classList.remove("hidden");
      noticeText.textContent = "✓ " + (data.revision_summary || "Report updated based on your prompt.");

      promptInput.value = "";
      triggerAutoSave();
      window.scrollTo({ top: document.getElementById("stepSection5").offsetTop, behavior: "smooth" });
    } else {
      alert("Revision error: " + (data.message || data.detail || "Server error"));
    }
  } catch (err) {
    alert("Failed to revise report: " + err.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

// Download University PDF
async function downloadReportPdf() {
  if (!appState.current_report) {
    alert("Please generate a report first.");
    return;
  }

  syncDirectEditsToReport();

  const btn = document.getElementById("btnDownloadPdf");
  const origHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Rendering University PDF...`;
  btn.disabled = true;

  try {
    const res = await fetch("/api/download-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        report: appState.current_report
      })
    });

    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeTitle = (appState.current_report.metadata.title || "Project_Report").replace(/[^a-zA-Z0-9_-]/g, "_");
      a.download = `${safeTitle}_Report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } else {
      const err = await res.json();
      alert("PDF generation error: " + (err.detail || "Failed to compile PDF document"));
    }
  } catch (err) {
    alert("PDF download failed: " + err.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

// Download .docx File (Supports Custom Template)
async function downloadReportDocx() {
  if (!appState.current_report) {
    alert("Please generate a report first.");
    return;
  }

  syncDirectEditsToReport();

  const btn = document.getElementById("btnDownloadDocx");
  const origHtml = btn.innerHTML;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Compiling DOCX...`;
  btn.disabled = true;

  try {
    const res = await fetch("/api/download-docx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        report: appState.current_report,
        custom_template_filename: appState.custom_template_filename
      })
    });

    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeTitle = (appState.current_report.metadata.title || "Project_Report").replace(/[^a-zA-Z0-9_-]/g, "_");
      a.download = `${safeTitle}_Report.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } else {
      const err = await res.json();
      alert("Download error: " + (err.detail || "Failed to generate Word document"));
    }
  } catch (err) {
    alert("Download failed: " + err.message);
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
    lucide.createIcons();
  }
}

// Saved Projects / Drafts Modal (SQLite)
async function openProjectsModal() {
  const container = document.getElementById("projectsListContainer");
  container.innerHTML = `<p class="text-center text-slate-400 py-6">Loading drafts from database...</p>`;
  document.getElementById("projectsModal").classList.remove("hidden");
  lucide.createIcons();

  try {
    const res = await fetch("/api/projects");
    const data = await res.json();
    if (res.ok && data.projects) {
      if (!data.projects.length) {
        container.innerHTML = `<p class="text-center text-slate-400 py-6 italic">No saved drafts found yet. Start typing to create your first draft!</p>`;
        return;
      }
      container.innerHTML = "";
      data.projects.forEach(p => {
        const item = document.createElement("div");
        item.className = "p-3 rounded-xl bg-slate-900/60 border border-white/10 flex items-center justify-between gap-3 hover:border-indigo-400/40 transition-all";
        const dateStr = new Date(p.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        item.innerHTML = `
          <div class="flex-1 truncate">
            <h4 class="font-bold text-white truncate text-xs">${p.title || 'Untitled Project'}</h4>
            <p class="text-[10px] text-slate-400">${p.degree || ''} • ${dateStr}</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="loadProjectDraft('${p.id}')" class="btn-primary text-[11px] py-1 px-2.5">
              Load Draft
            </button>
            <button onclick="deleteProjectDraft('${p.id}', event)" class="btn-secondary text-red-400 p-1.5 hover:bg-red-500/20">
              <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        `;
        container.appendChild(item);
      });
      lucide.createIcons();
    }
  } catch (e) {
    container.innerHTML = `<p class="text-center text-red-400 py-4 text-xs">Failed to load drafts: ${e.message}</p>`;
  }
}

function closeProjectsModal() {
  document.getElementById("projectsModal").classList.add("hidden");
}

async function loadProjectDraft(projectId) {
  try {
    const res = await fetch(`/api/projects/${projectId}`);
    const data = await res.json();
    if (res.ok && data.id) {
      appState.currentProjectId = data.id;
      if (data.metadata) {
        appState.metadata = data.metadata;
        document.getElementById("metaTitle").value = data.metadata.title || "";
        document.getElementById("metaDomain").value = data.metadata.domain || "";
        document.getElementById("metaDegree").value = data.metadata.degree || "";
        document.getElementById("metaDepartment").value = data.metadata.department || "";
        document.getElementById("metaCollege").value = data.metadata.college_name || "";
        document.getElementById("metaUniversity").value = data.metadata.university_name || "";
        document.getElementById("metaGuide").value = data.metadata.guide_name || "";
        document.getElementById("metaHOD").value = data.metadata.hod_name || "";
        document.getElementById("metaYear").value = data.metadata.academic_year || "";

        // Populate students
        const container = document.getElementById("studentsContainer");
        container.innerHTML = "";
        (data.metadata.students || [{ name: "Student", roll_no: "101" }]).forEach(s => {
          const row = document.createElement("div");
          row.className = "student-row flex flex-col sm:flex-row gap-3 items-center";
          row.innerHTML = `
            <input type="text" class="glass-input student-name" value="${s.name}" onchange="triggerAutoSave()">
            <input type="text" class="glass-input student-roll" value="${s.roll_no}" onchange="triggerAutoSave()">
            <button type="button" onclick="removeStudentRow(this)" class="btn-secondary text-red-400 p-2 hover:bg-red-500/20">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          `;
          container.appendChild(row);
        });
      }

      if (data.code_source) {
        appState.code_source = data.code_source;
        renderTechBadges();
        renderRepoCodeExplorer();
      }
      if (data.screenshots) {
        appState.screenshots = data.screenshots;
        renderScreenshots();
      }
      if (data.diagrams) {
        appState.diagrams = data.diagrams;
      }
      if (data.report_data && Object.keys(data.report_data).length) {
        appState.current_report = data.report_data;
        renderDocumentPaper(data.report_data);
      }

      closeProjectsModal();
      lucide.createIcons();
    }
  } catch (err) {
    alert("Error loading draft: " + err.message);
  }
}

async function deleteProjectDraft(projectId, event) {
  event.stopPropagation();
  if (!confirm("Are you sure you want to delete this saved project draft?")) return;

  try {
    const res = await fetch(`/api/projects/${projectId}`, { method: "DELETE" });
    if (res.ok) {
      openProjectsModal();
      refreshDraftsCount();
    }
  } catch (e) {
    alert("Delete failed: " + e.message);
  }
}

function createNewProjectDraft() {
  appState.currentProjectId = null;
  appState.current_report = null;
  document.getElementById("metaTitle").value = "";
  document.getElementById("githubUrl").value = "";
  document.getElementById("pastedCode").value = "";
  appState.screenshots = [];
  renderScreenshots();
  closeProjectsModal();
  switchStep(1);
}

async function refreshDraftsCount() {
  try {
    const res = await fetch("/api/projects");
    const data = await res.json();
    if (res.ok && data.projects) {
      const badge = document.getElementById("draftCountBadge");
      if (badge) badge.textContent = data.projects.length;
    }
  } catch (e) {}
}

// Settings Modal
function openSettingsModal() {
  document.getElementById("modalProviderSelect").value = appState.llm_config.provider;
  document.getElementById("modalApiKey").value = appState.llm_config.api_key;
  document.getElementById("modalModelName").value = appState.llm_config.model_name;
  handleProviderChange();
  document.getElementById("settingsModal").classList.remove("hidden");
  lucide.createIcons();
}

function closeSettingsModal() {
  document.getElementById("settingsModal").classList.add("hidden");
}

function handleProviderChange() {
  const provider = document.getElementById("modalProviderSelect").value;
  const keyGroup = document.getElementById("apiKeyGroup");
  if (provider === "offline") {
    keyGroup.classList.add("hidden");
  } else {
    keyGroup.classList.remove("hidden");
  }
}

function switchToOfflineMode() {
  document.getElementById("modalProviderSelect").value = "offline";
  document.getElementById("modalApiKey").value = "";
  document.getElementById("modalModelName").value = "";
  handleProviderChange();
  saveSettings();
}

function updateProviderLabel() {
  const label = document.getElementById("currentProviderLabel");
  if (!label) return;
  if (appState.llm_config.provider === "offline" || !appState.llm_config.api_key) {
    label.textContent = "AI: 100% Free Mode";
  } else {
    label.textContent = `AI: ${appState.llm_config.provider.toUpperCase()} (Connected)`;
  }
}

function saveSettings() {
  appState.llm_config.provider = document.getElementById("modalProviderSelect").value;
  appState.llm_config.api_key = document.getElementById("modalApiKey").value.trim();
  appState.llm_config.model_name = document.getElementById("modalModelName").value.trim();

  localStorage.setItem("scholarforge_llm_config", JSON.stringify(appState.llm_config));
  updateProviderLabel();
  closeSettingsModal();
}

function loadSavedSettings() {
  const saved = localStorage.getItem("scholarforge_llm_config");
  if (saved) {
    try {
      appState.llm_config = JSON.parse(saved);
    } catch (e) {}
  }
  updateProviderLabel();
}

async function testApiKey() {
  const provider = document.getElementById("modalProviderSelect").value;
  const key = document.getElementById("modalApiKey").value.trim();
  const model = document.getElementById("modalModelName").value.trim();
  const resElem = document.getElementById("keyTestResult");
  const btn = document.getElementById("btnTestKey");

  resElem.classList.remove("hidden", "text-emerald-400", "text-rose-400");
  resElem.textContent = "Testing connection...";
  btn.disabled = true;

  try {
    const res = await fetch("/api/test-api-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, api_key: key, model_name: model })
    });
    const data = await res.json();
    if (data.valid) {
      resElem.classList.add("text-emerald-400");
      resElem.textContent = "✓ " + data.message;
    } else {
      resElem.classList.add("text-rose-400");
      resElem.textContent = "✕ " + data.message;
    }
  } catch (err) {
    resElem.classList.add("text-rose-400");
    resElem.textContent = "Connection failed: " + err.message;
  } finally {
    btn.disabled = false;
  }
}

function toggleHelpModal() {
  const modal = document.getElementById("helpModal");
  modal.classList.toggle("hidden");
  lucide.createIcons();
}
