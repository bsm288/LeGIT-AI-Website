"""Run an existing finite TLA+ model with TLC and retain evidence (Python 3.10+)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(returncode, output, timed_out=False):
    if timed_out:
        return "TIMEOUT"
    if returncode == 0 and "Model checking completed. No error has been found." in output:
        if re.search(r"\b0 states left on queue\.", output):
            return "PASS"
    if "Deadlock reached" in output:
        return "DEADLOCK"
    if ("Temporal properties were violated" in output
            or re.search(r"Temporal property .+ was violated", output)):
        return "LIVENESS_VIOLATION"
    if re.search(r"Invariant .+ is violated", output):
        return "INVARIANT_VIOLATION"
    if re.search(r"Action property .+ is violated", output):
        return "ACTION_VIOLATION"
    return "ERROR"


def configured_checks(cfg_text):
    """Read TLC INVARIANT/PROPERTY declarations, including block form."""
    checks = []
    active_kind = None
    directive = re.compile(r"^(INVARIANT|PROPERTY)\b(.*)$")
    identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    for raw in cfg_text.splitlines():
        line = raw.split("\\*", 1)[0].strip()
        if not line:
            continue
        match = directive.match(line)
        if match:
            active_kind, remainder = match.groups()
            names = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", remainder)
            checks.extend((active_kind, name) for name in names)
            continue
        if active_kind and identifier.fullmatch(line):
            checks.append((active_kind, line))
            continue
        active_kind = None
    return checks


def run_model(jar, model, config, output_dir, java="java", timeout=120):
    jar, model, config = [Path(p).resolve() for p in (jar, model, config)]
    for path in (jar, model, config):
        if not path.is_file():
            raise FileNotFoundError(path)
    java_path = shutil.which(java)
    if not java_path:
        raise FileNotFoundError("Java executable not found: " + java)
    destination = Path(output_dir).resolve()
    # Never overwrite a source directory or a previous run's evidence.
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Output directory must be new or empty: " + str(destination))
    destination.mkdir(parents=True, exist_ok=True)
    cfg_text = config.read_text(encoding="utf-8")
    checks = configured_checks(cfg_text)
    if ("INVARIANT", "TypeOK") not in checks:
        raise ValueError("This workflow requires an explicit INVARIANT TypeOK entry.")
    evidence = destination / "inputs"
    evidence.mkdir()
    # Preserve local module dependencies. Nested/external modules need explicit packaging.
    for source in model.parent.glob("*.tla"):
        shutil.copy2(source, evidence / source.name)
    shutil.copy2(config, evidence / config.name)
    command = [java_path, "-Xmx512m", "-XX:+UseParallelGC", "-cp", str(jar),
               "tlc2.TLC", "-workers", "1", "-seed", "1", "-fp", "0",
               "-config", config.name, "-metadir", "states", model.name]
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="legit-tlc-") as temp:
        sandbox = Path(temp)
        for source in evidence.iterdir():
            shutil.copy2(source, sandbox / source.name)
        timed_out = False
        try:
            process = subprocess.run(command, cwd=sandbox, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True,
                                     encoding="utf-8", errors="replace", timeout=timeout)
            returncode, output = process.returncode, process.stdout
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            returncode = None
            raw = exc.stdout or ""
            output = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
            output += "\nRUNNER: timeout; exploration is inconclusive.\n"
    (destination / "tlc.log").write_text(output, encoding="utf-8")
    counts = re.findall(r"([\d,]+) states generated, ([\d,]+) distinct states found, "
                        r"([\d,]+) states left on queue\.", output)
    depth = re.search(r"depth of the complete state graph search is (\d+)", output)
    java_version = subprocess.run([java_path, "-version"], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True,
                                  encoding="utf-8", errors="replace", timeout=15).stdout
    record = {
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "status": classify(returncode, output, timed_out), "exit_code": returncode,
        "platform": platform.platform(), "python_version": platform.python_version(),
        "java_version": java_version.strip(), "jar_sha256": sha256(jar),
        "tlc_version": next((line for line in output.splitlines() if line.startswith("TLC2 ")), None),
        "command": command, "working_directory": "isolated temporary copy of inputs/",
        "inputs": {p.name: sha256(p) for p in sorted(evidence.iterdir())},
        "checks": checks,
        "bounds": re.findall(r"(?m)^\s*(MaxOperations|AdminConfigValues|InitialAdminConfig)\s*=\s*(.+)$", cfg_text),
        "states": dict(zip(("generated", "distinct", "remaining"),
                           [int(n.replace(",", "")) for n in counts[-1]])) if counts else None,
        "depth": int(depth.group(1)) if depth else None,
        "log": "tlc.log"
    }
    (destination / "result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jar", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--java", default="java")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        record = run_model(args.jar, args.model, args.config, args.output, args.java, args.timeout)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, "NOT VERIFIED: " + str(exc) + "\n")
    print(json.dumps({"status": record["status"], "states": record["states"],
                      "evidence": str(Path(args.output).resolve())}, indent=2))
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
