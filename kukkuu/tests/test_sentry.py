import pytest
from jose import ExpiredSignatureError

from kukkuu.exceptions import AuthenticationExpiredError
from kukkuu.settings import sentry_before_send

test_cases = [
    (Exception("Unable to parse global ID."), True),
    (Exception('Unable to parse global ID "some_id".'), True),
    (ExpiredSignatureError("Expired signature"), True),
    (AuthenticationExpiredError("Authentication expired"), True),
    (Exception("Some other error"), False),
]


@pytest.mark.parametrize(
    "exception,should_return_none",
    test_cases,
)
def test_sentry_before_send_ignores_defined_exceptions(exception, should_return_none):
    hint = {"exc_info": (type(exception), exception, None)}
    event = {"something": "test event is returned when not ignored"}

    result = sentry_before_send(event, hint)

    if should_return_none:
        assert result is None  # Ensure the event is dropped
    else:
        assert result is not None  # Ensure the event is not dropped
