# Web Agent

Local Python web research agent. No paid APIs. No browser needed.

## Setup
```bash
pip install -r requirements.txt
python main.py "your query here"
python main.py   # interactive mode
```

## How It Works
1. Takes your query
2. Searches DuckDuckGo (falls back to Google if DDG fails)
3. Fetches top results one by one
4. Extracts clean text from each page
5. Scores relevance to your query (keyword + density analysis)
6. Stops when a sufficient answer is found OR all results exhausted
7. Returns best result with source URL

## Scoring
- `>= 0.45` → sufficient, stops immediately
- `< 0.45`  → continues to next result
- Returns best found even if none hit threshold

## Logs
Saved to `logs/webagent_YYYYMMDD_HHMMSS.log`

## Config (in controller.py)
| Variable      | Default | Description              |
|---------------|---------|--------------------------|
| `MAX_RESULTS` | 8       | Max pages to try         |
| `MIN_SCORE`   | 0.45    | Relevance threshold      |
