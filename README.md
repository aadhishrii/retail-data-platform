# Retail Intelligence Platform

A modern retail analytics platform that transforms operational data into trusted business insights using Apache Airflow, Databricks, dbt, Python, SQL, and Streamlit.

## Overview

Retail data becomes useful only when it is reliable, well modeled, and easy to consume.

This project was built as an end to end retail data platform that takes operational data through ingestion, orchestration, transformation, quality validation, analytical modeling, and business facing reporting.

The goal is not simply to move data from one system to another.

The goal is to create a trusted analytical product that can support questions around revenue, orders, stores, products, customers, and operational performance.

## What this project solves

Retail teams often work with fragmented operational data spread across transactional systems and files.

That creates several challenges.

1. Source data changes continuously

2. Business logic gets repeated across reports

3. Analysts need stable fact and dimension models

4. Data quality issues can silently reach dashboards

5. Historical dimension changes need to be preserved

6. Pipeline failures need visible orchestration and dependency control

7. Analytics should remain usable even when cloud connectivity is unavailable

This project addresses those problems through a layered ELT architecture with clear responsibilities at each stage.

## Architecture

The platform combines database style ingestion, file ingestion, incremental transformation, quality validation, dimensional modeling, and analytics delivery.

Apache Airflow acts as the orchestration layer.

Databricks provides the execution environment.

dbt manages transformation logic, testing, incremental processing, and snapshots.

Streamlit presents the final analytical outputs to the user.

## Architecture Diagram
<p align="center">
<img width="2073" height="2319" alt="image" src="https://github.com/user-attachments/assets/065a722e-a30f-468e-83c8-8a21317a0d59" />
</p>

<p align="center">
  <em>End to end architecture of the Retail Intelligence Platform</em>
</p>

## Platform Flow

```text
Agentic Database
        ↓
CDC ingestion
        ↓

AWS S3
        ↓
File ingestion
        ↓

Incremental staging
        ↓

Silver technical models
        ↓

Data quality checks
        ↓

Silver business model
        ↓

Gold dimensions and fact models
        ↓

Streamlit dashboard
        ↓

Revenue
Order trends
Category performance
Store analysis
Product performance
```

## Core Capabilities

### CDC Style Ingestion

The Airflow DAG triggers a Databricks job through the Databricks SDK and waits for the job to complete before allowing downstream processing to continue.

This creates a controlled dependency between ingestion and transformation.

### File Ingestion

The architecture also supports file based ingestion through AWS S3.

This gives the project a more realistic ingestion pattern because production data platforms often need to support both operational database changes and batch file delivery.

### Incremental Transformation

Technical silver models are configured with incremental dbt logic.

Records are processed using business keys and updated timestamps so that the platform can focus on changed data rather than rebuilding every dataset during every run.

### Technical Silver Layer

The technical silver layer standardizes raw source data and adds processing metadata.

Its responsibility is to create clean and dependable source aligned models before business logic is introduced.

### Data Quality Validation

dbt tests are integrated directly into the orchestration sequence.

The pipeline validates important assumptions before downstream models are promoted.

This turns quality from a manual check into part of the data delivery process.

### Business Silver Layer

The business layer joins orders, order items, products, customers, stores, and employees into a reusable analytical structure.

This centralizes common business relationships and reduces repeated join logic for downstream consumers.

### Gold Layer

The gold layer provides analytics ready fact and dimension models.

The current implementation includes order focused fact modeling and historical dimension tracking through dbt snapshots.

### Analytics Application

The Streamlit dashboard provides business facing access to the final curated data.

When Databricks configuration is available, the application reads from the gold layer directly.

When Databricks is unavailable, the dashboard falls back to a local CSV export.

This makes the project both cloud connected and easy to demonstrate locally.

## Business Questions Supported

The analytical layer is designed to support practical retail questions.

1. How is revenue changing over time

2. Which stores are performing strongest

3. Which products contribute most to sales

4. Which categories are growing or declining

5. What patterns exist across order status and volume

6. How does performance vary across different parts of the retail operation

## Technology Stack

| Area                        | Technology     |
| --------------------------- | -------------- |
| Orchestration               | Apache Airflow |
| Data platform               | Databricks     |
| Transformation              | dbt            |
| Modeling                    | SQL            |
| Application                 | Streamlit      |
| Programming                 | Python         |
| File ingestion              | AWS S3         |
| Containerization            | Docker         |
| Local orchestration runtime | Docker Compose |

# Walmart Retail Data Engineering Project

A full-stack retail analytics project built around a Walmart-style sales dataset, using Python, Airflow, Databricks, and dbt to orchestrate and transform data into business-ready analytics tables.

## Overview

This project demonstrates an end-to-end data engineering workflow for retail operations and sales analytics. It starts with raw transaction and customer data, orchestrates ingestion through Airflow, and transforms the data in layered dbt models to create clean, analyst-friendly outputs.

The project is designed to show a realistic modern data stack that handles:

