# ScholarForge AI - Production University Project Report Generator 🎓📄 (v2.0)

> **Enterprise Production-Grade Academic Report Studio**: Auto-generate complete, authentic, Turnitin-compliant university dissertation reports from GitHub repositories, local code, and screenshots with auto-generated UML & DFD diagrams, natural-language prompt editing, custom Word template injection, and dual .docx / PDF export.

---

## 🌟 What's New in Production v2.0 (Based on User Requirements)

1. **Custom College .docx Template Injection**:
   - Students can upload their college's official Word template (`sample_format.docx`).
   - The engine replaces placeholders (`{{PROJECT_TITLE}}`, `{{STUDENT_NAMES}}`, `{{GUIDE_NAME}}`, etc.) AND preserves the college's exact cover page, borders, and margins while injecting generated chapters!
2. **Auto-Generated Mermaid.js Architecture & Flowcharts**:
   - Auto-generates **High-Level System Architecture**, **DFD Level 1 (Data Flow Diagram)**, **UML Sequence Diagram**, **Database ER Diagram**, and **Process Flowcharts** directly from the project's tech stack and code!
3. **SQLite Database Drafts & LocalStorage Auto-Save**:
   - Every keystroke and prompt revision is automatically debounced and persisted into SQLite (`data/scholarforge.db`).
   - "My Drafts" drawer lets students save multiple projects, switch between them, and resume work anytime without losing data.
4. **Academic Humanized Mode (Turnitin & AI-Detector Friendly)**:
   - Eliminates AI clichés ("In today's digital era", "delve into", "crucial", "revolutionize").
   - Implements varied syntactic structures (short assertions mixed with compound scholarly rationale), concrete telemetry metrics (latencies in ms, O(N log N) complexities), mathematical objective functions, and realistic IEEE citations.
5. **Production Cloud & Docker Deployment**:
   - Containerized with multi-stage `Dockerfile` and `docker-compose.yml`.
   - 1-Click Cloud Deployment ready for **Render** (`render.yaml`), **Railway** (`Procfile`), or AWS.
   - Built-in `/health` monitoring endpoint.

---

## 🚀 Deployment & Launch Options

### Option 1: One-Click Local Launch (Windows)
Double-click:
```bat
start.bat
```
Server launches automatically and opens **`http://127.0.0.1:8000`** in your browser.

### Option 2: Docker Container (Production)
```bash
docker-compose up -d
```
Runs isolated with persistent volumes for `./data` and `./uploads`.

### Option 3: Free Cloud Deployment (Render / Railway)
- **Render**: Connect your GitHub repository; Render detects `render.yaml` automatically and provisions a free public web service with SSL (`https://your-app.onrender.com`).
- **Railway / Heroku**: Uses `Procfile` and binds automatically to `$PORT`.

---

## 📖 Complete Workflow

1. **Step 1: College & Team Metadata**: Enter Project Title, Degree, Department, College, Guide Name, and student names with Roll Numbers / USNs.
2. **Step 2: Code & Repository**: Paste your public GitHub URL and click **"⚡ Auto-Analyze Repo"** to auto-extract the tech stack, README, and project architecture.
3. **Step 3: University Format or Custom .docx Template**: Choose a standard preset (General B.Tech, VTU, AKTU, BCA/MCA, IEEE) OR upload your college's official `.docx` file!
4. **Step 4: Diagrams & Screenshots**: Inspect the auto-generated Mermaid Architecture, DFD, Sequence, and ER diagrams. Upload project UI screenshots and assign figure captions.
5. **Step 5: Synthesize & Prompt Revisions**: Click **"🚀 Generate Production Academic Report"**. Review the live preview paper, and use the bottom AI prompt bar to make revisions on the fly!
6. **Download**: Click **"📥 Download University .docx"** or **"Print to PDF"**.
