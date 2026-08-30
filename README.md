# Skylark BI Copilot

## Monday.com Business Intelligence Agent

Skylark BI Copilot is a conversational Business Intelligence agent designed to help founders and executives get fast, reliable answers from sales and operations data stored in Monday.com.

The system connects to two live Monday.com boards:

- **Deals** — sales pipeline and opportunity data
- **Work Orders** — project execution, billing, collections and receivables

Instead of manually extracting data, cleaning spreadsheets, calculating metrics and interpreting results for every question, the agent provides a single conversational interface for business analysis.

---

## Hosted Prototype

**Live application:**  
https://skylark-bi-copilot.streamlit.app

The prototype can be tested directly through the browser without requiring local setup.

---

# 1. Problem Being Solved

Founders and executives often need answers such as:

- How is our pipeline looking?
- Which sectors have the strongest pipeline?
- How is the Mining pipeline performing?
- How much is currently receivable?
- How much is still to be billed?
- Which sectors have operational pressure?
- How does sales pipeline compare with execution?
- Which areas require leadership attention?
- What data-quality issues could affect our decisions?

Answering these questions manually requires:

1. Pulling data from Monday.com.
2. Cleaning inconsistent records.
3. Identifying the relevant business dimensions.
4. Performing calculations.
5. Combining information across boards.
6. Interpreting the results.
7. Communicating the result to leadership.

Skylark BI Copilot automates this workflow.

---

# 2. Solution Overview

The system follows a layered architecture:

```text
                    USER
                      │
                      ▼
            Conversational Question
                      │
                      ▼
              Query Understanding
                      │
                      ▼
             Structured Query Plan
                      │
                      ▼
              Analytics Layer
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       Deals                 Work Orders
          │                       │
          └───────────┬───────────┘
                      ▼
             Deterministic Results
                      │
                      ▼
               Gemini AI Layer
                      │
                      ▼
          Executive-Level Response
                      │
                      ▼
                Streamlit UI
```

The key architectural principle is:

> **The AI interprets and communicates business information, while Python performs the numerical calculations.**

This prevents the language model from becoming the source of truth for financial and operational numbers.

---

# 3. Core Features

## 3.1 Monday.com Integration

The application connects directly to Monday.com using its GraphQL API.

It dynamically reads the configured boards rather than using hardcoded CSV data.

The integration supports:

* Monday.com authentication
* Board discovery
* Board metadata retrieval
* Column discovery
* Item retrieval
* Pagination
* API error handling
* Read-only access
* Data refresh

The application does not create, update or delete Monday.com records.

Monday.com remains the source of truth.

---

# 4. Data Resilience

The assignment data contains real-world inconsistencies and incomplete records.

The application therefore includes a dedicated data cleaning and quality layer.

It handles:

* Missing/null values
* Missing deal values
* Missing closure probabilities
* Missing dates
* Unknown sectors
* Inconsistent text values
* Date normalization
* Incomplete work-order records
* Missing billing and collection information

The system does not blindly interpret missing information as zero.

For example:

```text
₹0
```

and:

```text
Value not recorded
```

have different business meanings.

Where appropriate, the application exposes data-quality information alongside analytical results.

Examples include:

* Missing record counts
* Value coverage
* Probability coverage
* Unknown/unclassified records
* Financial data gaps

This gives users visibility into the reliability of the underlying analysis.

---

# 5. Query Understanding

The agent converts natural-language founder questions into structured analytical plans.

For example:

```text
How is our pipeline looking for Mining this quarter?
```

is interpreted as:

```json
{
  "tool": "pipeline_summary",
  "sector": "Mining",
  "period": "this quarter"
}
```

This structured plan is then passed to the appropriate deterministic analytics function.

The agent can distinguish between questions involving:

* Pipeline
* Pipeline by sector
* Pipeline by stage
* Work-order execution
* Financials
* Cross-board analysis
* Leadership updates
* Data quality

---

# 6. Business Intelligence Capabilities

## Pipeline Analysis

The system provides:

* Open deal count
* Gross pipeline
* Weighted pipeline
* Pipeline by sector
* Pipeline by stage
* Sector concentration
* Deals without probability
* Deals without value
* Unknown/unclassified sectors
* Data coverage

### Weighted Pipeline

The prototype uses the following analytical weights:

| Probability Category | Weight |
| --------------------- | -----: |
| High                  |    80% |
| Medium                |    50% |
| Low                   |    20% |

These are explicitly treated as analytical assumptions and not as statistically validated company conversion rates.