- data ingestion
- orchestration
- transformation and testing
- business-layer modeling
- analytics readiness
- operational automation

## Business Use Case

The project models a retail business scenario involving:

- customers
- stores
- products
- employees
- orders
- order items

The final output is a set of curated tables and metrics that can support dashboards, sales analysis, operational reporting, and future demand or revenue analysis.

## Tech Stack

- Python
- Apache Airflow
- Databricks
- dbt
- SQL
- Pandas
- Streamlit
- Plotly

## Architecture

The system follows a layered warehouse approach:

1. Raw source data is loaded into dataset files and schema definitions.
2. Airflow orchestrates the workflow.
3. Databricks job ingestion is triggered through the Databricks SDK.
4. dbt runs source freshness, silver transformations, tests, and gold models.
5. Analytics-ready tables are produced for downstream reporting and dashboarding.

## Repository Structure

```text
<<<<<<< HEAD
airflow/
    dags/
        orchestrate.py
    Dockerfile
    docker compose.yaml
    requirements.txt

dashboard/
    app.py
    gold_layer.csv
    requirements.txt

walmart_dataset/
    data/
    ddl/
        walmart_schema.sql
    load_data.py

walmart_project/
    models/
        source/
        silver_t/
        silver_b/
        gold/
    snapshots/
    tests/
    dbt_project.yml
    profiles.yml

main.py
pyproject.toml
README.md
```

## Orchestration Sequence

The Airflow DAG coordinates the pipeline in a deliberate order.

```text
CDC ingestion
        ↓
Target cleanup
        ↓
Source freshness
        ↓
Silver technical models
        ↓
Silver technical tests
        ↓
Silver business model
        ↓
Silver business tests
        ↓
Gold ephemeral models
        ↓
Dimension snapshots
        ↓
Gold fact models
```

The important idea is that downstream data is created only after upstream stages complete successfully.

## Data Model

The project works with six core retail entities.

```text
customers
products
orders
order_items
stores
employees
```

These entities are transformed through multiple layers.

### Bronze

The bronze layer represents raw source data made available for transformation.

### Silver Technical

The technical silver layer keeps models close to source structure while adding incremental behavior and processing metadata.

### Silver Business

The business silver layer combines the cleaned entities into a reusable analytical model.

### Gold

The gold layer contains curated facts and dimensions designed for reporting and analytical consumption.

## Incremental Processing

Several silver models use dbt incremental materialization.

Each model uses a unique business key and checks updated timestamps to determine which records need to be processed.

This improves efficiency and demonstrates an important production pattern.

The pipeline does not need to rebuild every model from scratch when only a small portion of the source has changed.

## Data Quality Strategy

The project currently includes multiple forms of quality validation.

1. Source freshness checks

2. Silver model testing

3. Business layer testing

4. Custom validation for missing critical identifiers

The current strategy focuses on structural trust.

A future production version could extend this with volume anomaly checks, accepted value rules, relationship validation, SLA monitoring, and automated alerts.

## Slowly Changing Dimensions

dbt snapshots are used to preserve historical dimension changes.

This matters because business entities change over time.

Customers update information.

Products change attributes.

Stores evolve.

Employees move roles.

A historical analytical system needs to preserve what was true at the time of an event rather than only what is true today.

## Dashboard

The dashboard is the consumption layer of the platform.

It turns curated gold data into an experience that can be used by a business stakeholder rather than only by an engineer.

### Connected Mode

When Databricks credentials and connection settings are available, the dashboard reads directly from the gold layer.

### Demo Mode

When Databricks is unavailable, the application reads from `dashboard/gold_layer.csv`.

This keeps the project easy to review and portfolio friendly without changing the overall architecture.

## Local Setup

### Prerequisites

Python 3.12 or later

Docker

Docker Compose

A Databricks workspace

dbt with the Databricks adapter

### Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd retail_intelligence_platform
```

### Install Project Dependencies

Use your preferred Python environment manager.

The repository includes `pyproject.toml` and `uv.lock`.

### Configure Databricks

Provide Databricks connection values through environment variables or a secure local configuration.

```text
DATABRICKS_HOST
DATABRICKS_HTTP_PATH
DATABRICKS_TOKEN
DATABRICKS_CATALOG
DATABRICKS_SCHEMA
```

Credentials should never be committed to source control.

### Start Airflow

From the Airflow directory:

```bash
docker compose up
```

Open the Airflow interface and enable the orchestration DAG.

### Run dbt Directly

```bash
cd walmart_project
dbt debug
dbt source freshness
dbt run
dbt test
dbt snapshot
```

### Start the Dashboard

```bash
cd dashboard
pip install requirements.txt
streamlit run app.py
```

When Databricks configuration is present, the dashboard uses the connected gold layer.

Otherwise it uses the local fallback dataset.

## Engineering Decisions

### Clear Layer Ownership

Each layer has one responsibility.

Source handling stays separate from technical cleaning.

Technical cleaning stays separate from business logic.

Business logic stays separate from analytical serving.

This keeps the system easier to reason about and easier to extend.

### Quality Before Promotion

Tests are part of the workflow rather than optional checks.

This makes trust a requirement for downstream delivery.

### Incremental Processing

Incremental transformations reduce unnecessary work and make the project closer to how production pipelines operate.

### Historical Modeling

Snapshots preserve dimension history so that analytical results remain meaningful over time.

### A Visible Consumer

The Streamlit dashboard gives the platform an actual user.

That changes the project from a collection of data engineering tools into a data product.

## Product Perspective

This platform is designed around three responsibilities.

### Reliability

Data should move predictably through controlled stages.

### Meaning

Transformations should create stable business concepts rather than simply cleaner tables.

### Usability

The final models should be easy to consume without requiring users to understand the full pipeline.

The strongest data platforms combine all three.

## Current Limitations

This is a portfolio focused implementation rather than a finished enterprise platform.

The architecture is intentionally designed so that production features can be added without rebuilding the project from the beginning.

The main gaps today are security hardening, automated deployment, deeper observability, broader testing, formal data contracts, and cloud infrastructure automation.

## What This Project Demonstrates

This repository demonstrates more than familiarity with individual tools.

It shows how orchestration, ingestion, incremental transformation, data quality, dimensional modeling, historical tracking, analytical serving, and user facing reporting can work together as one platform.

From a data engineering perspective, the focus is reliability and structure.

From a product perspective, the focus is usefulness and trust.

The project becomes interesting where those two perspectives meet.

## Key Takeaways

1. Orchestration is not only scheduling. It defines the trust sequence of the platform.

2. Incremental models are an important step toward scalable data processing.

3. Data quality belongs inside the pipeline.

4. Business models should reduce repeated analytical complexity.

5. Gold models should represent stable business meaning.

6. Historical dimensions matter when business entities change over time.

7. A dashboard gives the platform a real consumer and a visible purpose.

## Final Note

This project was built to explore the complete lifecycle of a modern data product.

It begins with ingestion.

It earns trust through transformation and validation.

It models business meaning.

It ends with an analytical experience that someone can actually use.

That is the goal of the platform.

Not just data that moves.

Data that becomes useful.

```
├── airflow/
│   ├── dags/
│   │   └── orchestrate.py
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── requirements.txt
│   └── walmart_project/
├── dashboard/
│   ├── app.py
│   └── requirements.txt
├── walmart_dataset/
│   ├── data/
│   ├── ddl/
│   └── load_data.py
├── walmart_project/
│   ├── dbt_project.yml
│   ├── macros/
│   ├── models/
│   ├── snapshots/
│   ├── tests/
│   └── target/
├── main.py
├── pyproject.toml
└── README.md
```

## Pipeline Flow

The orchestration sequence in Airflow is:

- trigger CDC ingestion job
- clean target folder
- run source freshness checks
- run silver technical transformations
- run silver technical tests
- run silver business transformations
- run silver business tests
- run gold ephemeral models
- run snapshot models
- run gold fact models

This creates an organized ELT pipeline from raw source to curated business data.

## Data Model

Core entity tables include:

- customers
- employees
- stores
- products
- orders
- order_items

The dbt layer creates:

- source layer definitions
- silver technical staging models
- silver business layer joined data
- gold fact and ephemeral output models

## Dashboard Feature

A Streamlit dashboard has been added under the `dashboard/` folder to provide a simple analytics interface.

It includes:

- revenue overview
- orders by status
- sales by store
- sales by category
- monthly revenue trend
- top-performing products
- basic data quality snapshot

## How to Run

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r dashboard/requirements.txt
```

### 2. Run the dashboard

```bash
streamlit run dashboard/app.py
```

### 3. Airflow project

From the `airflow/` directory:

```bash
docker compose up --build
```

### 4. dbt project

From the `walmart_project/` directory:

```bash
dbt debug
dbt run
dbt test
```

## Key Files

- `airflow/dags/orchestrate.py` — orchestrates the full pipeline
- `walmart_project/models/silver_b/obt_b.sql` — joined business-layer model
- `walmart_project/models/gold/fact/fact_orders.sql` — fact table output
- `walmart_dataset/ddl/walmart_schema.sql` — schema definition for the raw retail entities
- `dashboard/app.py` — analytics dashboard app

## What I Learned

This project demonstrates:

- warehouse-style ELT architecture
- orchestrated transformation workflows
- layered business modeling with dbt
- operational automation patterns
- how to package a data engineering project for a portfolio

## Future Enhancements

Potential improvements for the next iteration include:

- customer segmentation analysis
- demand forecasting
- inventory risk monitoring
- store performance scorecards
- alerts and SLA monitoring in Airflow
- CI/CD for dbt and deployment checks
- cloud deployment and secrets management

## Portfolio Value

This project is strong because it combines a real retailer domain, pipeline orchestration, transformation logic, and a simple business-facing analytics experience. It shows an understanding of both engineering and data product thinking.
