"""Check translation coverage, mathematical parity, reference editions, and PDFs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


DISPLAY = re.compile(
    r"\\\[(.*?)\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\2\}",
    re.S,
)
INLINE = re.compile(r"\\\((.*?)\\\)|(?<!\\)\$(?!\$)(.*?)(?<!\\)\$", re.S)
TEXT_MACRO = re.compile(r"\\(?:text|textbf|textrm|textsf|mbox)\s*\{")
CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff01-\uff60]")
LAYOUT = re.compile(r"\\(?:begin|end)\{(?:gathered|aligned)\}|\\\\(?:\[[^\]]*\])?")


def math_canonical(source):
    # Translate prose inside math without weakening checks of mathematical tokens.
    while match := TEXT_MACRO.search(source):
        end, depth = match.end(), 1
        while depth and end < len(source):
            if source[end] in "{}" and source[end - 1] != "\\":
                depth += 1 if source[end] == "{" else -1
            end += 1
        assert depth == 0, source
        source = source[:match.start()] + "<TEXT>" + source[end:]
    source = LAYOUT.sub("", source)
    source = re.sub(r"\\label\{[^}]+\}", "", source)
    source = source.translate(str.maketrans({"。": ".", "，": ",", "；": ";", "：": ":", "、": ","}))
    return re.sub(r"\s+", "", source)


def math_blocks(source, pattern):
    return [math_canonical("".join(part for part in m.groups() if part))
            for m in pattern.finditer(source)]


def commands(source, command):
    return re.findall(r"\\" + command + r"\{([^}]+)\}", source)


def compare_chapter(chinese, english):
    a, b = chinese.read_text(), english.read_text()
    assert not CJK.search(b), ("untranslated text", english)
    for command in ("label", "ref", "eqref", "cite", "begin", "end"):
        left, right = [Counter(x for x in commands(s, command)
                               if command not in ("begin", "end") or x not in ("gathered", "aligned"))
                       for s in (a, b)]
        assert left == right, (english, command)
    for token in (r"\chapter{", r"\section{", r"\subsection{", r"\learninggoals{",
                  r"\studyroute{", r"\conceptbridge{", r"\aiexercise{",
                  r"\begin{chaptersummary}", r"\begin{authornote}", r"\begin{askai}"):
        assert a.count(token) == b.count(token), (english, token)
    left, right = math_blocks(a, DISPLAY), math_blocks(b, DISPLAY)
    assert left == right, ("display math", english,
                           [(i, x, y) for i, (x, y) in enumerate(zip(left, right)) if x != y])
    left, right = Counter(math_blocks(a, INLINE)), Counter(math_blocks(b, INLINE))
    assert left == right, ("inline math", english, list((left-right).elements()), list((right-left).elements()))
    return {"display_blocks": len(math_blocks(a, DISPLAY)),
            "inline_blocks": sum(left.values()),
            "summaries": a.count(r"\begin{chaptersummary}"),
            "author_supplements": a.count(r"\conceptbridge{")+a.count(r"\begin{authornote}"),
            "AI_boxes": a.count(r"\aiexercise{")+a.count(r"\begin{askai}")}


def check_volume2():
    reference = json.loads((ROOT/"verification/volume2_reference.json").read_text())
    for name, expected in reference["files"].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    return len(reference["files"])


def check_result_tables():
    def rows(path):
        return [re.findall(r"\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", line)
                for line in path.read_text().splitlines()
                if "&" in line and line.rstrip().endswith(r"\\")]
    chinese = rows(ROOT/"Vol0_Linear_Algebra_HPC/results/summary.tex")
    english = rows(ROOT/"Vol0_Linear_Algebra_HPC_EN/appendices/results.tex")
    assert chinese == english, ("result-table numbers", chinese, english)
    return len(chinese)


def check_readme_links():
    checked = 0
    paths = [ROOT/name for name in ("README.md", "README.zh-CN.md",
                                   "CONTRIBUTING.md", "CONTRIBUTING.zh-CN.md",
                                   "Vol0_Linear_Algebra_HPC/README.md")]
    paths.extend(sorted((ROOT/"docs").rglob("*.md")))
    for path in paths:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            destination = urllib.parse.unquote(target.split("#", 1)[0])
            assert (path.parent/destination).exists(), ("broken local link", path, target)
            checked += 1
    return checked


def check_cover_authors():
    authors = {}
    for volume, stems in (
        ("0", ("Course_of_Computational_Physics_Vol0",
               "Course_of_Computational_Physics_Vol0_EN")),
        ("I", ("Course_of_Computational_Physics_Vol1_Revised",
               "Course_of_Computational_Physics_Vol1_EN")),
        ("II", ("CourseofComputationPhysics_Vol2_CN",
                "CourseofComputationPhysics_Vol2_EN")),
    ):
        pair = []
        for stem in stems:
            pdf = ROOT/(stem+".pdf")
            info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
            match = re.search(r"^Author:[ \t]*([^\n]*)$", info, re.M)
            author = " ".join(match.group(1).split()) if match else ""
            assert author, ("missing PDF author", pdf)
            cover = subprocess.check_output(
                ["pdftotext", "-f", "1", "-l", "1", str(pdf), "-"], text=True)
            assert author in " ".join(cover.split()), ("missing cover credit", pdf, author)
            pair.append(author)
        assert pair[0] == pair[1], ("bilingual author mismatch", volume, pair)
        authors[volume] = pair[0]
    return authors


def check_pdf(stem, volume):
    pdf = ROOT/(stem+".pdf")
    log = ROOT/"build"/("vol"+str(volume)+"-en")/(stem+".log")
    assert pdf.is_file(), pdf
    sources = list((ROOT/("Vol0_Linear_Algebra_HPC_EN" if volume == 0 else "vol1_revised_en")).rglob("*.tex"))
    sources.append(ROOT/(stem+".tex"))
    assert pdf.stat().st_mtime >= max(p.stat().st_mtime for p in sources), ("stale PDF", pdf)
    if log.exists():
        assert not re.search(r"^!|Missing character|Overfull \\[hv]box|undefined|multiply defined|Warning:",
                             log.read_text(), re.M), ("LaTeX warnings", log)
    subprocess.run(["qpdf", "--check", str(pdf)], check=True, capture_output=True)
    text = subprocess.check_output(["pdftotext", str(pdf), "-"], text=True)
    assert not CJK.search(text), ("CJK text in PDF", pdf)
    for label in ("Chapter Overview", "Author Supplement:", "Ask AI", "Bibliography"):
        assert label in text, (pdf, label)
    bbox = subprocess.check_output(["pdftotext", "-bbox", str(pdf), "-"], text=True)
    # Poppler may emit math-font control glyphs forbidden in XML 1.0 text nodes.
    bbox = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", bbox)
    pages = ET.fromstring(bbox).findall(".//{http://www.w3.org/1999/xhtml}page")
    for page in pages:
        width, height = float(page.attrib["width"]), float(page.attrib["height"])
        for word in page:
            x0, y0, x1, y1 = (float(word.attrib[key]) for key in ("xMin", "yMin", "xMax", "yMax"))
            assert 20 < x0 <= x1 < width-20 and 20 < y0 <= y1 < height-20, (pdf, word.text)
    fonts = subprocess.check_output(["pdffonts", str(pdf)], text=True).splitlines()[2:]
    assert fonts and all(re.search(r"\s+yes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", row)
                         for row in fonts), ("unembedded font", pdf)
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    page_count = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
    assert len(pages) == page_count, ("incomplete page bounds check", pdf)
    return page_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    report = {"Volume_II_hash_checks": check_volume2(),
              "result_table_rows": check_result_tables(),
              "local_document_links": check_readme_links(), "volumes": {}}
    if not args.sources_only:
        report["cover_authors"] = check_cover_authors()
    for volume, directory, english_dir, pattern, count in (
        (0, "Vol0_Linear_Algebra_HPC", "Vol0_Linear_Algebra_HPC_EN", "*/*.tex", 29),
        (1, "vol1_revised", "vol1_revised_en", "*.tex", 22),
    ):
        paths = sorted((ROOT/directory/"chapters").glob(pattern))
        english_paths = list((ROOT/english_dir/"chapters").glob(pattern))
        assert len(paths) == len(english_paths) == count, (volume, len(paths), len(english_paths))
        totals = Counter()
        for path in paths:
            translated = ROOT/english_dir/path.relative_to(ROOT/directory)
            totals.update(compare_chapter(path, translated))
        for path in (ROOT/english_dir).rglob("*.tex"):
            assert not CJK.search(path.read_text()), ("untranslated source", path)
        reference = "references/bibliography.tex" if volume == 0 else "references.tex"
        a, b = [(ROOT/d/reference).read_text() for d in (directory, english_dir)]
        assert commands(a, "bibitem") == commands(b, "bibitem"), ("bibliography", volume)
        record = {"chapters": count, "references": len(commands(a, "bibitem")), **totals}
        if not args.sources_only:
            record["PDF_pages"] = check_pdf("Course_of_Computational_Physics_Vol"+str(volume)+"_EN", volume)
        report["volumes"][str(volume)] = record
    print(json.dumps({"status": "passed", **report}, indent=2))


if __name__ == "__main__":
    main()
