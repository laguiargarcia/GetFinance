import subprocess
import sys
from pathlib import Path

BASE_SCRIPTS = [
    "functions.py",
    "dataBase.py"
]

PIPELINE = [
    "etl/raw2cleansed.py"
]

def build_combined_code(target_script: str) -> str:
    parts = []
    for path in BASE_SCRIPTS + [target_script]:
        code = Path(path).read_text(encoding="utf-8")
        parts.append(f"# {'='*40}\n# {path}\n# {'='*40}\n{code}\n")
    return "\n".join(parts)

def run_step(script: str) -> None:
    print(f"\n{'='*50}")
    print(f"▶ Iniciando: {script}")
    print(f"{'='*50}")

    combined_code = build_combined_code(script)

    result = subprocess.run(
        [sys.executable, "-c", combined_code],
        check=False,
    )

    if result.returncode != 0:
        print(f"\n✗ Falha em '{script}' (exit code {result.returncode}). Pipeline interrompido.")
        sys.exit(result.returncode)

    print(f"✔ Concluído: {script}")

if __name__ == "__main__":
    # Valida existência de todos os arquivos antes de começar
    all_scripts = BASE_SCRIPTS + PIPELINE
    for script in all_scripts:
        if not Path(script).exists():
            print(f"✗ Arquivo não encontrado: {script}")
            sys.exit(1)

    for script in PIPELINE:
        run_step(script)

    print("\n✔ Pipeline concluído com sucesso.")