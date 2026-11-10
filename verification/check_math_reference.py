"""Check mathematical, citation, and structural regression fixtures."""
import hashlib
import json

from check_english_editions import DISPLAY, INLINE, ROOT, commands, math_blocks


def fingerprint(source):
    values = {
        "display": math_blocks(source, DISPLAY),
        "inline": sorted(math_blocks(source, INLINE)),
        "labels": commands(source, "label"),
        "citations": commands(source, "cite"),
        "structure": {token: source.count(token) for token in (
            r"\chapter{", r"\section{", r"\subsection{", r"\begin{chaptersummary}",
            r"\conceptbridge{", r"\aiexercise{", r"\begin{authornote}",
            r"\begin{askai}", r"\studyroute{")},
    }
    return {key: hashlib.sha256(json.dumps(value, ensure_ascii=True, sort_keys=True).encode()).hexdigest()
            for key, value in values.items()}


def main():
    baseline = json.loads((ROOT/"verification/math_reference.json").read_text())
    for name, expected in baseline["files"].items():
        actual = fingerprint((ROOT/name).read_text())
        assert actual == expected, (name, [key for key in actual if actual[key] != expected[key]])
    print(json.dumps({"status": "passed", "source_files": len(baseline["files"]),
                      "preserved": ["display mathematics", "inline mathematics",
                                    "labels", "citations", "chapter and learning-region structure"]},
                     indent=2))


if __name__ == "__main__":
    main()