---

# 7. Operational Analysis

The Work Orders board is used to calculate:

* Total work orders
* Active work orders
* Completed work orders
* Active share
* Completion share
* Execution status distribution
* Sector-level operational activity

This allows leadership to understand current execution workload in addition to future sales opportunities.

---

# 8. Financial Analysis

The application analyzes:

* Billed value
* Collected amount
* Amount to be billed
* Amount receivable
* Collection rate
* Receivable percentage
* Billing backlog ratio

This helps distinguish between sales performance and actual cash/operational realization.

---

# 9. Cross-Board Analysis

A key feature is the ability to combine information from both Monday.com boards.

For example:

```text
Sales Pipeline
      +
Work Order Execution
      +
Billing / Collections
      ↓
Sector-Level Business View
```

This allows questions such as:

* Which sectors have significant pipeline?
* Which sectors have active execution?
* Where is billing backlog concentrated?
* Which sectors have both opportunity and operational pressure?
* Where should leadership focus attention?

The goal is to move from isolated reporting to business-level context.

---

# 10. Leadership Updates

The optional leadership-update requirement is implemented as an executive decision brief.

A leadership update is designed to communicate:

### What happened?

Key sales, operations and financial metrics.

### Why does it matter?

Important concentration, execution, cash or data-quality signals.

### What should leadership watch?

Areas that may require review or action.

The objective is not to produce another raw dashboard export.

It is to turn the available data into a concise management-oriented summary.

---

# 11. Analytics Tools

The agent currently supports the following analytical capabilities:

### `pipeline_summary`

Overall open sales pipeline.

### `pipeline_by_sector`

Comparison of pipeline across sectors.

### `pipeline_by_stage`

Pipeline distribution across sales stages.

### `work_order_summary`

Operational work-order and execution analysis.

### `financial_summary`

Billing, collection and receivable analysis.

### `cross_board`

Sales pipeline and operational analysis by sector.

### `leadership_update`

Executive-level business summary.

### `data_quality`

Data completeness and quality analysis.

---

# 12. AI Layer

Gemini is used for:

* Natural-language query understanding
* Analytical intent selection
* Executive response generation
* Contextual interpretation
* Business insight communication
* Leadership summaries

The model is instructed not to invent business numbers.

The analytical flow is:

```text
User Question
      ↓
AI Query Understanding
      ↓
Structured Intent
      ↓
Python Analytics
      ↓
Calculated Result
      ↓
AI Executive Explanation
```

This separation improves reliability and makes the numerical layer reproducible.

---

# 13. Executive Interface

The Streamlit application is designed as an executive-facing interface rather than a developer-oriented data tool.

The dashboard surfaces key business signals such as:

* Open pipeline
* Weighted pipeline
* Active work orders
* Receivables
* Pipeline concentration
* Collection performance
* Billing backlog
* Data quality
* Leadership signals

Users can then ask follow-up questions conversationally.

An analysis trace is also available so the user can understand which analytical capability was selected.

---

# 14. Error Handling

The application includes error handling across multiple layers.

## Monday.com

Handles:

* Authentication failures
* Connection failures
* HTTP errors
* GraphQL errors
* Missing/inaccessible boards
* Invalid API responses

## Data

Handles:

* Missing values
* Unknown classifications
* Incomplete records
* Missing financial fields
* Missing probabilities

## Application

The UI displays readable error messages rather than silently failing.

---

# 15. Project Structure

```text
skylark-bi-agent/
│
├── app.py
├── agent.py
├── analytics.py
├── config.py
├── data_quality.py
├── monday_client.py
├── prompts.py
├── requirements.txt
│
├── assets/
│   └── skylark_logo.jpeg
│
├── DECISION_LOG.md
├── README.md
│
├── test_analytics.py
├── test_data.py
└── test_monday.py
```

### File Responsibilities

| File                 | Responsibility                               |
| -------------------- | --------------------------------------------- |
| `app.py`             | Streamlit application and user interface     |
| `agent.py`           | Query understanding and AI orchestration      |
| `analytics.py`       | Deterministic business calculations           |
| `data_quality.py`    | Cleaning, normalization and quality analysis  |
| `monday_client.py`   | Monday.com GraphQL API integration            |
| `prompts.py`         | AI system, planner and answer prompts         |
| `config.py`          | Environment and application configuration     |
| `test_monday.py`     | Monday.com integration testing                |
| `test_data.py`       | Data quality testing                          |
| `test_analytics.py`  | Business intelligence validation              |
| `DECISION_LOG.md`    | Engineering assumptions and trade-offs        |

