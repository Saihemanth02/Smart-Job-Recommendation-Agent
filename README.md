# Smart Job Recommendation Agent

The **Smart Job Recommendation Agent** (Career Advisor) is a production-grade career assessment tool. It employs a team of 8 specialized AI agents coordinating via a custom Agent-to-Agent (A2A) message protocol. The tool uses offline machine learning models (Multinomial Naive Bayes & Random Forest ensembles) to recommend job roles and project salary ranges, and uses LLM backends (Groq with Gemini fallbacks) to write custom roadmaps, cover letters, and practice interview questions.

---

## 🛠️ Project Setup & Installation

### 1. Initialize Virtual Environment
Configure a virtual environment using Python 3.11+:
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Secrets Configuration
Create a `.env` file in the project root:
```bash
cp .env.example .env
```
Open `.env` and fill in your LLM access keys:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🧠 Seed Generation & Model Training

Before launching the web portal, you must generate the synthetic dataset and train the offline classifiers:

### 1. Run Data Seed Generator
Generates ~800 synthetic Indian candidates and 1,000 salary records with regional colleges (JNTU, GVP) and skills taxonomy rules:
```bash
python data/seed_generator.py
```

### 2. Train Job Classifier Models
Trains Naive Bayes for coarse categories and Random Forest for fine-grained roles:
```bash
python ml/train_job_classifier.py
```

### 3. Train Salary Regressor Model
Trains a Random Forest Regressor on job metrics and encodes location/cert features:
```bash
python ml/train_salary_model.py
```

---

## 🚀 Running the Web Portal

To launch the portal locally, execute:
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Standalone Executable Packaging (Windows)

We compile the entire application, SQLite DB, models, and dependencies into a single `run.exe` binary:

### 1. Compile standard app spec
Run the bundled build script:
```bash
build\build_exe.bat
```
This builds `dist/run.exe`.

### ⚠️ Streamlit PyInstaller Caveats
Streamlit uses static files (`static/` and `runtime/` directories) which are sometimes missed or misaligned in older versions of PyInstaller.
- **Pin versions:** Streamlit is pinned to `1.32.0` in `requirements.txt` which has been validated against `app.spec`.
- **Known Fix:** If the compiled `dist/run.exe` launches a blank screen or fails to load UI assets, locate your streamlit install folder inside your python venv (e.g. `venv/Lib/site-packages/streamlit/static`) and manually copy the entire `static` folder into your `dist/_internal/streamlit/` directory.

---

## 🔍 Quality & Architecture Checklist

- **A2A Activity panel:** Live trace monitor on Page 2 displays JSON packets of each agent.
- **Confidence meters:** Real-time fit percentages and standard-deviation salary bounds on Page 3.
- **Explainability:** Seaborn feature importances are dynamically mapped to active resume signals on Page 3.
- **ATS Auditing:** Paste target job descriptions in Page 6 to compute ATS keyword overlap, compile bullet rewrites, and draft cover letters.
- **Conversational Chat:** Directly text the Career Advisor orchestrator on Page 6 with free-form queries about your report.
