# 🔍 SERP Position Tracker

Streamlit app that tracks Google Search ranking positions for Persian-language
cryptocurrency queries in the Iranian market, using the [Serper.dev](https://serper.dev)
API, and exports branded XLSX reports.

Built to the spec in [`PRD.md`](./PRD.md).

## Features
- **Global Config** — brand identity, logo, Serper API key, region/language/device/page-depth.
- **Template Manager** — query templates with `{column}` placeholders (CRUD, persisted).
- **Tracking Dashboard** — upload coin list → generate queries → preview → run with live progress.
- **Reports** — run history with re-downloadable, self-contained XLSX reports.
- Brand-position detection, per-query error isolation, rate-limit back-off, RTL-aware UI.
- **Private per-user API keys** — each user enters their own key; it lives only in their Streamlit session and is never written to disk or shared.
- **Proxy support** — route Serper calls through an HTTP/SOCKS proxy when `google.serper.dev` is geo-blocked on your network (e.g. from Iran).

## API key & privacy model
Your Serper key is held **only in your browser session** (`st.session_state`) — it is never saved to `config.json` or committed to the repo, so no other user can see it. Enter it on **⚙️ Global Config → Your Serper API key** and click *Save key*.

For single-owner convenience you may instead set the key once via `st.secrets` or the `SERPER_API_KEY` env var (in `.env`); it will only prefill *your* session. For a public multi-user deployment, leave it unset so every visitor supplies their own.

## "API key is invalid" — it's usually a network block, not your key
`google.serper.dev` is fronted by Google infrastructure that geo-blocks some IPs (notably Iran), returning an HTML `403` that is **not** an auth error. The app now detects this and tells you to use a proxy. Fix it by setting **Proxy** on the Global Config page, e.g.:

```
socks5://127.0.0.1:1080
http://user:pass@host:port
```

Then click *Test API key* again.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: put SERPER_API_KEY here, or enter it in the UI
streamlit run app.py
```

## Usage
1. **⚙️ Global Config** — enter brand name + Serper API key, set search params, save. Use *Test API key* to verify.
2. **📋 Template Manager** — add templates such as `خرید {fa_name}`, `قیمت {en_name}`, `{symbol} price in Iran`.
3. **🚀 Tracking Dashboard** — upload your coin list (XLSX), pick templates, generate, review config, **Run Tracking**, then download the XLSX.
4. **📊 Reports** — revisit and re-download any past run.

### Coin list format
First sheet, with at least these columns (extra columns become extra placeholders):

| fa_name | en_name | symbol |
|---|---|---|
| بیت‌کوین | Bitcoin | BTC |

A ready-made example is in [`sample_coins.xlsx`](./sample_coins.xlsx).

## Report structure
- **Summary** — run metadata + brand header/logo.
- **Results (full)** — one row per SERP result (position, page, domain, title, URL, snippet, is-brand).
- **Brand Positions** — filtered rows where the brand domain matched.

## Project layout
```
app.py                 Streamlit entry point
pages/                 Config · Templates · Dashboard · Reports
core/                  serper · query_engine · xlsx_writer · config_store
data/                  config.json · templates.json · runs_history.json (runtime)
outputs/               generated XLSX reports
assets/                brand logo
```
