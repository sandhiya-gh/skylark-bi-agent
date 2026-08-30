# Skylark BI Copilot — Decision Log

## 1. Objective and Interpretation

The assignment asks for an AI agent that can answer founder-level business
questions using two messy Monday.com boards: Deals and Work Orders.

I interpreted the requirement as building a decision-intelligence layer rather
than simply a chatbot or dashboard.

The system therefore needs to:

1. Understand natural-language business questions.
2. Retrieve current data dynamically from Monday.com.
3. Clean and normalize messy records.
4. Perform reliable business calculations.
5. Combine information across boards where required.
6. Explain results in executive language.
7. Communicate data-quality limitations.
8. Help leadership identify areas requiring attention.

---

## 2. Architecture Decision

### Decision

Separate AI reasoning from numerical analytics.

The implemented flow is:

```text
User Question
      ↓
Query Understanding
      ↓
Structured Analytical Plan
      ↓
Deterministic Python Analytics
      ↓
Calculated Business Result
      ↓
Gemini Executive Interpretation
```

### Rationale

I deliberately did not allow the LLM to become the source of truth for
business calculations.

Financial, pipeline and operational numbers are calculated deterministically
in Python.

Gemini is used for language understanding, interpretation and communication.

This improves:

* Reproducibility
* Auditability
* Consistency
* Resistance to numerical hallucination

---

## 3. Monday.com Integration

### Decision

Use the Monday.com GraphQL API rather than MCP.

The assignment permits either approach.

### Why API?

The application primarily requires read-only retrieval from two boards.

The API provides direct control over:

* Authentication
* Board discovery
* Column metadata
* Item retrieval
* Pagination
* Error handling

Introducing an additional MCP layer would increase integration complexity
without providing a significant benefit for this scoped use case.

Monday.com remains the source of truth and the application does not write
back to the boards.

---

## 4. Data Resilience

The supplied dataset contains missing and inconsistent real-world business
data.

I therefore added a dedicated cleaning and data-quality layer rather than
assuming that all records are complete.

The system handles:

* Missing values
* Missing deal values
* Missing probabilities
* Missing dates
* Unknown sectors
* Inconsistent text
* Incomplete work-order records
* Missing billing and collection information

### Important assumption

Missing values are not automatically treated as zero.

For example:

```text
₹0
```

means something different from:

```text
Value not recorded
```

Where possible, the system reports the extent of missing data so that
leadership can judge the confidence of the analysis.

---

## 5. Pipeline Probability Assumption

The prototype uses the following analytical weights:

| Probability | Weight |
| ----------- | -----: |
| High        |    80% |
| Medium      |    50% |
| Low         |    20% |

### Rationale

The assignment requires pipeline-health analysis, but the available data does
not provide a statistically validated company-specific conversion model.

Therefore these values are explicitly treated as analytical assumptions.

They should not be interpreted as actual Skylark conversion probabilities.

With historical won/lost deal data, I would replace these assumptions with
empirically calibrated probabilities.

---

## 6. Query Understanding

Founder questions are often expressed conversationally rather than as
structured database queries.

I therefore implemented intent routing.

The agent identifies analytical categories such as:

* Pipeline summary
* Pipeline by sector
* Pipeline by stage
* Work-order execution
* Financial analysis
* Cross-board analysis
* Leadership updates
* Data quality

For example:

```text
How is our pipeline looking for Mining this quarter?
```

is converted into a structured analytical plan:

```text
Tool: pipeline_summary
Sector: Mining
Period: this quarter
```

This allows the analytical layer to remain deterministic and predictable.

---

## 7. Cross-Board Analysis

### Decision

Treat the Deals and Work Orders boards as complementary sources rather than
two isolated datasets.

The system can combine:

```text
Sales Pipeline
      +
Work Order Execution
      +
Billing / Collections
```

to produce a sector-level business view.

### Rationale

A founder may not care only about how much pipeline exists.

They may also want to know whether that opportunity is accompanied by:

* Execution pressure
* Active projects
* Billing backlog
* Collection pressure

This provides more useful business context than returning isolated board
metrics.

---

## 8. Leadership Update Interpretation

The assignment makes leadership updates optional and leaves the
interpretation open.

