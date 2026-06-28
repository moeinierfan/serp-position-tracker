
🔍  SERP Position Tracker
Product Requirements Document
Cryptocurrency Keyword Ranking Tool for the Iranian Market

Version	1.0 — Initial Draft
Date	June 2026
Platform	Streamlit (Python)
Search API	Serper.dev
Target Market	Iran — Persian-language queries
Status	Ready for Development


1. Product Overview
The SERP Position Tracker is a Streamlit-based web application that enables cryptocurrency brands and SEO teams to monitor their Google Search ranking positions for Persian-language queries targeting the Iranian market. The app integrates with Serper.dev to retrieve real-time SERP data and produces structured Excel reports for analysis and archiving.
The tool is designed for recurring use: operators configure their brand, upload a coin list, build query templates, generate a query bank, and execute tracking runs — all within a single, intuitive dashboard.

2. Goals & Success Metrics
2.1  Primary Goals
•	Enable accurate position tracking of cryptocurrency-related Persian queries on Google Iran.
•	Allow non-technical users to build a rich query list via template-driven automation.
•	Deliver structured XLSX outputs with full SERP data — not just rank positions.
•	Support configurable search parameters (region, language, device, page depth).
•	Integrate brand identity so reports are professional and client-ready.

2.2  Success Metrics
Metric	Target
Query generation time (100 coins, 5 templates)	< 5 seconds
API call success rate	> 99%
Position accuracy vs. manual Google check	100% match
XLSX output completeness (all domains per page)	All results from configured pages
Brand logo/name visible on every report sheet	Yes

3. User Personas
SEO Manager
Runs weekly or daily tracking campaigns. Needs to configure once and export fast. Not necessarily a developer.
Crypto Exchange Marketing Team
Wants to benchmark their brand's visibility against competitors across high-intent crypto queries in Farsi.
Agency Analyst
Manages multiple brands. Needs the brand config feature and clean report output to hand off to clients.

4. Application Architecture & Navigation
The app is a multi-page Streamlit application organized into four main sections accessible from a sidebar:

Section / Page	Purpose
⚙️  Global Config	Brand setup, Serper API key, search parameters
📋  Template Manager	Create and manage query templates with dynamic placeholders
🚀  Tracking Dashboard	Upload coin list, generate queries, preview, run tracking
📊  Reports	View historical runs, download XLSX reports

5. Feature Specifications
5.1  Global Configuration
All settings in this section persist across sessions (stored in a local config file or Streamlit session state with file persistence).

Field	Description	Type	Required
Brand Name	Displayed on reports and dashboard header	Text input	Yes
Brand Logo	Upload PNG/JPG; rendered on XLSX report header	File upload	No
Serper API Key	Used for all Serper.dev calls; stored securely	Password input	Yes
Search Region	Google country code (default: ir)	Dropdown / text	Yes
Search Language	Language code (default: fa)	Dropdown / text	Yes
Device Type	Desktop or Mobile	Radio buttons	Yes
Number of Pages	How many SERP pages to retrieve (1 = first 10 results, 2 = 20, etc.)	Number input (1–10)	Yes

Notes
•	The region field maps to Serper.dev's `gl` parameter (e.g. 'ir' for Iran).
•	The language field maps to Serper.dev's `hl` parameter (e.g. 'fa' for Persian).
•	Pages are fetched by incrementing the `page` parameter on the Serper API call. Page 1 = results 1–10, Page 2 = results 11–20, etc.
•	Config changes apply to all future tracking runs but do not retroactively affect saved reports.

5.2  Template Manager
The Template Manager is where users build their query pattern bank. Templates use placeholder variables that reference columns from the coin list XLSX file.

5.2.1  Placeholder System
Placeholders follow the syntax: {column_name} — where column_name exactly matches a column header in the uploaded coin list file. The system is case-sensitive.

Placeholder Example	Resolves To (example)
{fa_name}	بیت‌کوین (Persian name of coin)
{en_name}	Bitcoin (English name of coin)
{symbol}	BTC (ticker symbol)
{fa_name_short}	Any custom column in the user's XLSX

5.2.2  Template CRUD Operations
•	Add Template: text input field + 'Add' button. Validates that the template is non-empty before saving.
•	View Templates: list of all saved templates with a preview of the placeholder variables detected.
•	Edit Template: inline edit or edit modal.
•	Delete Template: removes from the bank with a confirmation prompt.
•	Templates persist across sessions (saved in a local JSON or SQLite store).

