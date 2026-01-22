# Proyecto TFG: Framework de Experimentación

Este repositorio contiene el código base y el framework de experimentación para el desarrollo de tu Trabajo de Fin de Grado.

Sigue estrictamente estas instrucciones para configurar tu entorno de desarrollo y validar que la instalación es correcta antes de realizar cualquier modificación.

---

## 1. Configuración del Entorno

Es **obligatorio utilizar Python 3.9** para garantizar la compatibilidad de las librerías científicas. Se recomienda encarecidamente el uso de **Conda**.

### 1.1 Crear el entorno virtual
Abre una terminal en la raíz del proyecto y ejecuta los siguientes comandos para crear y activar el entorno:

```bash
# Crear un entorno nuevo llamado 'tfg_env' forzando Python 3.9
conda create -n tfg_env python=3.9

# Activar el entorno
conda activate tfg_env
```

### 1.2 Instalar dependencias
Con el entorno `tfg_env` activado, instala las librerías necesarias mediante el archivo adjunto en la raíz:

```bash
pip install -r requirements.txt
```

---

## 2. Prueba de Funcionamiento (Test de Regresión)

El repositorio incluye resultados pre-calculados de un experimento de control. Debes ejecutar este experimento en tu máquina y comprobar que obtienes exactamente los mismos resultados.

### Paso A: Preparar los datos de referencia
Para poder comparar, primero debemos renombrar los resultados existentes para que no sean sobrescritos.

1. Navega a la siguiente ruta de resultados dentro del proyecto:
   `work/brca/mrna/NB_bal_acc_leanness/2_folds/`

2. Busca la carpeta con el siguiente nombre:
   `NSGA2_k2_pop16_bin(uni0-30)_gen20_CrowdCICR_c0.33_m1.0flip_(MV_lassoFI,none)`

3. **Renómbrala** añadiendo el prefijo `OLD_` al principio.
   * *Nombre final:* `OLD_NSGA2_k2_pop16_bin(uni0-30)_gen20_CrowdCICR_c0.33_m1.0flip_(MV_lassoFI,none)`

### Paso B: Ejecutar el experimento
⚠️ **Importante:** La ejecución de los scripts debe realizarse **siempre** desde el directorio `work`.

1. Sitúate en la carpeta de trabajo:
   ```bash
   cd work
   ```

2. Ejecuta el script principal cargando la configuración de prueba (`test_small.ini`):
   ```bash
   python ../py/run_with_setups.py setups/brca/test_small.ini
   ```

### Paso C: Validación de resultados
Una vez finalice la ejecución del script:

1. Ve a la ruta del *Paso A*. Verás que se ha creado una **nueva carpeta** con el nombre original (sin `OLD_`).
2. Compara el contenido de la nueva carpeta con la carpeta `OLD_`.
3. **Validación:** Si los archivos generados y los resultados numéricos son idénticos a los de la carpeta `OLD`, tu entorno está correctamente configurado.

---

## 3. Arranque del TFG

Ahora que nos hemos asegurado de que el código base funciona es el momento de comenzar el TFG. Familiarízate con la estructura, estudia la documentación y comienza el trabajo.
No olvides actualizar la documentación en html con los cambios significativos que hagas respetando el formato actual. Será uno de tus mejores aliados.
