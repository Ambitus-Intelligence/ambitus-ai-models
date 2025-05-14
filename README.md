# ambitus-ai-models 🔍

**Part of the [ambitus Intelligence](https://github.com/ambitus-intelligence) Ecosystem**

This repository contains AI/ML models, experiments, and tools powering **ambitus Intelligence**'s market research automation platform.  
All exploratory work, prototypes, and notebooks are organized under `/notebooks`.

---

## 🚀 Overview

`ambitus-ai-models` is the core engine behind Ambitus Intelligence’s automated market research platform. It provides:

- **Orchestrated Multi‑Agent Workflows**  
  A centralized Orchestrator sequences specialized AI agents, handles error‑flows, and manages user hand‑offs.

- **FastMCP Tool Server**  
  `ambitus-tools-mcp`—a MCP server, backed by FastMCP—hosts all external utilities (scrapers, API clients, validators) and the CitationAgent, allowing agents to discover and invoke tools at runtime.

- **Structured Agent Outputs**  
  Each agent emits well‑defined JSON payloads, which are persisted to a database and exposed via REST for downstream consumption.

---

## 🔑 Key Agents

| Agent Name                     | Responsibility                                                                                           |
|--------------------------------|----------------------------------------------------------------------------------------------------------|
| **CompanyResearchAgent**       | Scrape and ingest public & proprietary sources (Crunchbase, Wikipedia, web) to produce a company profile. |
| **IndustryAnalysisAgent**      | Analyze the company profile via LLM prompts to rank and rationalize potential expansion domains.         |
| **MarketDataAgent**            | Retrieve quantitative metrics (market size, CAGR, trends) from external APIs (Google Trends, Statista). |
| **CompetitiveLandscapeAgent**  | Compile and summarize key competitors, their products, market share, and strategic positioning.          |
| **GapAnalysisAgent**           | Use LLM reasoning to detect unmet needs and strategic gaps by comparing capabilities vs. competitors.    |
| **OpportunityAgent**           | Brainstorm, validate, and rank growth opportunities grounded in data from upstream agents.               |
| **ReportSynthesisAgent**       | Aggregate all agent outputs into a citation‑rich final report (Markdown, HTML, PDF).                    |
| **CitationAgent** *(Tool)*     | On‑demand retrieval of citations or data snippets, serving all agents via the MCP tool server.          |
---

## 📖 Documentation

- **Docs Index**: [docs/README.md](docs/README.md)  
- **System Overview**: [docs/system_overview.md](docs/system_overview.md)  
- **Agent Specifications**: [docs/agent_specs.md](docs/agent_specs.md)

##### Legacy Notion (for archival reference only):  
- [General Overview][notion-general]
- [Agent Details][notion-agents]  

[notion-general]: https://vedantcantsleep.notion.site/ambitus
[notion-agents]: https://vedantcantsleep.notion.site/Architecture-1f11629c6c5081a5b6edfef830af579f  

---
## 📁 Repository Structure

```text
ambitus-ai-models/
├── docs/                                       # Architecture & agent specs (Markdown)
│   ├── README.md                               # Index of spec docs
│   ├── system_overview.md
│   ├── agent_specs.md
│   ├── workflow_examples.md                    # TODO
│   └── mcp_server.md                           # TODO
├── notebooks/                                  # Experimental Jupyter/Colab prototypes
│   ├── Experiment ##- <experiment_name>.ipynb   
│   └── ...                                     # Additional experiments in ##-*.ipynb format
├── src/                                        # Production code (rapidly changing)
│   ├── agents/                                 # Agent implementations (one class per agent)
│   ├── tools/                                  # FastMCP-registered utilities & CitationAgent
│   └── orchestrator.py                         # Master orchestration logic
├── requirements.txt                            # Python dependencies
└── README.md                                   # Project overview (this file)
```
---

## 📧 Contacts

For questions or collaborations, contact:

Lead Developers:

- [Vedant Yadav](https://github.com/TheMimikyu)

- [Nidhi Satyapriya](https://github.com/Nidhi-Satyapriya)

- [Priyanshu Paritosh](https://github.com/gamerguy27072)

---
Part of the Next-Gen Market Intelligence Suite

[ambitus Intelligence](https://github.com/ambitus-intelligence) | [Documentation](https://github.com/ambitus-intelligence) | [Main Repository](https://github.com/ambitus-intelligence)


