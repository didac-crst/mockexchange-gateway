"""tests/test_client.py

Placeholder test module for the low-level HTTP client.

Why keep a placeholder?
-----------------------
Maintaining a test file (even trivial) ensures:
    * Pytest discovers the `tests/test_client.py` path early.
    * Contributors see where to add future `HttpClient` tests (timeouts,
      error mapping, headers) instead of scattering them elsewhere.

Action Item
-----------
Replace this placeholder with real tests once the HTTP layer gains
logic beyond what is already covered by integration-style tests.
"""


def test_placeholder():
    """Trivial always-pass test.

    This prevents CI from excluding the file as "empty" and serves
    as an anchor for future, meaningful assertions.
    """
    assert True
