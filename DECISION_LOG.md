# Skylark BI Copilot — Decision Log

## 1. Objective

The objective was to build a conversational Business Intelligence agent that allows founders and executives to ask natural-language questions over live Monday.com Deals and Work Orders data.

The primary design goal was not simply to build a chatbot, but to create a reliable decision-support layer over messy operational data.

The architecture was therefore designed around:

> **Live source data → deterministic analytics → executive interpretation**

---

# 2. Key Assumptions

## 2.1 Monday.com is the source of truth

The supplied spreadsheets were treated as initial source data for populating the Monday.com boards.

The application itself does not embed or hardcode the supplied records.

At runtime, Skylark reads the Deals and Work Orders boards dynamically through the Monday.com GraphQL API.

This satisfies the requirement that the agent operate on the live boards rather than on static CSV/XLSX data.

---

## 2.2 Gross pipeline and weighted pipeline are different concepts

I treated gross pipeline as the total value of open deals.

Weighted pipeline is calculated using analytical assumptions:

- High = 80%
- Medium = 50%
- Low = 20%

These percentages are not assumed to be probabilities supplied by Monday.com.

They are explicitly presented as analytical assumptions.

This distinction is important because otherwise a user could interpret a calculated weighted pipeline as an official company forecast.

---

## 2.3 Missing data is not automatically zero

A missing deal value is different from a deal whose value is genuinely zero.

Similarly, a missing closure probability should not silently be treated as zero probability.

Therefore, missing fields are tracked separately and surfaced through data-quality indicators.

This allows the user to understand both:

1. the calculated result, and
2. how complete the underlying data was.

---

## 2.4 Sector names are normalized conservatively

The source data contains inconsistent text conventions.

I normalize text for matching, but avoid aggressively merging business categories unless there is sufficient evidence.

For example, similar-looking sectors are not automatically assumed to represent the same commercial category.

This reduces the risk of silently changing the meaning of the source data.

---

## 2.5 "This quarter", "this month" and "this year"

When a user asks for a relative period, the application interprets:

- "this quarter" → current quarter
- "this month" → current month
- "this year" → current year

Period filtering is performed by the analytics layer rather than by the LLM.

---

# 3. Architectural Decisions

## 3.1 Why Monday.com API instead of MCP?

The assignment allowed either MCP or API.

I chose the Monday.com GraphQL API because:

- it provided direct access to the required boards;
- the application needed only read access;
- the data retrieval layer could be explicitly controlled;
- pagination, errors and DataFrame conversion could be handled deterministically;
- it kept the prototype lightweight within the six-hour constraint.

MCP would be a valid future option if the system needed a broader tool ecosystem.

---

## 3.2 Why Streamlit?

Streamlit was chosen because the assignment required a hosted, testable prototype within a six-hour development window.

It allowed rapid development of:

- conversational interaction;
- dashboards;
- KPI cards;
- scenario analysis;
- data-health views;
- evidence traces.

This enabled more time to be spent on the actual BI logic rather than frontend infrastructure.

---

## 3.3 Why separate Python analytics from the LLM?

This was the most important architectural decision.

I deliberately did not allow the LLM to calculate financial metrics.

Instead:

```text
LLM
↓
understands the question

Python
↓
performs calculations

LLM
↓
explains the verified result
