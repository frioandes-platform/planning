#!/usr/bin/env python3
"""Capture reproducible, explicitly mocked HU24 evidence without changing IaC."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone

COMMIT = "c0944a395c8c3acd6cbdcaee6bd97a244c6f05aa"
ROOTS = ("connectivity", "dev", "test", "prod")
EXPECTED_RUNS = {"connectivity": 4, "dev": 8, "test": 2, "prod": 3}


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def successful_summaries(directory):
    rows = []
    for root in ROOTS:
        path = directory / f"{root}.jsonl"
        events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        summaries = [e["test_summary"] for e in events if e.get("type") == "test_summary"]
        if len(summaries) != 1:
            raise ValueError(f"Missing or ambiguous test summary: {root}")
        summary = summaries[0]
        if (summary.get("status") != "pass" or summary.get("failed") != 0
                or summary.get("errored") != 0 or summary.get("skipped", 0) != 0
                or summary.get("passed", 0) != EXPECTED_RUNS[root]):
            raise ValueError(f"Incomplete or unsuccessful test suite: {root}")
        rows.append((root, summary["passed"]))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iac", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="New output directory; never overwritten")
    args = parser.parse_args()
    repo, out = args.iac.expanduser().resolve(), args.out.expanduser().resolve()
    for tool in ("git", "bash", "terraform", "python3"):
        if not shutil.which(tool):
            parser.error(f"Required command not found: {tool}")
    # Export a reviewed, immutable revision, not the user's current working tree.
    check = subprocess.run(["git", "-C", str(repo), "rev-parse", f"{COMMIT}^{{commit}}"],
                           capture_output=True, text=True)
    if check.returncode or check.stdout.strip() != COMMIT:
        parser.error("Pinned commit unavailable. Run git fetch origin main inside iac first.")
    archive = subprocess.check_output(["git", "-C", str(repo), "archive", "--format=tar", COMMIT])
    out.mkdir(parents=True, exist_ok=False)
    os.chmod(out, 0o700)
    started = utc()
    record = {"iac_commit": COMMIT, "started_utc": started,
              "mode": "terraform-test-mock-provider", "authenticated_plan": False,
              "azure_deployment": False, "collector_sha256": sha(Path(__file__))}
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("ARM_", "AZURE_", "TF_VAR_", "TF_CLI_ARGS", "TF_DATA_DIR"))}
    env.update(TF_IN_AUTOMATION="1", TF_INPUT="0", PYTHONDONTWRITEBYTECODE="1")
    version = subprocess.run(["terraform", "version", "-json"], capture_output=True, text=True, env=env)
    if version.returncode:
        raise RuntimeError("Cannot obtain Terraform version")
    record["terraform_version"] = json.loads(version.stdout)["terraform_version"]
    rows, reason = [], ""
    with tempfile.TemporaryDirectory(prefix="frioandes-hu24-") as tmp:
        # Resolve symlinked temp roots (macOS /var -> /private/var) before the containment check.
        work = Path(tmp).resolve()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                target = (work / member.name).resolve()
                if not target.is_relative_to(work) or not (member.isfile() or member.isdir()):
                    raise ValueError("Unsupported archive member")
            tar.extractall(work, filter="data")
        locks_before = {root: sha(work / f"environments/{root}/.terraform.lock.hcl") for root in ROOTS}
        record["command"] = "bash scripts/check-ingest.sh"
        print("Ejecutando verificaciones simuladas; puede tardar varios minutos.", flush=True)
        print(f"Salida completa: {out / 'ejecucion.log'}", flush=True)
        with (out / "ejecucion.log").open("w") as log:
            result = subprocess.run(["bash", "scripts/check-ingest.sh"], cwd=work, env=env,
                                    stdout=log, stderr=subprocess.STDOUT)
        record["exit_code"] = result.returncode
        evidence = work / ".security-verification"
        for root in ROOTS:
            source = evidence / f"{root}.jsonl"
            if source.exists():
                shutil.copyfile(source, out / source.name)
        if result.returncode == 0:
            try:
                rows = successful_summaries(out)
                locks_after = {root: sha(work / f"environments/{root}/.terraform.lock.hcl") for root in ROOTS}
                if locks_before != locks_after:
                    raise ValueError("Provider locks changed during initialization")
            except (ValueError, KeyError, OSError) as exc:
                reason = str(exc)
        else:
            reason = "El comando falló; revisar ejecucion.log. No se declara validación completa."
    passed = record["exit_code"] == 0 and not reason and len(rows) == 4
    record.update(ended_utc=utc(), complete_mock_validation=passed,
                  provider_lock_sha256=locks_before, failure_reason=reason)
    record["evidence_sha256"] = {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()}
    (out / "manifest.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    table = "\n".join(f"| `{root}` | {count} | Aprobadas |" for root, count in rows) if passed else "| — | — | Ejecución incompleta |"
    status = "VALIDACIÓN SIMULADA COMPLETA" if passed else "VALIDACIÓN INCOMPLETA"
    report = f"""# Evidencia de planificación simulada — #24

