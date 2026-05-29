# Study: public-apis/public-apis

Date: 2026-05-28

Source:
- https://github.com/public-apis/public-apis
- https://raw.githubusercontent.com/public-apis/public-apis/master/README.md
- https://github.com/davemachado/public-api

Findings:
- `public-apis/public-apis` is a curated Markdown catalog of free/public APIs, not a ready data service.
- Current README parsing found about 1,498 API rows across 51 categories.
- Most relevant BI demo categories: Business, Finance, Currency Exchange, Government, Open Data, Transportation, Weather, Environment, Events, Health.
- Useful metadata columns: API name, description, auth type, HTTPS support, CORS support, category, documentation URL.
- Auth distribution from parsed rows: No auth 703, apiKey 625, OAuth 150, X-Mashape-Key 6, User-Agent 1.
- HTTPS is common: 1,394 Yes, 91 No.
- CORS is often uncertain: 933 Unknown, 435 Yes, 117 No.
- The README links to the legacy `api.publicapis.org` JSON service, but local checks on 2026-05-28 failed with transfer/connection errors. Treat the Markdown source as canonical unless the API is revalidated.

Superset demo use:
- Good candidate as a seed dataset for an "API marketplace/catalog quality" dashboard.
- Prefer ingesting README from GitHub raw, parsing Markdown tables into PostgreSQL, then charting category counts, auth mix, HTTPS/CORS readiness, and BI-relevant shortlist.
- For live API integration demos, filter first to `Auth = No`, `HTTPS = Yes`, and `CORS = Yes` or server-side-only candidates with stable documentation.
