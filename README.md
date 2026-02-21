# 🔍 NitiLens
### AI-Powered Policy Intelligence & Continuous Compliance Platform

## 🧠 Problem Statement
Compliance requirements and business policies are often stored as unstructured PDF documents, while company data is stored in constantly changing databases. This disconnect makes compliance enforcement manual, slow, and error-prone.

## 💡 Solution
NitiLens bridges the gap between static policy documents and dynamic business data by automatically:
- Ingesting free-text policy PDFs
- Extracting structured compliance rules
- Scanning company databases for violations
- Explaining why violations occurred
- Enabling human review and intervention
- Continuously monitoring data for new risks
- 
## 🏗️ High-Level Architecture
Policy PDFs
↓
AI Rule Extraction Engine
↓
Structured Compliance Rules
↓
Compliance Scanning Engine
↓
Explainable Violation Detection
↓
Human Review & Governance
↓
Dashboards & Audit-Ready Reports

## ✨ Key Features
- 📄 Policy PDF ingestion
- 🧠 AI-driven rule extraction
- 🔍 Automated compliance scanning
- 🧾 Explainable violations with evidence
- 👩‍⚖️ Human-in-the-loop review workflow
- 🔁 Continuous and periodic monitoring
- 📊 Compliance dashboards and trends
- 🧾 Audit-ready report generation

## 🧭 Demo Flow
1. Upload a policy PDF  
2. Review extracted compliance rules  
3. Connect to a sample company dataset  
4. Run a compliance scan  
5. Review detected violations  
6. Approve or dismiss findings  
7. Generate an audit-ready report  

## 🛠️ Tech Stack

**Frontend**
- Next.js
- Tailwind CSS

**Backend**
- Python FastAPI

**Data**
- SQLite / Mock JSON datasets

**AI / NLP**
- LLM-based policy rule extraction (simulated)

## 📁 Repository Structure
nitilens-ai-compliance-platform/
│
├── frontend/ # Next.js frontend
├── backend/ # FastAPI backend
├── data/ # Sample policies and mock datasets
├── docs/ # Architecture and API docs
├── reports/ # Sample compliance reports
├── .env.example
├── README.md
└── LICENSE

🔐 Authentication
Mock email/password login
Simulated SSO placeholders
Role-based access (demo only)

📊 Sample Data
Policy PDFs (IT Security, Data Privacy)
Employee records
Access logs
Transaction datasets

🔁 Continuous Monitoring
NitiLens supports manual and scheduled scans with historical tracking to detect new and recurring compliance violations.

⚠️ Disclaimer
This project is a hackathon prototype created for demonstration purposes only. All data and policies are mock examples.

📜 License
MIT License



