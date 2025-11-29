import os

readme_content = r"""# 🚀 Universal Converter Pro (Modular & Dual AI)

**Universal Converter Pro** is a robust, modular desktop application designed to scrape **Web Documentation** and convert **PDF Files** into clean, structured **Markdown**.

Optimized for **RAG (Retrieval-Augmented Generation)** workflows, it features a **Dual AI Engine** (Google Gemini & OpenAI GPT) to intelligently filter crawl paths and reformat complex PDF documents, ensuring high-quality data extraction.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![AI Powered](https://img.shields.io/badge/AI-Gemini%20%7C%20GPT--4o-orange?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Modular-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Key Features

### 🧠 Dual AI Engine
* **Multi-Provider:** Seamlessly switch between **Google Gemini** (Flash/Pro) and **OpenAI** (GPT-4o/Turbo).
* **Smart Caching:** Automatically fetches and caches available models for your API key.
* **Prompt Engineering:** Built-in editor to customize AI instructions for both crawling and PDF cleaning.

### 🌍 Intelligent Web Crawler
* **Smart Filter (Heuristic):** Fast filtering based on customizable keywords (e.g., keep "manual", discard "login").
* **AI Filter (Semantic):** Uses LLMs to analyze link context (e.g., "Is this a documentation page?").
* **Deep Control:** Configurable recursion depth and strict domain locking.

### 📄 Advanced PDF Converter
* **Raw Text:** Instant extraction using `PyMuPDF`.
* **AI Reformatting:** Uses AI to read pages, fix broken sentences, remove headers/footers, and format tables into Markdown.
* **Auto-Discard:** Intelligently ignores irrelevant pages (Index, Copyright, Ads).

### 🛠️ Modern GUI & Architecture
* **Modular Codebase:** Clean separation of concerns (`ui`, `engine`, `utils`, `settings`).
* **Dual Logging:** Separate tabs for "Process" (info) and "Discarded" (debug/rejected items).
* **Persistence:** Automatically saves API keys, preferred models, and UI state to `config.json`.

---

## 📂 Project Structure

The project is organized into a clean modular structure under `src/`:

```text
UniversalConverterPro/
├── data/                # Auto-generated output folders (docs_web, docs_pdf)
├── src/                 # Source Code
│   ├── __init__.py      # Package initializer
│   ├── main.py          # Application Entry Point (Launcher)
│   ├── app_ui.py        # GUI Logic & Threading (Tkinter)
│   ├── ai_engine.py     # AI Handlers (Gemini/OpenAI adapters)
│   ├── settings.py      # Configuration & JSON Management
│   └── utils.py         # Helper functions (File cleaning, Heuristics)
├── config.json          # User Settings (Auto-generated on first run)
└── requirements.txt     # Project Dependencies