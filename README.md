# 🚁 Skylark BI Copilot

### AI-Powered Business Intelligence Agent for Monday.com

Skylark BI Copilot is a conversational decision-intelligence application built for founders and business leaders who need fast, reliable answers from operational business data.

It connects directly to Monday.com and analyzes two live business boards:

- **Deals** — sales pipeline and commercial information
- **Work Orders** — project execution, billing, collections and operational information

Instead of requiring a user to manually extract, clean and analyze data, Skylark converts natural-language business questions into deterministic analytics and executive-level insights.

---

## 🎯 Problem

Business leaders often need answers that span multiple operational systems.

A question such as:

> "How is our Energy pipeline looking this quarter?"

may require someone to:

1. Retrieve the latest data from Monday.com
2. Identify the relevant sector
3. Filter the appropriate records
4. Handle missing values and inconsistent formats
5. Calculate pipeline metrics
6. Interpret the result
7. Communicate the business implication

This becomes increasingly difficult when operational data is incomplete or inconsistent.

Skylark automates this workflow.

---

# 💡 Solution

Skylark acts as a conversational BI layer over Monday.com.

A founder can ask questions such as:

- "How is our pipeline looking overall?"
- "How is the Energy pipeline?"
- "Which sectors have the strongest pipeline?"
- "Which stages contain the most pipeline?"
- "How much is currently receivable?"
- "How much is still to be billed?"
- "Compare sales pipeline with execution."
- "Where is our biggest business risk?"
- "Which sectors need leadership attention?"
- "Prepare a leadership update."
- "What data quality issues should I know about?"

The system retrieves the current Monday.com data, applies deterministic analytics, and converts the results into concise executive insights.

---

# 🏗️ Architecture

```text
                         ┌───────────────────────┐
                         │       Founder         │
                         │ Natural-language      │
                         │      question         │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    Streamlit UI       │
                         │  Conversational BI    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Query Understanding │
                         │ Intent / sector /     │
                         │ period identification │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Deterministic BI      │
                         │ Analytics Engine      │
                         │                       │
                         │ • Pipeline            │
                         │ • Sectors             │
                         │ • Stages              │
                         │ • Operations          │
                         │ • Finance             │
                         │ • Cross-board         │
                         │ • Data quality        │
                         └───────────┬───────────┘
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ Monday.com      │   │ Data Quality    │
                │ GraphQL API     │   │ / Normalization │
                └────────┬────────┘   └─────────────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
        ┌──────────────┐  ┌────────────────┐
        │ Deals Board  │  │ Work Orders    │
        │              │  │ Board          │
        └──────────────┘  └────────────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Gemini Explanation    │
                         │                       │
                         │ Executive context     │
                         │ + implications        │
                         │ + recommendations     │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Executive Answer      │
                         │ + evidence / caveats  │
                         └───────────────────────┘
