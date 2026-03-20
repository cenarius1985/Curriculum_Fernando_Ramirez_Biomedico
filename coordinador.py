import os
import sys
import shutil
import subprocess
import datetime

# Directorio donde reside este script (raíz del repo)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = SCRIPT_DIR
LOG_FILE = os.path.join(WORK_DIR, "compilation_log.txt")

def command_available(cmd):
    return shutil.which(cmd) is not None

def log_output(title, content):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n=== {title} === {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(content)
            f.write("\n")
    except Exception:
        pass

def get_tex_env():
    env = os.environ.copy()
    sep = ";" if os.name == 'nt' else ":"

    # Todo en la raíz del proyecto (estructura plana)
    paths = ["."]
    texinputs = sep.join(paths) + sep

    env["TEXINPUTS"] = texinputs
    env["BIBINPUTS"] = "." + sep
    env["BSTINPUTS"] = "." + sep

    return env

def run_command(cmd, title="Comando"):
    print(f"> Ejecutando: {' '.join(cmd)}")
    env = get_tex_env()
    try:
        proc = subprocess.run(
            cmd,
            cwd=WORK_DIR,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        log_output(title, proc.stdout + "\n" + proc.stderr)
        if proc.returncode != 0:
            print(f"Error en {title}. Ver log.")
            print(proc.stdout)
            print(proc.stderr)
            return False
        return True
    except Exception as e:
        print(f"Excepción ejecutando {title}: {e}")
        return False

def compile_full():
    if not os.path.exists(os.path.join(WORK_DIR, "main.tex")):
        print("Error: No se encuentra main.tex")
        return False

    print("=== Iniciando compilación: Curriculum Fernando Ramirez ===")

    if command_available("pdflatex"):
        print("Usando PDFLaTeX...")
        if not run_command(["pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"], "PDFLaTeX 1"):
            return False
        if os.path.exists(os.path.join(WORK_DIR, "main.aux")):
            run_command(["bibtex", "main"], "BibTeX")
        run_command(["pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"], "PDFLaTeX 2")
        run_command(["pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"], "PDFLaTeX 3")

    elif command_available("tectonic"):
        print("PDFLaTeX no encontrado. Usando Tectonic...")
        if not run_command(["tectonic", "main.tex"], "Tectonic"):
            return False
    else:
        print("Error: No se encontró ni pdflatex ni tectonic.")
        return False

    print("=== Compilación finalizada ===")
    pdf_path = os.path.join(WORK_DIR, "main.pdf")
    if os.path.exists(pdf_path):
        print(f"PDF generado exitosamente: {pdf_path}")
        return True
    else:
        print("No se generó main.pdf.")
        return False

if __name__ == "__main__":
    success = compile_full()
    sys.exit(0 if success else 1)
