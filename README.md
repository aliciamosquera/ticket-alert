# ticket-alert

A small script that checks a given URL for ticket availability and sends an
email alert when seats become available.

## Features

* Separate parsers for each supported site (`SDG`, `FIGARO`, …)
* Environment-variable driven configuration
* Reusable fetch and email utilities
* Logging instead of `print()`
* Unit tests for HTML parsing logic
* CI workflow via GitHub Actions

## Usage

Set the required environment variables (for example using a `.env` file):

```sh
export EVENT_ID=SDG
export EVENT_NAME="Some Concert"
export URL="https://example.com/tickets"
export TARGET_DATE="01/01/2026"
export EMAIL_TO="me@example.com, other@example.com"
export EMAIL_FROM="alert@example.com"
export SMTP_SERVER="smtp.example.com"
export SMTP_USER="user"
export SMTP_PASSWORD="password"
```

Then run:

```sh
python main.py
```

The script prints `tickets_found=true` or `tickets_found=false` and logs info to
stdout. You can call `from alert import check_and_alert` in other Python code if
you prefer.

## Testing

Install development requirements (see `requirements.txt`), then run:

```sh
pytest
```

Tests cover the checker classes with sample HTML snippets and the
`check_and_alert` function. All network/email operations are monkey‑patched, so
running `pytest` will never connect to a real SMTP server or dispatch a
message. If you want to exercise the full script yourself, point the
`SMTP_SERVER`/`SMTP_USER`/etc. at a throwaway or local mail‑catcher service
(eg. [MailHog](https://github.com/mailhog/MailHog) or a test account).

You can add new cases when supporting additional sites.

## CI / GitHub Actions

Two workflows manage the project:

### `python-app.yml` – Testing & Validation
Runs on push and pull request against `main`. Installs dependencies and
executes the test suite via `pytest`. No special secrets are required; all
tests mock network/email operations so they're safe to run anywhere.

### `check_ticket_availability.yml` – Scheduled Polling
Runs on a cron schedule (multiple times daily) and on manual trigger. Fetches
tickets from the configured URLs, sends email alerts when available, and
updates repository variables to avoid duplicate notifications. Requires
`SMTP_*` and `EMAIL_TO_*` secrets to be configured in your GitHub repository
settings.

## Extending

To add support for a new event/site:

### 1. Add a Checker class in `alert.py`

```python
class MyVenueChecker:
    def check(self, html: str, target_date: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")
        # ... parse the HTML and return True if target_date is available
        return available
```

### 2. Register it in the `CHECKERS` dict

```python
CHECKERS: Dict[str, Checker] = {
    "MY_VENUE": MyVenueChecker(),  # Add here
}
```

### 3. Add a test for the new checker

In `tests/test_parsers.py`, add test cases with sample HTML:

```python
def test_my_venue_found():
    html = "..."  # sample HTML from the venue
    assert MyVenueChecker().check(html, "01/01/2026")
```

### 4. Update the GitHub Actions workflow

In `.github/workflows/check_ticket_availability.yml`, add a matrix entry:

```yaml
- EVENT_ID: MY_VENUE
  EVENT_NAME: "My Venue Name"
  URL: ${{ vars.URL_MY_VENUE }}
  TARGET_DATE: ${{ vars.TARGET_DATE_MY_VENUE }}
  EMAIL_SENT: ${{ vars.EMAIL_SENT_MY_VENUE }}
```

### 5. Add repository variables and secrets

In GitHub repository settings > **Secrets and variables** > **Variables**, add:
- `URL_MY_VENUE` – the URL to monitor
- `TARGET_DATE_MY_VENUE` – the date to look for
- `EMAIL_SENT_MY_VENUE` – set to `false` initially

And under **Secrets**, add (if not already set):
- `EMAIL_TO_MY_VENUE` – comma-separated email addresses for this venue

---

Happy ticket hunting!
