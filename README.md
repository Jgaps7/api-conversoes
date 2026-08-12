# Conversion Tracking API & Analytics Dashboard

A portfolio/study project for collecting first-party conversion events, storing them in PostgreSQL, and routing eligible events to advertising platforms such as Google Ads and Meta.

The project combines backend API development, third-party integrations, event processing, authentication, logging, and analytics dashboards.

## Key Features

- Receives conversion events through a FastAPI endpoint
- Supports authenticated and anonymous event flows
- Stores event data in PostgreSQL/Supabase
- Sends eligible conversions to Google Ads and Meta integrations
- Uses API keys for authenticated platform events
- Includes rate limiting and CORS controls
- Provides event and delivery logging
- Includes a Streamlit dashboard for operational monitoring
- Supports user-level controls for enabling or disabling outbound delivery

## Tech Stack

- **Backend:** Python, FastAPI
- **Data:** PostgreSQL / Supabase, Pandas
- **Advertising APIs:** Google Ads, Meta
- **Dashboard / BI:** Streamlit, Plotly
- **Security / API Controls:** API keys, rate limiting, CORS
- **Deployment:** Procfile-compatible cloud deployment

## High-Level Flow

```text
Website / Application
        |
        v
  FastAPI /conversao
        |
        +----> Validate event and API key
        |
        +----> Persist event in PostgreSQL
        |
        +----> Google Ads integration
        |
        +----> Meta integration
        |
        v
 Streamlit monitoring dashboard
```

## Example Event Fields

The API can process information such as:

- email and phone
- IP and user agent
- page URL and referrer
- campaign and traffic source
- `gclid`, `fbclid`, `fbp`, and `fbc`
- visitor ID
- consent status
- event name and origin

## API Design

The primary event endpoint is implemented with FastAPI and validates event origin before processing. Platform-specific events require an API key, while first-party website/cookie events can be persisted without outbound platform delivery.

A per-user control determines whether stored conversions should be forwarded to advertising APIs, allowing collection and delivery to be managed independently.

## Analytics

The Streamlit layer provides an operational interface for reviewing conversion data and monitoring the system. The project uses Pandas and Plotly for data processing and visualization.

## Security Notes

- Credentials and API secrets are not intended to be stored in the repository.
- Database credentials, advertising API credentials, and application secrets should be supplied through environment variables.
- The API includes rate limiting for public endpoints.
- This repository is a portfolio/study project and should be reviewed and hardened before use in a new production environment.

## Project Context

This project was created as a practical study of first-party tracking, API integrations, event pipelines, and marketing analytics. It demonstrates the connection between backend engineering and business intelligence rather than representing a currently supported commercial product.

Client production projects are kept private due to confidentiality requirements.

## Author

**Julio Alencar**  
Applied AI & Automation Engineer  
Python • FastAPI • APIs • PostgreSQL • Automation • Analytics

- LinkedIn: https://www.linkedin.com/in/juliioalencar/
- GitHub: https://github.com/Jgaps7
