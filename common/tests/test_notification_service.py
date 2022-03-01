from unittest.mock import patch

from common.tests.utils import mocked_json_response


@patch("common.notification_service.requests.post")
def test_send_sms(mock_sms_post, sms_notification):
    sms_notification.send_sms("test-sender", ["0123456789", "9876543210"], "test text")
    assert mock_sms_post.call_count == 1


@patch(
    "common.notification_service.requests.post",
    return_value=mocked_json_response(data=None, status_code=404),
)
@patch("common.notification_service.logger.exception")
def test_send_sms_exceptions_passed(
    mock_sms_post, mock_logger_exception, sms_notification
):
    response = sms_notification.send_sms(
        "test-sender", ["0123456789", "9876543210"], "test text"
    )
    assert response.status_code == 404
    assert mock_logger_exception.call_count == 1
    assert mock_sms_post.call_count == 1
