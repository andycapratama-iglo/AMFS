# AMFS — OrangeHRM Login Automation Suite

Playwright + pytest automation for the manual test cases in
`OrangeHRM_Login_ManualTestCases.xlsx` (TC-AUTH-001 .. TC-AUTH-015).

## Structure

```
AMFS/
├── pages/
│   ├── base_page.py       # Common Playwright wrapper actions
│   └── login_page.py      # LoginPage POM (locators + actions for the Login screen)
├── tests/
│   ├── conftest.py        # Fixtures: browser, context, page, login_page, failure screenshots
│   ├── test_tc_auth_001.py  ... test_tc_auth_015.py   # One spec file per test case
├── utils/
│   └── config.py           # Base URL, credentials, timeouts (env-overridable)
├── pytest.ini
├── requirements.txt
└── .gitignore
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Configuration

Override defaults via environment variables or a `.env` file in the repo root:

```
BASE_URL=https://opensource-demo.orangehrmlive.com
LOGIN_PATH=/web/index.php/auth/login
VALID_USERNAME=admin
VALID_PASSWORD=Admin123
HEADLESS=true
```

## Running the tests

```bash
# All tests
pytest

# Only critical (P1) tests
pytest -m p1

# A single test case
pytest tests/test_tc_auth_001.py

# With HTML report
pytest --html=report.html --self-contained-html
```

## Notes

- Each test file is self-contained and maps 1:1 to a manual test case ID.
- `conftest.py` auto-captures a screenshot to `screenshots/` on any test failure.
- Locators in `pages/login_page.py` target the OrangeHRM demo site's current DOM;
  update them if the target application's markup differs.
- TC-AUTH-009 assumes a 40-character username limit as stated in the manual test
  case; adjust `MAX_USERNAME_LENGTH` if the real app's limit differs.