I interpreted "leadership update" as a concise executive decision brief.

The output should answer:

### What happened?

Important sales, operations and financial signals.

### Why does it matter?

Business implications such as concentration, cash pressure, execution load or
data-quality concerns.

### What should leadership watch?

Areas that may require review or action.

I intentionally avoided treating a leadership update as a simple export of
all KPIs because leadership generally needs prioritization and context, not
another raw data table.

---

## 9. Data Quality as a Business Signal

### Decision

Expose data quality alongside analytical results.

### Rationale

An apparently precise number can create false confidence if a large portion
of the underlying records is incomplete.

For example, if some open deals have no value or probability, the system
should communicate that limitation instead of presenting the result as
perfectly complete.

The analytics layer therefore tracks metrics such as:

* Missing values
* Missing probabilities
* Unknown sectors
* Value coverage
* Probability coverage

This makes uncertainty visible rather than hiding it.

---

## 10. Dashboard Design

### Decision

Use a lightweight Streamlit executive interface.

### Rationale

The assignment requires a hosted prototype that can be tested without local
setup.

Streamlit provides:

* Fast deployment
* Interactive dashboards
* Conversational input
* Easy integration with Python analytics
* Low infrastructure overhead

The interface was designed around key executive signals rather than exposing
raw implementation details.

The conversational interface provides deeper analysis when required.

---

## 11. Read-Only Architecture

The assignment explicitly specifies Monday.com as read-only.

The implementation therefore does not:

* Create records
* Update records
* Delete records
* Modify board configuration

This reduces operational risk and keeps the prototype aligned with the
assignment requirements.

---

## 12. Error Handling

The system handles failures at multiple levels.

### API level

* Authentication failures
* Connection failures
* HTTP errors
* GraphQL errors
* Missing/inaccessible boards
* Invalid responses

### Data level

* Missing fields
* Unknown classifications
* Incomplete records
* Missing financial values
* Missing probabilities

### Application level

The Streamlit interface displays understandable errors rather than failing
silently.

---

## 13. Validation

The implementation was tested against the live Monday.com boards.

The connected data contained:

* 346 Deals
* 176 Work Orders

The analytics validation produced results including:

* 51 open deals
* ₹68.82 Cr gross pipeline
* ₹25.90 Cr weighted pipeline
* 55 active work orders
* ₹3.63 Cr receivables

The important design point is that these figures are calculated from
retrieved Monday.com data and are not hardcoded into the application.

The agent's query-routing behavior was also validated for pipeline,
sector/time-period, leadership and financial questions.

---

## 14. Key Trade-offs

### API vs MCP

API was chosen because the prototype only needs controlled, read-only access
to two boards.

### LLM calculations vs deterministic calculations

Deterministic Python calculations were chosen because numerical correctness is
more important than allowing the LLM complete freedom.

### Flexible AI vs structured planning

Structured intent routing was chosen to make the agent predictable while
still supporting natural-language questions.

### Completeness vs transparency

Rather than hiding incomplete records, the system exposes data-quality
limitations.

### Prototype speed vs production infrastructure

The six-hour assignment constraint favored a focused Streamlit prototype
over a larger production architecture.

---

## 15. What I Would Do Differently With More Time

The next version would focus on improving analytical depth and production
readiness.

### Analytics

* Historical pipeline trends
* Deal aging
* Sales-cycle analysis
* Forecast versus actual performance
* Statistically calibrated win probabilities
* Sector risk scoring
* Anomaly detection
* Capacity forecasting
* Cash-flow forecasting

### Agent

* Stronger ambiguity handling
* Clarifying-question flows
* Formal agent evaluation datasets
* Regression testing for business questions
* Confidence-aware responses

### Production

* Authentication
* Role-based access
* Audit logging
* Observability
* Automated alerts
* Historical data snapshots

---

## 16. Final Design Principle

The core principle behind the implementation is:

> **AI should reduce the time between a business question and a defensible business decision.**

For that reason, Skylark BI Copilot combines:

```text
Live Monday.com Data
        +
Resilient Data Processing
        +
Deterministic Analytics
        +
AI Query Understanding
        +
Executive Interpretation
        +
Data-Quality Transparency
```

rather than treating a generative AI model as a replacement for the
underlying BI system.
