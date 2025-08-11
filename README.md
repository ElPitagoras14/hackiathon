# Project Documentation: Financial Risk Assessment for SMEs

## 1. Overview

This project develops an AI-driven credit risk scoring solution for Ecuadorian SMEs lacking formal credit history, using non-traditional data like digital social media and commercial references to improve credit access and decision-making.

[Read a more detailed description of the project.](https://hackiathon.com/en/projects/financial-risk-assessment-for-smes/)

The project is built on top of a frontend, backend, and Celery worker orchestrated by Docker Compose.

![Sequence diagram](/assets/sequence.png)

## 2. Technology Stack

- **Frontend:** NextJS with AuthJS and Shadcn/UI components.
- **Backend:** FastAPI + Celery for async processing, orchestrated by LangChain.
- **Database:** Postgres for core data storage.
- **Broker:** Redis for task queueing and caching.
- **Scraping:** Playwright for dynamic data extraction.
- **AI:** OpenAI LLMs and ChromaDB for embedding storage and retrieval.
- **Deployment:** Docker Compose.

![Architecture diagram](/assets/architecture.png)

## 3. System Architecture and Workflow Highlights

- Aggregates diverse data sources into structured features for risk evaluation.
- Combines financial metrics with social signals for explainable scoring.
- Leverages vector search for contextual benchmarking.
- Separates heavy tasks for scalability and responsiveness.
- Supports credit applications with scenario simulations.

<!-- Suggested image: workflow diagram combining data ingestion, processing, scoring, and application -->

## 4. Design Rationales

- Asynchronous task handling ensures scalability.
- Vector databases enrich semantic analysis beyond traditional methods.
- Modular NLP pipelines improve maintainability.
- Browser automation guarantees up-to-date data capture.
- Environment variables secure sensitive info and support consistent deployment.
- Emphasis on explainability builds user trust and compliance readiness.

## 5. Usage

### 5.1 Docker Compose

To deploy the full stack with Docker Compose:

1. Rename `.env.example` to `.env` and fill in environment variables.
2. Run `docker compose up -d --build` to launch all services.

All core services will launch in coordinated containers.

<!-- Suggested image: Docker Compose service layout -->

### 5.2 Local Development

To run the full stack locally:

1. Rename `.env.example` to `.env` and fill in environment variables.
2. Run the `ia-db` and `ia-redis` services with Docker Compose.
3. Create a virtual environment and install dependencies from `/backend/requirements.txt` and `/queues/requirements.txt`.
4. Install the `playwright` Chromium browser driver.
5. Install npm dependencies from `/frontend/package.json`.
6. Go to `/backend/src` and run `python main.py` to start the FastAPI api.
7. Go to `/frontend` and run `npm run dev` to start the NextJS web.
8. Go to `/queues` and run `python main.py` to start the Celery worker.

## 6. Future Enhancements

- Localized AI model refinement.
- Integration of more alternative data sources.
- Enhanced user dashboards for scenario exploration.
- Audit and compliance features.
- Dynamic worker autoscaling.

---

Made with by [ElPitagoras14](https://github.com/ElPitagoras14), [Cmeneses](https://github.com/Cmenesess) and [TingoCarlos08](https://github.com/TingoCarlos08)
