# 🚀 Automated Batch-Renaming System with Sequential Patterns and Varied Sorting Methods

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Framework](https://img.shields.io/badge/UI_Framework-CustomTkinter-orange.svg)](https://github.com/tomsimonson/customtkinter)
[![Academic Project](https://img.shields.io/badge/Course-Advanced_Web_Programming-purple.svg)](https://github.com/RhainyAulia)

An advanced desktop utility built with Python and CustomTkinter engineered to automate file organization through hierarchical multi-criteria sorting and structured batch renaming. This application directly resolves typical digital workspace issues such as inconsistent naming conventions, unorganized structures, and high human-error risk in manual file management.

---

## ✨ Features

### 🔍 Advanced Sorting Architecture
* **Single Attribute Sorting:** Instantly arrange target files using individual attributes: Alphabetical (A-Z/Z-A), Modification Date, Creation Date, File Size, or File Extension.
* **Multi-Criteria Tiered Sorting:** Allows users to define custom execution priorities and combine multiple sorting attributes dynamically for multi-level hierarchical ordering.

### 🧠 Smart Renaming Engine
* **Pattern Configurations:** Supports flexible formatting styles including Sequential Rename, Custom Prefixes, Custom Suffixes, Text Appending/Prepending, and Text Replacement.
* **Serialized Control:** Integrates a structured Number-Only mode and precise word-boundary pattern processing to securely manage formatting states.

### 🛡️ System Operations & Safety Gates
* **Live Action Preview:** Provides real-time generation feedback of the new file structure configurations prior to execution.
* **Undo / Rollback State Engine:** Uses persistent history states to safely revert executed batch-naming processes back to their exact previous naming attributes.
* **Conflict & Collision Detection:** Runs background checking loops to intercept file overwrites and naming duplications before mutations occur.

---

## 🛠️ Tech Stack Layer

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Custom Tkinter | Constructs the application UI, handles user entry forms, and displays the reactive rename tables. |
| **Backend** | Python | Orchestrates the primary application control, routes inputs, and drives the structural file logic. |
| **File Processing** | Pathlib | Operates dynamic system directory reads, extracts metadata, and maps target path mutations. |
| **Packaging** | PyInstaller | Compiles the multi-component modular structure into a clean standalone `.exe` desktop application. |
| **Data Storage** | JSON | Stores transactional history parameters utilized to run accurate Undo/Rollback procedures. |

---

## 📂 Project Directory Structure

```text
batch-renamer/
├── core/               # Backend Logic Layer (Algorithmic Processing Engines)
│   └── renaming.py     # Multi-Criteria Sorting & Sequential Renaming logic
├── ui/                 # Frontend Presentation Layer
│   ├── components/     # Specialized Layout Widgets & Panel Modules
│   │   ├── renaming_panel.py
│   │   └── sorting_panel.py
│   └── main_window.py  # Global Window Instantiation & Visual State Lifecycles
├── data/               # Local Storage Layer
│   └── history.json    # Rollback log arrays for historical tracking
├── app_icon.ico        # Native GUI Asset Icon
├── main.py             # Global Application Bootstrap Entrance
└── .gitignore          # Production untracking criteria

```

---

## 📦 How to Run Locally

To manually evaluate, configure, or launch this environment from the source code, run the following terminal script blocks:

1. **Clone the repository:**
```bash
git clone [https://github.com/RhainyAulia/Batch_Renamer.git](https://github.com/RhainyAulia/Batch_Renamer.git)
cd Batch_Renamer

```


2. **Establish and activate a Virtual Environment:**
```bash
python -m venv venv
# On Windows (CMD):
venv\Scripts\activate

```


3. **Install technical project prerequisites:**
```bash
pip install customtkinter pyinstaller

```


4. **Launch the core system application:**
```bash
python main.py

```



---

## 🚀 Compiling Standalone Production Executables

To bundle the entire architecture structure, embedded dynamic metadata assets, and native environment components into a single Windows portable binary execution file, run:

```bash
pyinstaller --onefile --noconsole --icon="app_icon.ico" --add-data "app_icon.ico;." --name="BatchRenamer" main.py

```

*The packaged asset will deploy inside the local `dist/` workspace directory.*

---

*Developed as an Advanced Web Programming (Pemenuhan Tugas Akhir Pemrograman Web Lanjut) Core Examination Project.*