5.2.3  Example Templates
Template String	Generated Query (Bitcoin example)
خرید {fa_name}	خرید بیت‌کوین
قیمت {fa_name}	قیمت بیت‌کوین
قیمت {en_name}	قیمت Bitcoin
{fa_name} چیست	بیت‌کوین چیست
خرید {en_name} در ایران	خرید Bitcoin در ایران
{symbol} price in Iran	BTC price in Iran

5.3  Coin List (XLSX Input)
Users upload a coin list as an Excel file. The file must contain at least one column that matches the placeholders used in their templates.

Required XLSX Structure (minimum)
Column Header	Description
fa_name	Persian coin name — used for {fa_name} placeholder
en_name	English coin name — used for {en_name} placeholder
symbol	Ticker symbol — used for {symbol} placeholder

Additional columns may be added by the user and referenced via custom placeholders in templates. The system dynamically reads all column headers and makes them available as placeholders.

5.4  Tracking Dashboard
The main operational screen where tracking runs are configured and executed.

5.4.1  Workflow (Step-by-Step UI)
1.	Upload Coin List XLSX — file picker; system reads and validates the file, shows column headers detected.
2.	Select Templates — multi-select list of all templates in the Template Bank. User picks which to apply to this run.
3.	Generate Query List — system iterates: for each coin × each selected template, resolve all placeholders → produce one query string per combination.
4.	Preview — display generated query list in a scrollable table showing: query string, source coin, source template. Total query count displayed prominently.
5.	Review Search Config — show current Global Config settings (region, language, device, pages) with quick-edit links. User confirms before proceeding.
6.	Start Tracking — 'Run Tracking' button triggers the API calls. Real-time progress bar shows completion (X of Y queries processed).
7.	Export Results — on completion, a 'Download XLSX' button appears. Report is also saved to the Reports history.

5.4.2  Query Generation Logic
Pseudo-code for the generation engine:
queries = []
for coin in coin_list:
    for template in selected_templates:
        query = template
        for col in coin.columns:
            query = query.replace('{'+col+'}', coin[col])
        queries.append({ query, coin, template })

5.5  SERP API Integration (Serper.dev)

5.5.1  API Call Parameters
Parameter	Value / Source
q	Generated query string
gl	From Global Config (region, e.g. 'ir')
hl	From Global Config (language, e.g. 'fa')
num	10 (results per page; Serper default)
page	Iterated from 1 to configured page count
device	From Global Config ('desktop' or 'mobile')

5.5.2  Data Extracted Per Result
•	Position number (1, 2, 3 … across all pages)
•	Result title
•	Result URL
•	Domain extracted from URL
•	Snippet / description
•	Page number the result appears on

5.5.3  Brand Position Detection
The brand name (from Global Config) is matched against result domains. When a result domain contains the brand name (case-insensitive), that row is flagged as 'Your Brand' in the output.

5.6  XLSX Output Report
5.6.1  Report Structure
•	Sheet 1 — Summary: run metadata (date, query count, config snapshot), brand logo and name in header.
•	Sheet 2 — Results (full): one row per SERP result across all queries and pages.
•	Sheet 3 — Brand Positions: filtered view showing only rows where brand domain matched.

5.6.2  Results Sheet Columns
Column Name	Description
Run Date	Timestamp of the tracking run
Query	The exact query string sent to Serper
Template	The template used to generate the query
Coin (fa_name)	Persian name of the coin
Coin (en_name)	English name of the coin
Coin (symbol)	Ticker symbol
Position	Overall rank position (1 = top result)
Page	SERP page number (1, 2, ...)
Domain	Domain extracted from result URL
Title	Page title of the result
URL	Full URL of the result
Snippet	Meta description / snippet
Is Brand	TRUE if domain matches brand name, else FALSE

5.6.3  Report Header Branding
Each sheet in the XLSX output includes a header row (rows 1–3) containing:
•	Brand logo image (if uploaded) in cell A1
•	Brand name as bold text
•	Run date and configuration snapshot (region, language, device, pages)

6. Non-Functional Requirements
Category	Requirement	Priority	Notes
Performance	Process and display 500-query preview in < 3 seconds	High	Local computation only
API Rate Limiting	Respect Serper.dev rate limits; add configurable delay between calls	High	Default: 200ms delay
Error Handling	Per-query error catching; log failures without stopping the run	High	Show error count in UI
Persistence	Templates and config survive app restarts	Medium	JSON file or SQLite
Security	API key never exposed in UI after entry (masked)	High	Use st.secrets or env vars
RTL Support	UI should handle RTL text display correctly for Persian queries	Medium	Streamlit supports this
Offline XLSX	Report fully usable without opening the app again	High	Self-contained file
Scalability	Support up to 1,000 queries per run without timeout	Medium	Add async or batch calls

