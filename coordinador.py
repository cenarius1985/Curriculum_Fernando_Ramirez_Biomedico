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
    
    # Rutas para TEXINPUTS (fuentes, estilos, imágenes)
    # Incluimos . (root), Styles, Figures, Content, Logos, Tables
    paths = [
        ".",
        os.path.join(WORK_DIR, "Styles"),
        os.path.join(WORK_DIR, "Figures"),
        os.path.join(WORK_DIR, "Content"),
        os.path.join(WORK_DIR, "Logos"),
        os.path.join(WORK_DIR, "Tables"),
        os.path.join(WORK_DIR, "Bibliography"), # Por si acaso
    ]
    
    texinputs = sep.join(paths) + sep
    
    # Rutas para BIBINPUTS y BSTINPUTS
    bib_paths = [
        ".",
        os.path.join(WORK_DIR, "Bibliography"),
        os.path.join(WORK_DIR, "Styles")
    ]
    bibinputs = sep.join(bib_paths) + sep
    bstinputs = sep.join(bib_paths) + sep # Estilos .bst suelen estar en Styles
    
    env["TEXINPUTS"] = texinputs
    env["BIBINPUTS"] = bibinputs
    env["BSTINPUTS"] = bstinputs
    
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
            print(proc.stdout) # Mostrar stdout en caso de error para debug rápido
            return False
        return True
    except Exception as e:
        print(f"Excepción ejecutando {title}: {e}")
        return False

def compile_full():
    main_file = "main" # Asumimos main.tex
    
    if not os.path.exists("main.tex"):
        print("Error: No se encuentra main.tex")
        return

    print("=== Iniciando compilación completa ===")
    
    # Intentar primero con pdflatex (flujo estándar)
    if command_available("pdflatex"):
        print("Usando PDFLaTeX...")
        # 1. pdflatex inicial
        if not run_command(["pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"], "PDFLaTeX 1"):
            return
            
        # 2. bibtex
        if os.path.exists("main.aux"):
            run_command(["bibtex", "main"], "BibTeX")
            
        # 3. pdflatex x2 para referencias
        run_command(["pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"], "PDFLaTeX 2")
        run_command(["pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex"], "PDFLaTeX 3")

    # Si no está pdflatex, intentar con Tectonic
    elif command_available("tectonic"):
        print("PDFLaTeX no encontrado. Usando Tectonic...")
        if not run_command(["tectonic", "-X", "compile", "main.tex"], "Tectonic"):
            return
    else:
        print("Error: No se encontró ni pdflatex ni tectonic.")
        return
    
    print("=== Compilación finalizada ===")
    if os.path.exists("main.pdf"):
        print("PDF generado exitosamente: main.pdf")
        # Intentar abrir el PDF en Google Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        try:
            chrome_paths.append(r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getlogin()))
        except Exception:
            pass
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path, os.path.abspath("main.pdf")])
                    print(f"Abriendo PDF en Chrome: {path}")
                    chrome_found = True
                    break
                except Exception as e:
                    print(f"Error al abrir Chrome: {e}")
        
        if not chrome_found:
            try:
                if os.name == 'nt':
                    os.startfile("main.pdf")
                else:
                    # Intento abrir en WSL
                    subprocess.Popen(["cmd.exe", "/c", "start", "main.pdf"])
            except Exception as e:
                print("No se pudo abrir automáticamente:", e)

if __name__ == "__main__":
    compile_full()