## Alcance y estado

**{status}.** FríoAndes se desarrolla como diseño, sin suscripción de Azure.
El procedimiento ejecuta `terraform validate` y `terraform test` con
`mock_provider \"azurerm\"`. No se ejecutó el comando independiente
`terraform plan` autenticado, ni se desplegaron recursos en Azure.

El criterio literal de un plan autenticado permanece pendiente. La aceptación
de esta evidencia simulada como equivalente académico corresponde al responsable
de la historia; este documento no afirma que esa aceptación ya exista.

## Identificación de la ejecución

- Repositorio: `frioandes-platform/iac`.
- Commit exacto: [{COMMIT}](https://github.com/frioandes-platform/iac/commit/{COMMIT}).
- Inicio UTC: `{started}`.
- Fin UTC: `{record['ended_utc']}`.
- Terraform: `{record['terraform_version']}`; proveedor fijado por los locks del commit.
- Comando: `bash scripts/check-ingest.sh`.
- Código de salida: `{record['exit_code']}`.
- Fuente: copia temporal exportada mediante `git archive` del commit indicado.
  No incluye cambios locales, archivos tfvars personales ni estados existentes.

## Resultado por raíz

| Raíz | Pruebas Terraform aprobadas | Resultado |
|---|---:|---|
{table}

{reason}

## Cobertura de las historias anteriores

- **#20:** integridad de los CSV corregidos, hashes, tres VNets y 33 subredes,
  contención y ausencia de solapamientos con hub, reservas y 23 redes on-premises.
- **#21:** firewall compartido, política, NSG y comparación contra la tabla
  aprobada; reglas temporales solo en escenarios que las seleccionan explícitamente.
- **#22:** contrato del Event Hub, DNS compartido, aislamiento y referencias
  a red y NSG. También se prueban rechazos de configuraciones inválidas.

El escenario `approved_alert_contract` planifica el módulo de ingesta con datos
simulados. `private_alert_ingest_uses_existing_modules` comprueba su integración
con los módulos reales de configuración mediante un **apply simulado**, dentro
de `terraform test`; no constituye un despliegue. `disabled_by_default` por sí
solo no demostraría la cobertura de ingesta.

Las pruebas negativas con `expect_failures` deben pasar porque rechazan lo
previsto. Su éxito no significa que una configuración inválida pueda desplegarse.

## Archivos de evidencia y reproducción

La carpeta adjunta `evidencia-plan-limpio/` contiene `ejecucion.log`, las salidas
JSONL disponibles por raíz y `manifest.json` con los SHA-256, versiones y fechas.
Las salidas proceden exclusivamente de pruebas con valores sintéticos. No se
adjuntan estados, planes binarios autenticados, credenciales ni tfvars reales.

Desde el paquete de captura:

```bash
python3 capturar-evidencia.py --iac /ruta/al/iac --out /ruta/nueva/de/evidencia
```

El commit debe estar disponible localmente; se obtiene con `git fetch origin main`.
La carpeta de salida debe ser nueva. El ejecutor no cambia ramas, no crea commits
y no copia los archivos del paquete encima del repositorio.

## Límites y conclusión

Resultado de las comprobaciones simuladas: **{'sin errores inesperados' if passed else 'no confirmado'}**.
No demuestra permisos, cuotas, disponibilidad de nombres, conectividad, DNS real,
lectura/escritura de eventos ni comportamiento del proveedor frente a Azure.
No se presenta esta salida como un `terraform plan` autenticado sin errores.

Referencias: [#24](https://github.com/frioandes-platform/planning/issues/24),
[#20](https://github.com/frioandes-platform/planning/issues/20),
[#21](https://github.com/frioandes-platform/planning/issues/21) y
[#22](https://github.com/frioandes-platform/planning/issues/22).

Documentación técnica: [Terraform provider mocking](https://developer.hashicorp.com/terraform/language/tests/mocking).
"""
    (out / "evidencia-plan-limpio.md").write_text(report)
    print(f"{status}\nEvidencia: {out}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"No se completó la captura: {exc}", file=sys.stderr)
        sys.exit(1)