7. Data Flow Diagram
High-level flow of data through the application:

Step	Data Movement
1. Config Input	User enters brand, API key, search params → stored in config.json
2. Template Creation	User writes templates → stored in templates.json
3. Coin Upload	User uploads coins.xlsx → loaded into memory as DataFrame
4. Query Generation	DataFrame × Templates → query list (List[Dict])
5. API Calls	Query list → Serper.dev API → raw SERP JSON responses
6. Data Parsing	SERP JSON → structured rows (position, domain, title, URL, etc.)
7. XLSX Export	Structured rows + brand config → formatted .xlsx file
8. History Save	Run metadata + output path → runs_history.json

8. Error Handling & Edge Cases
Scenario	Behavior	Priority	User Message
Invalid Serper API key	Show error; block run start	High	"API key is invalid. Please check your config."
Coin XLSX missing required column	Show warning listing missing columns	High	"Column '{fa_name}' not found in uploaded file."
Template placeholder not in coin list	Skip that combination; log warning	Medium	Yellow warning badge in preview
Serper API rate limit hit	Pause, retry after back-off, continue	High	"Rate limit hit. Retrying in 5s..."
No results for a query	Record row with position = 'Not Found'	Medium	Shown as blank position in XLSX
Network failure mid-run	Save partial results; allow resume or re-run	Medium	"Run interrupted. Partial results saved."
Empty template bank	Disable 'Generate Queries' button	Low	"Add at least one template to continue."
Empty coin list	Disable 'Generate Queries' button	Low	"Upload a coin list file to continue."

9. Technology Stack
Component	Technology
Frontend / App Framework	Streamlit (Python)
SERP Data API	Serper.dev REST API
HTTP Client	requests or httpx (async for large runs)
Excel Read/Write	openpyxl (write), pandas (read input XLSX)
Data Processing	pandas
Config Persistence	JSON files (config.json, templates.json, runs_history.json)
Environment Variables	python-dotenv or Streamlit secrets
URL Parsing	Python urllib.parse

10. Suggested Project File Structure
serp-tracker/
├── app.py                   # Main Streamlit entry point
├── pages/
│   ├── 1_Config.py          # Global Config page
│   ├── 2_Templates.py       # Template Manager page
│   ├── 3_Dashboard.py       # Tracking Dashboard page
│   └── 4_Reports.py         # Reports & History page
├── core/
│   ├── serper.py            # Serper.dev API client
│   ├── query_engine.py      # Template → query generation
│   ├── xlsx_writer.py       # XLSX report builder
│   └── config_store.py      # Read/write config & templates
├── data/
│   ├── config.json          # Persisted global config
│   ├── templates.json       # Template bank
│   └── runs_history.json    # Past run metadata
├── outputs/                 # Generated XLSX reports
├── assets/                  # Brand logos etc.
├── requirements.txt
└── .env                     # API key (not committed)

11. Development Milestones
Phase	Deliverable	Priority	Est. Effort
Phase 1 — Core	Global Config page + Serper API integration + basic single-query test	Critical	1–2 days
Phase 2 — Template Engine	Template Manager + query generation + preview table	Critical	1–2 days
Phase 3 — Tracking Run	Full tracking dashboard with progress bar + error handling	Critical	2–3 days
Phase 4 — XLSX Output	Branded XLSX report with all columns + brand position sheet	Critical	1–2 days
Phase 5 — Reports History	Reports page with run history + re-download	Medium	1 day
Phase 6 — Polish	RTL support, mobile view, UX refinements, async API calls	Low	1–2 days

12. Out of Scope (v1.0)
•	Scheduled / automated recurring runs (cron jobs) — manual trigger only in v1.
•	Multi-user authentication or team collaboration features.
•	Support for search engines other than Google (Bing, Yahoo, etc.).
•	Historical rank delta charts / trend visualizations (data is captured but visualization is v2).
•	Direct integration with Google Search Console.
•	Email or Slack notifications on run completion.
•	Cloud deployment pipeline (v1 runs locally or on a single-user Streamlit Cloud instance).

13. Open Questions
•	Should the coin list support multiple sheets in the XLSX, or always read the first sheet?
•	What is the maximum number of API credits available per month on the chosen Serper.dev plan? This determines the practical scale of runs.
•	Should partial-run results be saved automatically mid-run, or only on full completion?
•	Is there a need to compare results across two different runs (e.g. week-over-week delta) within the app?
•	Should the brand matching logic support multiple brand domains (e.g. main domain + sub-domains + alternative TLDs)?

End of Document  •  SERP Position Tracker PRD v1.0