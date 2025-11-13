import textwrap

from gene_report_reader.parser import format_markdown_table, parse_report_text


def test_parse_report_text_extracts_key_values():
    text = textwrap.dedent(
        """
        Patient Name: Jane Doe
        Patient ID: 12345
        Sample Date - 2024-05-01
        BRCA1 c.68_69delAG Pathogenic mutation detected
        Recommendations: Consider familial testing.
        """
    )

    report = parse_report_text(text)

    expected = {
        "Patient Name": "Jane Doe",
        "Patient ID": "12345",
        "Sample Date": "2024-05-01",
        "Gene": "BRCA1",
        "Variant": "c.68_69delAG",
        "Classification": "Pathogenic",
        "Recommendations": "Consider familial testing.",
    }

    assert dict(report.key_values) == expected


def test_format_markdown_table_generates_table():
    markdown = format_markdown_table(
        [
            ("Patient Name", "Jane Doe"),
            ("Gene", "BRCA1"),
        ]
    )

    assert markdown.strip().splitlines() == [
        "| Field | Value |",
        "| --- | --- |",
        "| Patient Name | Jane Doe |",
        "| Gene | BRCA1 |",
    ]
