# 🚁 Skylark BI Copilot

An AI-powered Business Intelligence Agent that answers founder-level
questions using live data from monday.com Deals and Work Orders boards.

## Problem

Business leaders often need answers that require combining sales,
pipeline, project execution, billing and collection information.

The source data is operational and can contain missing values,
inconsistent naming and incomplete records.

## Solution

Skylark BI Copilot connects directly to monday.com using its GraphQL API.

The system:

1. Retrieves live Deals and Work Orders data.
2. Normalizes inconsistent fields.
3. Detects missing and incomplete data.
4. Performs deterministic BI calculations.
5. Uses an LLM to interpret questions and communicate insights.
6. Provides founder-level recommendations.
7. Supports cross-board analysis.
8. Generates leadership updates.

## Architecture

Founder
↓
Streamlit Conversational UI
↓
AI Query Planner
↓
BI Analytics Engine
↓
Monday.com GraphQL API
↓
Deals + Work Orders Boards

## Key Design Principle

The LLM does not perform financial calculations.

Python performs numerical operations such as:

- Pipeline aggregation
- Weighted pipeline
- Sector aggregation
- Billing backlog
- Receivables
- Operational metrics

The LLM is responsible for intent understanding and executive
communication.

## Data Resilience

The application:

- Handles missing values.
- Normalizes sectors.
- Normalizes dates.
- Normalizes financial values.
- Handles missing closure probabilities.
- Surfaces data-quality warnings.
- Handles Monday.com API failures gracefully.

## Supported Questions

Examples:

- What's our pipeline looking like this quarter?
- How is the Energy pipeline?
- Which sectors have the strongest pipeline?
- Which stages contain the most pipeline?
- How much is still to be billed?
- What are our receivables?
- Compare sales pipeline with execution.
- Prepare a leadership update.
- What data quality issues should I know about?

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt