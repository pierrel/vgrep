from pathlib import Path

from command import org_format_result, org_format_results
def test_org_format_result():
    result = {
        "text": "snippet",
        "filename": Path("note.org"),
        "line_start": 5,
        "context": "",
    }
    expected = (
        "[[note.org::5][note.org]]\n"
        "#+begin_quote\nsnippet\n#+end_quote"
    )
    assert org_format_result(result) == expected


def test_org_format_results():
    r1 = {"text": "foo", "filename": Path("a.org"), "line_start": 1, "context": ""}
    r2 = {"text": "bar", "filename": Path("b.org"), "line_start": 2, "context": ""}
    expected = f"{org_format_result(r1)}\n\n{org_format_result(r2)}"
    assert org_format_results([r1, r2]) == expected
