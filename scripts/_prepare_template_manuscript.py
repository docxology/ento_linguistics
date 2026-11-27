"""Prepare Template Markdown from the canonical paper and retained v1.3.1 evidence."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/manuscript"
OUTPUT = ROOT / "output"
REVIEW = OUTPUT / "review-v1.3.1-20261009/variables-v1.3.1-candidate.json"
NETWORK = OUTPUT / "extensions/network_reading"
FIGURE = re.compile(
    r"\\begin\{figure\}\[[^\]]*\]\s*\\centering\s*"
    r"\\includegraphics\[[^\]]*\]\{\.\./output/([^}]+)\}\s*"
    r"\\caption\{(.+?)\}\s*\\label\{([^}]+)\}\s*\\end\{figure\}",
    re.DOTALL,
)
TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
TABLE = re.compile(r"\\begin\{table\}.*?\\end\{table\}", re.DOTALL)
EQUATION = re.compile(
    r"\\begin\{equation\}\\label\{([^}]+)\}\s*(.*?)\s*\\end\{equation\}",
    re.DOTALL,
)


# Keep cross-references in display captions. Give these figures an independent
# description because the registry supplies plain text to the accessible writers.
FIGURE_ALT = {
    "fig:terminology_network": (
        "Term co-occurrence network with node area scaled by frequency and color "
        "by primary domain. A companion bar chart ranks the ten strongest term "
        "pairs by shared document count."
    ),
    "fig:domain_overlap": (
        "Heatmap of vocabulary overlap across domains. Each cell gives shared terms "
        "as a percentage of the smaller vocabulary, with 100 percent on the diagonal."
    ),
    "fig:domain_patterns_grid": (
        "Panels compare the shares of single words, multi-word phrases, compounds "
        "with hyphens or underscores, and terms containing digits across domain vocabularies."
    ),
    "fig:concept_hierarchy": (
        "Six concept categories are ranked by summed vocabulary overlap in the left "
        "panel. The right panel plots that score against each category's term count."
    ),
}


def portable_figure_record(filename: str, label: str, caption: str, digest: str) -> dict:
    """Keep the authored caption and figure digest beside the plain-text description."""
    return {
        "filename": filename,
        "label": label,
        "caption": caption,
        "alt_text": FIGURE_ALT.get(label, caption),
        "metadata": {"sha256": digest},
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_hash(path: Path, expected: str) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Retained artifact did not match its receipt: {path}")


def retained_variables() -> dict[str, str]:
    values = load_json(REVIEW)
    report = NETWORK / "network_reading.json"
    verify_hash(report, load_json(NETWORK / "receipt.json")["outputs"][report.name])
    reading = load_json(report)
    base, strict = [
        next(row for row in reading["cells"] if row["terms"] == 100 and row["threshold_documents"] == threshold)
        for threshold in (1, 20)
    ]
    values.update(
        NETREAD_CELLS=str(len(reading["cells"])),
        NETREAD_DOCUMENTS=str(reading["documents"]),
        NETREAD_BASE_DENSITY=f"{base['density']:.4f}",
        NETREAD_THRESHOLD20_EDGES=str(strict["edges"]),
        NETREAD_THRESHOLD20_DENSITY=f"{strict['density']:.4f}",
    )
    return values


def convert_table(match: re.Match[str]) -> str:
    source = match[0]
    columns = [
        re.split(r"(?<!\\)&", line.strip()[:-2])
        for line in source.splitlines()
        if line.strip().endswith(r"\\")
    ]
    width = len(columns[0])
    if any(len(row) != width for row in columns):
        raise ValueError("Inconsistent column counts in the source table")
    rows = [
        "| " + " | ".join(re.sub(r"\\textbf\{([^{}]+)\}", r"**\1**", cell.strip()) for cell in row) + " |"
        for row in columns
    ]
    rows.insert(1, "| " + " | ".join(["---"] * width) + " |")
    caption, label = re.search(
        r"\\caption\{(.+?)\}\s*\\label\{tab:([^}]+)\}", source, re.DOTALL
    ).groups()
    return "\n".join(rows) + f"\n\n: {caption} {{#tbl:{label}}}"


def prepare() -> None:
    values = retained_variables()
    native_registry = json.loads(subprocess.check_output(
        ["git", "show", "HEAD:output/figures/figure_registry.json"], cwd=ROOT
    ))
    sections = {}
    figures = {}
    portable_registry = {}
    used_values = {}

    def fill(match: re.Match[str]) -> str:
        key = match[1]
        value = values[key]
        used_values[key] = value
        return value

    def figure(match: re.Match[str]) -> str:
        relative, caption, label = match.groups()
        path = OUTPUT / relative
        if path.parent == OUTPUT / "figures":
            digest = next(
                entry["metadata"]["sha256"] for entry in native_registry.values()
                if entry["filename"] == path.name
            )
        else:
            digest = load_json(path.parent / "receipt.json")["outputs"][path.name]
        verify_hash(path, digest)
        figures[path.name] = path
        portable_registry[label] = portable_figure_record(path.name, label, caption, digest)
        return f"![{caption}](../figures/{path.name}){{#{label} width=85%}}"

    for path in sorted(SOURCE.glob("*.md")):
        if not re.fullmatch(r"(?:\d\d|S\d\d)[a-z]?_.+\.md", path.name):
            continue
        text = TOKEN.sub(fill, path.read_text(encoding="utf-8"))
        text = FIGURE.sub(figure, text)
        if r"\begin{figure}" in text:
            raise ValueError(f"Unconverted figure in {path.name}")
        text = TABLE.sub(convert_table, text)
        text = EQUATION.sub(lambda m: f"$$\n{m[2]}\n$$ {{#{m[1]}}}", text)
        text = re.sub(
            r"\\citep?\{([^}]+)\}", lambda m: "[" + "; ".join("@" + key.strip() for key in m[1].split(",")) + "]",
            text,
        )
        text = re.sub(r"\\citet\{([^}]+)\}", r"@\1", text)
        text = re.sub(r"((?:[Ff]igures?|[Tt]ables?) )\\ref\{(?:fig:|tab:)([^}]+)\}", lambda m: (
            f"[@{'fig' if m[1].lower().startswith('fig') else 'tbl'}:{m[2]}]"
        ), text)
        text = re.sub(r"\\ref\{tab:([^}]+)\}", r"[@tbl:\1]", text)
        text = re.sub(r"\\ref\{fig:([^}]+)\}", r"[@fig:\1]", text)
        text = re.sub(r"Eq\.~\\ref\{eq:([^}]+)\}", r"[@eq:\1]", text)
        # Keep existing prose prefixes and range punctuation around bare numbers.
        text = re.sub(r"\\ref\{eq:([^}]+)\}", r"[-@eq:\1]", text)
        text = re.sub(r"\\ref\{sec:([^}]+)\}", r"[\1](#sec:\1)", text)
        sections[path.name] = text

    destination = OUTPUT / "manuscript"
    registry_path = OUTPUT / "figures/figure_registry.json"
    if registry_path.exists():
        raise FileExistsError("Use a clean sparse worktree without the native figure registry.")
    destination.mkdir()
    for name, text in sections.items():
        (destination / name).write_text(text, encoding="utf-8")
    for name in ("preamble.md", "references.bib"):
        shutil.copyfile(SOURCE / name, destination / name)
    config = (SOURCE / "config.yaml").read_text(encoding="utf-8")
    config = re.sub(r"^  (?:version_doi|zenodo_record_url):.*\n", "", config, flags=re.MULTILINE)
    config = re.sub(r'^  date:.*$', '  date: "Template reproduction from retained v1.3.1 evidence"', config, flags=re.MULTILINE)
    (destination / "config.yaml").write_text("# Project-resolved config\n" + config, encoding="utf-8")
    for name, path in figures.items():
        target = OUTPUT / "figures" / name
        if path != target:
            shutil.copyfile(path, target)
    registry_path.write_text(json.dumps(portable_registry, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "manuscript-values.json").write_text(json.dumps(used_values, indent=2) + "\n")
    print(f"Prepared {len(sections)} sections, {len(used_values)} variables and {len(figures)} figures.")


if __name__ == "__main__":
    prepare()
