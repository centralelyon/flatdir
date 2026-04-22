from __future__ import annotations

import json
from pathlib import Path

from flatdir.__main__ import main
from flatdir.ics import list_ics_entries


SAMPLE_ICS = """BEGIN:VCALENDAR
PRODID:-//Example Corp//Flatdir ICS Test//EN
VERSION:2.0
BEGIN:VEVENT
DTSTART;TZID=Europe/Paris:20260422T090000
DTEND;TZID=Europe/Paris:20260422T100000
DTSTAMP:20260421T144850Z
UID:event-one@example.com
ATTENDEE:mailto:a@example.com
ATTENDEE:mailto:b@example.com
SUMMARY:Folded
 summary
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER:-P1D
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
BEGIN:VTODO
UID:todo-one@example.com
SUMMARY:Task item
END:VTODO
END:VCALENDAR
"""


def test_list_ics_entries_keeps_ics_property_names(tmp_path: Path):
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(SAMPLE_ICS, encoding="utf-8")

    entries = list_ics_entries(ics_path)

    assert len(entries) == 1
    event = entries[0]
    assert event["BEGIN"] == "VEVENT"
    assert event["UID"] == "event-one@example.com"
    assert event["SUMMARY"] == "Foldedsummary"
    assert event["DTSTART"] == {
        "value": "20260422T090000",
        "parameters": {"TZID": "Europe/Paris"},
    }
    assert event["ATTENDEE"] == ["mailto:a@example.com", "mailto:b@example.com"]
    assert event["VALARM"] == {
        "BEGIN": "VALARM",
        "ACTION": "DISPLAY",
        "TRIGGER": "-P1D",
        "DESCRIPTION": "Reminder",
        "END": "VALARM",
    }
    assert "start_date" not in event
    assert "summary" not in event


def test_cli_auto_converts_ics_file_to_json(tmp_path: Path, capsys):
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(SAMPLE_ICS, encoding="utf-8")

    rc = main([str(ics_path)])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["UID"] == "event-one@example.com"
    assert data[0]["DTEND"]["value"] == "20260422T100000"


def test_cli_can_select_non_event_component(tmp_path: Path, capsys):
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(SAMPLE_ICS, encoding="utf-8")

    rc = main(["--ics-component", "VTODO", str(ics_path)])

    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data == [{"BEGIN": "VTODO", "UID": "todo-one@example.com", "SUMMARY": "Task item", "END": "VTODO"}]


def test_cli_filters_and_writes_ics_entries(tmp_path: Path):
    ics_path = tmp_path / "calendar.ics"
    out_path = tmp_path / "calendar.json"
    ics_path.write_text(SAMPLE_ICS, encoding="utf-8")

    rc = main([
        "--ics",
        "--only", "UID=event-one@example.com",
        "--output", str(out_path),
        str(ics_path),
    ])

    assert rc == 0
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["SUMMARY"] == "Foldedsummary"
