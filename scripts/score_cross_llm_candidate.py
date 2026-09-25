"""Score a cross-model NVMe CC.EN candidate and retain a reproducible TLC run."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_model import run_model

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="Directory containing Candidate.tla/.cfg/source.json/README.md")
    parser.add_argument("--jar", required=True)
    parser.add_argument("--output", required=True, help="New or empty score/evidence directory")
    parser.add_argument("--model-label", required=True)
    args = parser.parse_args()
    candidate = Path(args.candidate).resolve()
    out = Path(args.output).resolve()
    golden = json.loads((ROOT / "evaluation/cc-en-v1/golden.json").read_text(encoding="utf-8"))
    if out.exists() and any(out.iterdir()):
        parser.error("--output must be new or empty")
    out.mkdir(parents=True)
    audited_candidate = out / "candidate"
    audited_candidate.mkdir()
    for name in golden["required_artifacts"]:
        source_path = candidate / name
        if source_path.is_file():
            shutil.copy2(source_path, audited_candidate / name)
    points, notes = 0, []
    expected = set(golden["required_artifacts"])
    actual = {p.name for p in candidate.iterdir()} if candidate.is_dir() else set()
    missing = sorted(expected - actual)
    if not missing:
        points += 10
    else:
        notes.append("Missing candidate artifacts: " + ", ".join(missing))
    source = None
    try:
        source = json.loads((candidate / "source.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        notes.append("Invalid source.json: " + str(exc))
    if source:
        if source.get("source") == golden["source"]:
            points += 8
        else:
            notes.append("Source metadata/hash does not exactly match golden.json.")
        candidates = {r.get("id"): r for r in source.get("requirements", [])}
        location_count = 0
        mapping_count = 0
        for expected_req in golden["requirements"]:
            got = candidates.get(expected_req["id"])
            if got and got.get("location") == expected_req["location"]:
                location_count += 1
            if got and set(expected_req["required_checks"]).issubset(set(got.get("checks", []))):
                mapping_count += 1
        points += round(12 * location_count / len(golden["requirements"]))
        points += round(15 * mapping_count / len(golden["requirements"]))
        topics = " ".join(json.dumps(source.get(key, "")).lower() for key in ("assumptions", "exclusions"))
        absent = [t for t in golden["required_assumption_or_exclusion_topics"] if t not in topics]
        if not absent:
            points += 10
        else:
            notes.append("Assumption/exclusion topics missing: " + ", ".join(absent))
    model, config = candidate / "Candidate.tla", candidate / "Candidate.cfg"
    tlc = None
    if model.is_file() and config.is_file():
        try:
            tlc = run_model(args.jar, model, config, out / "tlc")
            enabled = {name for _, name in tlc["checks"]}
            required = set(golden["required_cfg_checks"])
            if tlc["status"] == "PASS" and required.issubset(enabled):
                points += 35
            else:
                notes.append("TLC did not pass all required checks: " + str(tlc["status"]))
        except (OSError, ValueError) as exc:
            notes.append("TLC did not execute: " + str(exc))
    else:
        notes.append("Candidate model/config not available for TLC.")
    readme = candidate / "README.md"
    if readme.is_file() and any(term in readme.read_text(encoding="utf-8").lower()
                                for term in ("finite", "bounded", "abstraction")):
        points += 5
    else:
        notes.append("README lacks a bounded-model statement.")
    if tlc and tlc["status"] == "PASS" and (out / "tlc/result.json").is_file():
        points += 5
    result = {
        "benchmark_id": golden["benchmark_id"], "model_label": args.model_label,
        "score": points, "maximum": 100, "notes": notes,
        "candidate_hashes": {p.name: digest(p) for p in candidate.iterdir() if p.is_file()},
        "candidate_evidence": "candidate/",
        "tlc": tlc,
        "manual_review": {
          "source_faithfulness_0_to_5": None, "property_correctness_0_to_5": None,
          "abstraction_disclosure_0_to_5": None, "identifier_consistency_0_to_5": None,
          "reviewer_1": None, "reviewer_2": None, "disagreements": None
        },
        "limitation": "Automated score measures artifact/source/config conformance and TLC execution. It is not a semantic accuracy score."
    }
    (out / "score.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"model_label": args.model_label, "score": points, "maximum": 100,
                      "tlc_status": None if not tlc else tlc["status"], "output": str(out)}, indent=2))
    return 0 if tlc and tlc["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