---

# 16. Local Setup

## Requirements

* Python 3.12+
* Monday.com API token
* Access to the Deals board
* Access to the Work Orders board
* Gemini API key

---

## Clone Repository

```bash
git clone https://github.com/sandhiya-gh/skylark-bi-agent.git
cd skylark-bi-agent
```

---

## Create Virtual Environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a local `.env` file:

```env
MONDAY_API_URL=https://api.monday.com/v2

MONDAY_API_TOKEN=YOUR_MONDAY_API_TOKEN

DEALS_BOARD_ID=YOUR_DEALS_BOARD_ID

WORK_ORDERS_BOARD_ID=YOUR_WORK_ORDERS_BOARD_ID

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

GEMINI_MODEL=gemini-3.6-flash
```

Never commit `.env` or API credentials to GitHub.

---

# 17. Validation

Run the Monday.com integration test:

```bash
python test_monday.py
```

Run the data-quality test:

```bash
python test_data.py
```

Run the analytics test:

```bash
python test_analytics.py
```

Run the application:

```bash
streamlit run app.py
```

---

# 18. Deployment

The hosted prototype is deployed using Streamlit Community Cloud.

Deployment configuration:

```text
Repository: sandhiya-gh/skylark-bi-agent
Branch: main
Entrypoint: app.py
Python: 3.12
```

Production credentials are supplied through deployment secrets.

They are not stored in the GitHub repository.

---

# 19. Security

The application is read-only with respect to Monday.com.

It does not:

* Create records
* Modify records
* Delete records
* Change board configuration

Credentials are supplied through environment variables locally and deployment secrets in production.

The `.env` file is excluded through `.gitignore`.

---

# 20. Current Validation Snapshot

During development, the live Monday.com boards returned:

* 346 Deals
* 176 Work Orders

The analytics layer successfully produced results including:

* 51 open deals
* ₹68.82 Cr gross pipeline
* ₹25.90 Cr weighted pipeline
* 55 active work orders
* ₹3.63 Cr receivables

These values are validation results from the connected assignment dataset.

They are **not hardcoded into the application**.

The application retrieves data dynamically from Monday.com.

---

# 21. Example Questions

### Sales

```text
How is our pipeline looking?
```

```text
How is the Mining pipeline this quarter?
```

```text
Which sectors have the strongest pipeline?
```

```text
What stages contain the most pipeline value?
```

### Operations

```text
How many active work orders do we have?
```

```text
Which sectors have the largest execution workload?
```

### Finance

```text
How much money is currently receivable?
```

```text
How much is still to be billed?
```

```text
How efficient are our collections?
```

### Cross-Board

```text
Compare sales pipeline with execution.
```

```text
Which sectors have both pipeline and operational pressure?
```

### Leadership

```text
Which sectors need leadership attention?
```

```text
Prepare a leadership update.
```

### Data Quality

```text
What data quality issues should I know about?
```

---

# 22. Limitations

This is a six-hour assignment prototype and intentionally focuses on the
required capabilities.

Current limitations include:

1. Monday.com remains the source of truth.
2. Pipeline probability weights are analytical assumptions.
3. Historical trend analysis requires historical snapshots that are not
   currently maintained.
4. Insight quality depends on the completeness of Monday.com data.
5. The application is currently read-only.
6. Production deployment would benefit from additional authentication,
   monitoring and audit infrastructure.

---

# 23. Future Improvements

With additional development time, the next version could include:

* Historical pipeline trends
* Deal aging analysis
* Sales-cycle analysis
* Statistically calibrated win probabilities
* Forecast versus actual analysis
* Sector risk scoring
* Automated anomaly detection
* Capacity forecasting
* Cash-flow forecasting
* Automated executive briefing generation
* Alerts for material business changes
* Role-based access control
* Audit logging
* Agent evaluation and regression testing

---

# 24. Design Philosophy

Skylark BI Copilot is built around a simple principle:

> **The goal of AI in business intelligence is not merely to answer a question, but to reduce the time between a business question and a defensible business decision.**

The system combines:

```text
Live Business Data
        +
Data Resilience
        +
Deterministic Analytics
        +
Natural-Language Intelligence
        +
Executive Context
        +
Data-Quality Transparency
        =
Decision Intelligence
```

---

## Author

**Sandhiya Kennedy**

Built for the Skylark Drones
Monday.com Business Intelligence Agent Technical Assignment.
