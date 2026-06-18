# Basis Values Scraper

Python project for collecting basis values from multiple websites and saving one combined CSV.

## What This Project Does

- Runs all enabled scrapers from `config/scraper_config.py`
- Collects these columns:
  - `location`
  - `basis`
  - `delivery_start`
  - `delivery_end`
  - `symbol`
  - `cash_price`
  - `commodity`
- Saves one combined CSV in `data/`
- Keeps rows through January 2027
- Orders the final CSV by the configured group and location sequence

## Project Structure

```text
Basis scraping/
  config/
    scraper_config.py
  scrapers/
    base_scraper.py
    CGB_scrape.py
    gradable_scraper.py
    barchart_jsonp_scraper.py
    bushel_html_scraper.py
    agricharts_embed_scraper.py
    cihedging_scraper.py
    simple_table_scraper.py
  data/
  main.py
  requirements.txt
  run_scraper.bat
  run_scraper.ps1
```

## Setup On A New Computer

### 1. Clone or copy the repo

```powershell
git clone <your-repo-url>
cd "Basis scraping"
```

### 2. Create the virtual environment

```powershell
py -3 -m venv .venv
```

### 3. Activate it

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running The Scraper

From an activated venv:

```powershell
python main.py
```

Or use the included launchers:

```powershell
.\run_scraper.ps1
```

```cmd
run_scraper.bat
```

Both launchers now prefer `.venv\Scripts\python.exe` and fall back to `py -3`.

## Output

- Combined files are written to `data/`
- Filename format:

```text
basis_values_YYYYMMDD_HHMMSS.csv
```

## Notes

- The virtual environment `.venv/` is intentionally ignored by Git
- Generated `basis_values_*.csv` files are also ignored by Git
- Scraper enable/disable settings and output ordering are controlled in `config/scraper_config.py`
- A Playwright template file still exists in `scrapers/`, but it is not part of the active scraper set
