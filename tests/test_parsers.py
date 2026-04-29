from alert import SDGChecker, FigaroChecker, check_and_alert, Settings


def test_sdg_found():
    html = '<div class="el-meta"> 01/01/2026 </div>'
    assert SDGChecker().check(html, "01/01/2026")


def test_sdg_not_found():
    html = '<div class="el-meta"> 02/01/2026 </div>'
    assert not SDGChecker().check(html, "01/01/2026")


def test_figaro_found():
    # create minimal structure with correct date and koobin link
    html = (
        '<table><tr><td><time datetime="2026-01-01T00:00"></time></td>'
        '<td><a href="https://koobin.com/foo">buy</a></td></tr></table>'
    )
    assert FigaroChecker().check(html, "2026-01-01")


def test_figaro_not_found_date():
    html = '<table><tr><td>No time tag here</td></tr></table>'
    assert not FigaroChecker().check(html, "2026-01-01")


def test_figaro_no_link():
    html = (
        '<table><tr><td><time datetime="2026-01-01T00:00"></time></td>'
        '<td><a href="https://example.com/">buy</a></td></tr></table>'
    )
    assert not FigaroChecker().check(html, "2026-01-01")


def test_check_and_alert_sends(monkeypatch, tmp_path):
    # patch the external effects: fetch_page returns HTML, send_email is recorded
    html = '<div class="el-meta"> 01/01/2026 </div>'
    monkeypatch.setattr("alert.fetch_page", lambda url, timeout=30: html)
    sent = {}
    def fake_send(settings):
        sent['called'] = True
    monkeypatch.setattr("alert.send_email", fake_send)

    settings = Settings(
        event_id="SDG",
        event_name="Test",
        url="https://example.com",
        target_date="01/01/2026",
        email_to=["a@example.com"],
        email_from="from@example.com",
        smtp_server="smtp",
        smtp_user="u",
        smtp_password="p",
    )
    result = check_and_alert(settings)
    assert result is True
    assert sent.get('called')


def test_check_and_alert_no_ticket(monkeypatch):
    monkeypatch.setattr("alert.fetch_page", lambda url, timeout=30: '<div></div>')
    monkeypatch.setattr("alert.send_email", lambda settings: (_ for _ in ()).throw(AssertionError("should not send")))
    settings = Settings(
        event_id="SDG",
        event_name="Test",
        url="https://example.com",
        target_date="01/01/2026",
        email_to=["a@example.com"],
        email_from="from@example.com",
        smtp_server="smtp",
        smtp_user="u",
        smtp_password="p",
    )
    assert not check_and_alert(settings)