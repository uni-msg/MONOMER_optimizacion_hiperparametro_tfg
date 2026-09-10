import os
import shutil
import glob
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

console = Console()

BEST_CLASSIFIERS = {
    "brca": "leanness_svm_bal_acc",
    "luad_lusc": "NB_bal_acc_leanness",
    "tcga_kir": "RF_bal_acc_leanness",
    "tcga_ov": "leanness_svm_bal_acc"
}

# --- CORRECCIÓN DE LA RUTA ---
# Si ejecutas "python ../py/cleanup_experiments.py" desde /work, os.getcwd() devuelve /work.
# El script anterior intentaba subir una carpeta (..), y acababa buscando en la raíz de MONOMER.
WORK_DIR = os.getcwd() 

def scan_experiments():
    experiments = {}
    searched_paths = []
    
    for dataset, obj_folder in BEST_CLASSIFIERS.items():
        search_paths = [
            os.path.join(WORK_DIR, dataset, "mrna", obj_folder, "2_folds", "*"),
            os.path.join(WORK_DIR, dataset, "mrna", obj_folder, "5_folds", "*")
        ]
        
        for search_path in search_paths:
            searched_paths.append(search_path)
            for folder_path in glob.glob(search_path):
                if os.path.isdir(folder_path):
                    exp_name = os.path.basename(folder_path)
                    if exp_name not in experiments:
                        experiments[exp_name] = {}
                    experiments[exp_name][dataset] = folder_path
                    
    return experiments, searched_paths

def parse_selection(input_str, max_val):
    selected = set()
    parts = input_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part: continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if start <= end:
                    selected.update(range(start, end + 1))
            except ValueError: pass
        else:
            try:
                val = int(part)
                selected.add(val)
            except ValueError: pass
                
    return {v for v in selected if 1 <= v <= max_val}

def main():
    while True:
        console.clear()
        console.print(Panel.fit(" 🧹 MONOMER - Gestor de Limpieza de Experimentos ", border_style="red"))
        
        experiments, searched_paths = scan_experiments()
        
        if not experiments:
            console.print("[bold green]¡Todo limpio! No se encontraron experimentos.[/bold green]")
            console.print("\n[dim]He buscado en estas rutas (¿estoy en el directorio correcto?):[/dim]")
            for p in searched_paths[:4]: # Mostramos las 4 primeras para no hacer spam
                console.print(f"[dim]  - {p}[/dim]")
            break
            
        exp_names = sorted(list(experiments.keys()))
        completos = [name for name in exp_names if len(experiments[name]) == 4]
        incompletos = [name for name in exp_names if len(experiments[name]) < 4]
        ordered_exps = incompletos + completos
        
        table = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
        table.add_column("ID", justify="right", style="magenta")
        table.add_column("Estado", justify="center")
        table.add_column("Nombre del Experimento")
        table.add_column("Datasets Presentes")
        
        for i, name in enumerate(ordered_exps):
            present_in = list(experiments[name].keys())
            if len(present_in) == 4:
                status = "[green]COMPLETO (4/4)[/green]"
                ds_str = "[dim]Todos[/dim]"
            else:
                status = f"[yellow]PARCIAL ({len(present_in)}/4)[/yellow]"
                ds_str = ", ".join(present_in)
                
            table.add_row(str(i + 1), status, name, ds_str)
            
        console.print(table)
        console.print("[cyan]Instrucciones:[/cyan] Escribe IDs separados por comas o rangos (ej: [bold]1-5, 8, 10-12[/bold]).")
        console.print("Escribe [bold red]0[/bold red] o 'q' para salir.")
        
        raw_input = Prompt.ask("\n[bold yellow]¿Qué experimentos deseas ELIMINAR?[/bold yellow]")
        
        if raw_input.strip().lower() in ['0', 'q', 'quit', 'exit']:
            break
            
        selected_ids = parse_selection(raw_input, len(ordered_exps))
        
        if not selected_ids:
            console.print("[red]Selección no válida. Pulsa Enter para intentarlo de nuevo.[/red]")
            input()
            continue
            
        exps_to_delete = [ordered_exps[i - 1] for i in selected_ids]
        
        console.print("\n[bold red]ATENCIÓN: Vas a borrar PERMANENTEMENTE los siguientes experimentos:[/bold red]")
        for exp in exps_to_delete:
            console.print(f"  - {exp}")
            
        confirm = Prompt.ask("\n¿Estás absolutamente seguro? (s/N)", choices=["s", "n", "S", "N"], default="n")
        
        if confirm.lower() == 's':
            deleted_count = 0
            with console.status("[bold red]Eliminando carpetas...[/bold red]"):
                for exp in exps_to_delete:
                    paths_dict = experiments[exp]
                    for dataset, path in paths_dict.items():
                        try:
                            shutil.rmtree(path)
                            deleted_count += 1
                        except Exception as e:
                            console.print(f"[red]Error borrando {path}: {e}[/red]")
                            
            console.print(f"\n[bold green]¡Limpieza exitosa! Se han eliminado {deleted_count} carpetas físicas.[/bold green]")
            Prompt.ask("Presiona Enter para recargar la lista")
        else:
            console.print("[green]Operación cancelada.[/green]")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Limpieza abortada por el usuario.[/yellow]")