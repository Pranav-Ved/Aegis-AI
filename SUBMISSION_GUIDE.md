# 🐙 AegisAI — GitHub Submission Guide

This guide details step-by-step instructions on how to initialize, commit, and push the AegisAI Disaster Management Platform code to a private or public GitHub repository.

---

## ⚡ Step 1: Initialize Git Repository

1. Open your terminal (PowerShell, Git Bash, or Command Prompt).
2. Navigate to the root directory `D:\AegisAI`:
   ```bash
   cd D:\AegisAI
   ```
3. Initialize a new local Git repository:
   ```bash
   git init
   ```

---

## 📦 Step 2: Stage & Commit Files

1. Add all project files to Git staging. The `.gitignore` file is already pre-configured to automatically exclude `node_modules`, python virtual environments (`.venv`), temporary PDF logs, and your active `.env` file containing local API credentials:
   ```bash
   git add .
   ```
2. Verify the list of staged files to ensure no sensitive credentials or modules are tracked:
   ```bash
   git status
   ```
3. Commit the code with a descriptive commit message:
   ```bash
   git commit -m "feat: complete AegisAI multi-agent disaster platform core implementation"
   ```

---

## 🔗 Step 3: Link to Remote Repository

1. Go to [GitHub](https://github.com) and log in.
2. Click the **New** button to create a new repository:
   - **Repository Name:** `AegisAI`
   - **Description:** `AI-powered multi-agent disaster response platform using Google ADK & Gemini`
   - **Visibility:** Public or Private (depending on your choice)
   - **Initialize this repository with:** *Do NOT select README, .gitignore, or license (they are already present in the workspace).*
3. Copy the remote repository URL (e.g., `https://github.com/your-username/AegisAI.git`).
4. Link the local repository to your remote GitHub repository:
   ```bash
   git remote add origin https://github.com/your-username/AegisAI.git
   ```
5. Rename the default branch to `main`:
   ```bash
   git branch -M main
   ```

---

## 🚀 Step 4: Push to GitHub

1. Push your local main branch to remote:
   ```bash
   git push -u origin main
   ```

---

## 🛡️ Pre-Push Quality Checklist

Before pushing, verify that the project is completely ready:
1. **Compilation Check:** Every backend python file was successfully compiled using Python's `compileall` compiler utility:
   ```bash
   python -m compileall backend/app
   ```
2. **Frontend Production Build:** The Next.js frontend has built successfully:
   ```bash
   npm run build --prefix frontend
   ```
3. **No Committed API Keys:** Ensure your `.env` contains no hardcoded keys or production secrets (all files are configured to fall back to safe local mock states).
