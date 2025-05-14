# Agent Specifications

Each agent below is defined by its responsibilities, I/O schema, and dependencies.

___
### **1. Company Research Agent**

- **Purpose**: Collect foundational data on the target company.
- **Responsibilities**:
    - Query web and API sources (Crunchbase [Pricey, Find Loophole] , Wikipedia)
    - Scrape/ingest documents and preprocess text [Not in Primary Stages, for later iterations]
    - Summarize into a structured **company profile** JSON
- **Key Inputs**: `company_name` (string)
- **Key Outputs**:
    
    ```json
    
    {
      "name": "...",
      "industry": "...",
      "description": "...",
      "products": [...],
      "headquarters": "...",
      "sources": [...]
    } 
    ```
___    

### **2. Industry/Domain Analysis Agent**

- **Purpose**: Identify and rank relevant domains where the company can expand.
- **Responsibilities**:
    - Analyze company profile with an LLM prompt chain
    - Generate a ranked list of candidate domains with rationales
- **Key Inputs**: Company profile JSON
- **Key Outputs**:
    
    ```json
    
    [
      { "domain": "Retail Tech", "score": 0.92, "rationale": "...", "sources": [...] },
      …
    ]
    
    ```
___    

### **3. Market Data Agent**

- **Purpose**: Fetch quantitative market metrics for the chosen domain.
- **Responsibilities**:
    - Pause for optional **domain selection** by the user (default: top-most score)
    - Call trend and financial APIs
        - Google Trends [must be possible]
        - Statistica [see how much free tier offers]
        - Web Search
        - Pirated Knowledge Bases
    - Summarize into **market statistics** and narrative
- **Key Inputs**: `chosen_domain` (string)
- **Key Outputs**:
    
    ```json
    
    {
      "market_size_usd": 5e9,
      "CAGR": 0.07,
      "key_drivers": [...],
      "sources": [...]
    }
    
    ```
___    

### **4. Competitive Landscape Agent**

- **Purpose**: Map out key competitors and their offerings.
- **Responsibilities**:
    - Query APIs (Crunchbase, CB Insights) if possible else web search
    - Compile a table of competitors, features, and market positions
    - Provide summary of competitor strengths/weaknesses
- **Key Inputs**: Company profile + chosen domain
- **Key Outputs**:
    
    ```json
    [
      { "competitor": "A Corp", "product": "X", "market_share": 0.15, "note": "...", "source": "..." },
      …
    ]
    
    ```
___   

### **5. Gap Analysis Agent**

- **Purpose**: Detect unmet needs and strategic gaps in the market.
- **Responsibilities**:
    - Compare company capabilities vs. competitor features
    - Use an LLM to reason over data tables and narratives
    - Output a list of **market gaps** with evidence
- **Key Inputs**: Company profile, competitor list, and market stats
- **Key Outputs**:
    
    ```json
    [
      { "gap": "Missing AI-driven personalization", "impact": "High", "evidence": "...", "source": "..." },
      …
    ]
    
    ```
___

### **6. Opportunity Agent**

- **Purpose**: Generate prioritized growth opportunities and use-cases.
- **Responsibilities**:
    - Brainstorm and validate ideas via LLM prompts
    - Ground each opportunity in data from previous agents
    - Rank by feasibility and strategic impact
- **Key Inputs**: List of gaps + any additional context
- **Key Outputs**:
    
    ```json
    [
      { "title": "Launch AI Chatbot", "priority": "High", "description": "...", "sources": [...] },
      …
    ]
    
    ```
___   

### **7. Report Synthesis Agent**

- **Purpose**: Compile a polished, citation-rich final report.
- **Responsibilities**:
    - Combine structured outputs from all agents
    - Use an LLM template to generate Markdown or PDF
    - Embed citations as footnotes or bracketed references
- **Key Inputs**: Outputs from Agents 1–6
- **Key Outputs**: Full **Market Research Report** text, exportable as Markdown/HTML/PDF

___

### **8. Citation/Data Collector Agent [Served as a Tool]**

- **Purpose**: Support all agents by retrieving and formatting citations.
- **Responsibilities**:
    - Execute on-demand queries (keywords, URLs)
    - Extract snippets or dataset records with metadata
    - Attach citation info to agent outputs
- **Key Inputs**: Citation requests from any agent
- **Key Outputs**: Snippet/text with `{ "url": "...", "excerpt": "...", "title": "..." }`

---