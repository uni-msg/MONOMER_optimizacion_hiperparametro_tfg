from sys import argv
import pandas as pd
from util.cross_hypervolume.cross_hypervolume import hypervolume
from util.hyperbox.hyperbox import ConcreteHyperbox0B

def check_monomer_math(file_path):
    print(f"Verificando con motor MONOMER: {file_path}")
    df = pd.read_csv(file_path)
    
    # Extraer datos Inner CV
    data = df[['inner_cv_NB_bal_acc', 'inner_cv_leanness']].dropna().values
    
    # 1. CÁLCULO CON TODOS LOS DATOS
    boxes = [ConcreteHyperbox0B.create_by_b_vals(row) for row in data]
    hv_full = hypervolume(boxes)
    print(f"Hipervolumen (CSV Completo): {hv_full}")
    
    # 2. CÁLCULO QUITANDO EL PUNTO TRIVIAL (0.2, 1.0)
    # Filtramos filas donde leanness sea exactamente 1.0
    data_filtered = df[df['inner_cv_leanness'] < 0.99][['inner_cv_NB_bal_acc', 'inner_cv_leanness']].values
    boxes_filtered = [ConcreteHyperbox0B.create_by_b_vals(row) for row in data_filtered]
    hv_filtered = hypervolume(boxes_filtered)
    print(f"Hipervolumen (Sin punto trivial): {hv_filtered}")

if __name__ == "__main__":
    # Asegúrate de poner la ruta correcta a tu CSV
    check_monomer_math(argv[1])