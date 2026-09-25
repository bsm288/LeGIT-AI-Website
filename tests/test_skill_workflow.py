"""Repeatable TLC integration tests, including intentionally incorrect models."""
import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_model import run_model, sha256

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "examples/nvme-cc-enable/NVMeCCEnable.tla"
CONFIG = MODEL.with_suffix(".cfg")


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Mutation location must be unique: " + repr(old))
    return text.replace(old, new, 1)


def add_bad_action(text, action):
    text = replace_once(text, "Next ==\n", action + "\nNext ==\n    \\/ InjectedBug\n")
    return text


def dictionary_check():
    data = json.loads((ROOT / "dictionary/identifiers.json").read_text(encoding="utf-8"))
    text = re.sub(r"\(\*.*?\*\)", "", MODEL.read_text(encoding="utf-8"), flags=re.S)
    text = re.sub(r"\\\*.*", "", text)
    declarations = {}
    for kind, names in re.findall(r"\b(CONSTANTS|VARIABLES)\s+"
                                  r"([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)", text):
        for name in re.split(r"\s*,\s*", names):
            declarations[name] = kind[:-1]
    entries = data["entries"]
    assert [e["canonical"] for e in entries] == sorted(e["canonical"] for e in entries)
    assert len({e["canonical"] for e in entries}) == len(entries)
    relevant = {e["canonical"]: e for e in entries
                if any(ref.startswith("examples/nvme-cc-enable/") for ref in e["model_refs"])}
    assert set(declarations) == set(relevant), (declarations, relevant)
    for name, kind in declarations.items():
        entry = relevant[name]
        assert entry["kind"] == kind
        for field in ("meaning", "domain", "owner", "initial", "reset", "sources", "status"):
            assert entry[field], (name, field)
    source = json.loads(MODEL.with_name("source.json").read_text(encoding="utf-8"))
    valid_ids = {r["id"] for r in source["requirements"] + source["assumptions"]}
    for entry in relevant.values():
        for source_ref in entry["sources"]:
            assert source_ref["requirement_id"] in valid_ids
    pdf = ROOT / source["source"]["file"]
    # The redistributable test bundle can run without the proprietary/reference PDF.
    source_match = sha256(pdf) == source["source"]["sha256"] if pdf.exists() else None
    assert source_match is not False, "Source PDF differs from reviewed revision"
    return {"declarations": len(declarations), "status": "PASS", "source_hash_matches": source_match}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jar", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--java", default="java")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    model = MODEL.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8")
    checks = dictionary_check()
    cases = []
    for bound in (1, 2, 3):
        cases.append((f"valid-bound-{bound}", model,
                      config.replace("MaxOperations = 2", f"MaxOperations = {bound}"),
                      "PASS", "No error has been found"))
    cases.append(("valid-initial-config-b", model,
                  config.replace("InitialAdminConfig = cfgA", "InitialAdminConfig = cfgB"),
                  "PASS", "No error has been found"))

    # An illegal processing event while disabled; preserves TypeOK/count ordering.
    bug = r"""InjectedBug ==
    /\ ccEn = 0
    /\ processedCount < MaxOperations
    /\ processedCount' = processedCount + 1
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, commandPhase, completedCount>>
"""
    cases.append(("reject-disabled-processing", add_bad_action(model, bug), config,
                  "ACTION_VIOLATION", "NoWorkWhileDisabled"))
    # An illegal completion while disabled, but still no greater than processed.
    bug = r"""InjectedBug ==
    /\ ccEn = 0
    /\ completedCount < processedCount
    /\ completedCount' = completedCount + 1
    /\ UNCHANGED <<ccEn, cstsRdy, adminConfig, commandPhase, processedCount>>
"""
    cases.append(("reject-disabled-completion", add_bad_action(model, bug), config,
                  "ACTION_VIOLATION", "NoWorkWhileDisabled"))
    bad_reset = replace_once(model,
        '/\\ UNCHANGED <<cstsRdy, adminConfig, processedCount, completedCount>>',
        '/\\ adminConfig\' \\in AdminConfigValues \\ {adminConfig}\n'
        '    /\\ UNCHANGED <<cstsRdy, processedCount, completedCount>>')
    # Isolate the reset-specific check from the stronger general admin check.
    reset_config = config.replace("PROPERTY AdminWritesOnlyDisabled\n", "")
    cases.append(("reject-reset-config-loss", bad_reset, reset_config,
                  "ACTION_VIOLATION", "AdminPreservedOnReset"))
    old_reset_done = r"""    /\ ccEn = 0
    /\ cstsRdy = 1
    /\ cstsRdy' = 0
    /\ UNCHANGED <<ccEn, adminConfig, commandPhase,
                    processedCount, completedCount>>"""
    new_reset_done = r"""    /\ ccEn = 0
    /\ cstsRdy = 1
    /\ cstsRdy' = 0
    /\ adminConfig' \in AdminConfigValues \ {adminConfig}
    /\ UNCHANGED <<ccEn, commandPhase, processedCount, completedCount>>"""
    cases.append(("reject-reset-completion-config-loss",
                  replace_once(model, old_reset_done, new_reset_done), config,
                  "ACTION_VIOLATION", "AdminPreservedOnReset"))
    bad_type = replace_once(model, "processedCount' = processedCount + 1",
                             "processedCount' = MaxOperations + 1")
    cases.append(("reject-type-error", bad_type, config,
                  "INVARIANT_VIOLATION", "Invariant TypeOK is violated"))
    bad_parse = replace_once(model, "MaxOperations > 0", "MissingOperator(MaxOperations)")
    cases.append(("reject-semantic-error", bad_parse, config, "ERROR", "Unknown operator"))
    no_fairness = replace_once(model, "    /\\ WF_vars(ControllerReady)\n", "")
    cases.append(("reject-unjustified-progress", no_fairness, config,
                  "LIVENESS_VIOLATION", "EnableEventuallyReady"))
    no_reset_fairness = replace_once(model, "    /\\ WF_vars(ControllerResetDone)\n", "")
    cases.append(("reject-unjustified-reset-progress", no_reset_fairness, config,
                  "LIVENESS_VIOLATION", "ResetEventuallyDone"))
    next_block = model[model.index("Next ==\n"):model.index("(* ASSUME-PROGRESS:")]
    deadlock = replace_once(model, next_block, "Next == FALSE /\\ UNCHANGED vars\n\n")
    cases.append(("reject-deadlock", deadlock, config, "DEADLOCK", "Deadlock reached"))
    for probe in ("NoCompletionReached", "NoResetPendingReached"):
        cases.append(("witness-" + probe, model, config + "\nINVARIANT " + probe + "\n",
                      "INVARIANT_VIOLATION", "Invariant " + probe + " is violated"))

    records = []
    for name, case_model, case_config, expected, diagnostic in cases:
        with tempfile.TemporaryDirectory(prefix="legit-test-") as temp:
            temp = Path(temp)
            path = temp / MODEL.name
            path.write_text(case_model, encoding="utf-8")
            cfg = temp / CONFIG.name
            cfg.write_text(case_config, encoding="utf-8")
            actual = run_model(args.jar, path, cfg, output / name, args.java)
        log = (output / name / "tlc.log").read_text(encoding="utf-8")
        ok = actual["status"] == expected and diagnostic in log
        records.append({"case": name, "expected": expected, "actual": actual["status"],
                        "test_passed": ok, "required_diagnostic": diagnostic,
                        "states": actual["states"], "evidence": name + "/result.json"})
        print(f'{name}: {"PASS" if ok else "FAIL"} (TLC {actual["status"]})', flush=True)
    summary = {"all_passed": all(r["test_passed"] for r in records),
               "model_sha256": sha256(MODEL), "config_sha256": sha256(CONFIG),
               "dictionary_check": checks, "cases": records,
               "interpretation": "Negative tests and reachability probes intentionally fail TLC. "
                                 "Only valid-* cases are passing production configurations."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
