from notification_importers.notification_importer import NotificationFileImporter


def test_notification_file_importer_fetch_data_subject_handling(tmp_path, monkeypatch):
    monkeypatch.setattr(NotificationFileImporter, "__init__", lambda self: None)

    email_file = tmp_path / "email" / "event_published-fi.html"
    email_file.parent.mkdir(parents=True)
    email_file.write_text("<title>Email Subject</title>Email Body")

    sms_file = tmp_path / "sms" / "event_published-fi.j2"
    sms_file.parent.mkdir(parents=True)
    sms_file.write_text("SMS Body")

    # Processing email then SMS preserves email subject
    importer = NotificationFileImporter()
    importer.files = [str(email_file), str(sms_file)]
    data = importer._fetch_data()
    assert data["event_published"]["fi"]["subject"] == "Email Subject"
    assert (
        data["event_published"]["fi"]["body_html"]
        == "<title>Email Subject</title>Email Body"
    )
    assert data["event_published"]["fi"]["body_text"] == "SMS Body"

    # Processing SMS then email overwrites SMS fallback with email subject
    importer.files = [str(sms_file), str(email_file)]
    data_sms_first = importer._fetch_data()
    assert data_sms_first["event_published"]["fi"]["subject"] == "Email Subject"

    # SMS only assigns fallback subject when no subject exists
    importer.files = [str(sms_file)]
    data_sms_only = importer._fetch_data()
    assert data_sms_only["event_published"]["fi"]["subject"] == "event published"
    assert data_sms_only["event_published"]["fi"]["body_text"] == "SMS Body"
    assert "body_html" not in data_sms_only["event_published"]["fi"]
