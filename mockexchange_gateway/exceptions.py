"""exceptions.py

Exception hierarchy for the mockexchange-gateway.

Objectives
----------
* Provide *semantic* exceptions so calling code can branch on type instead
  of brittle string inspection.
* Map HTTP status codes to meaningful subclasses (`AuthError`, `NotFoundError`).
* Represent logical (non-HTTP) domain failures (`InsufficientFunds`).

Why custom exceptions?
----------------------
Using plain `Exception` or a single umbrella error collapses signal.
Downstream (strategies, UI, tests) often want to:
    * Retry only on network/server faults.
    * Display user-friendly messages for auth issues.
    * Abort trades immediately on insufficient funds.
Granular classes make that straightforward.

Future extension
----------------
Add more domain-specific exceptions (e.g. `OrderRejected`, `RateLimitExceeded`)
*only when actually produced* by the back-end, to keep noise low.
"""


class MockExchangeError(Exception):
    """Base exception for all gateway-related errors.

    Inherit from this to allow a single broad except clause:
        except MockExchangeError:
            ...
    while still preserving specificity via subclasses.
    """


class HTTPError(MockExchangeError):
    """Generic HTTP-layer error.

    Parameters
    ----------
    status:
        HTTP status code returned by the server.
    message:
        Human-readable message (extracted from payload or raw text).
    payload:
        Optional original parsed JSON body for additional context.

    Design Choice
    -------------
    Store `status` & `payload` as attributes (not just in the string message)
    so callers can programmatically react (e.g. log structured JSON).
    """

    def __init__(self, status: int, message: str, payload=None):
        super().__init__(f"[{status}] {message}")
        self.status = status
        self.payload = payload or {}


class AuthError(HTTPError):
    """Authentication / authorization failure (HTTP 401 or 403).

    Separate subclass allows retry logic (e.g., refreshing credentials)
    to trigger only on this branch.
    """


class NotFoundError(HTTPError):
    """Resource not found (HTTP 404).

    Distinguishing 404 avoids misleading retries (usually not helpful)
    and lets upstream code degrade gracefully (e.g. treat as 'missing state').
    """


class InsufficientFunds(MockExchangeError):
    """Raised when available balance cannot support an order.

    Origin
    ------
    Typically mapped from the `/orders/can_execute` dry-run endpoint,
    or a failed `create_order` response (if the back-end rejects it).

    Why separate from HTTPError?
    ----------------------------
    Lack of funds is a *business* condition, not a transport failure;
    surfacing it distinctly prevents misclassification as a network issue.
    """
