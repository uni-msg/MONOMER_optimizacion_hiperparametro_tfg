# Proyecto TFG: Optimización conjunta de características e hiperparámetros mediante algoritmos evolutivos sobre datos ómicos

Este repositorio contiene el código desarrollado para el desarrollo del Trabajo de Fin de Grado.

Para garantizar la compatibilidad con las librerías utilizadas y la correcta reproducción de los experimentos, se recomienda seguir las instrucciones de configuración descritas a continuación.

---

## 1. Configuración del entorno

Es **obligatorio utilizar Python 3.9** para garantizar la compatibilidad de las librerías científicas utilizadas en el proyecto. Se recomienda el uso de **Conda** para la gestión del entorno virtual.

### 1.1. Crear el entorno virtual

Desde una terminal, crear un nuevo entorno con Python 3.9:

```bash
conda create -n tfg_env python=3.9
```

Activar el entorno:

```bash
conda activate tfg_env
```

### 1.2. Instalar las dependencias

Con el entorno `tfg_env` activado, instalar las dependencias incluidas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 2. Configuración de Matplotlib

Los experimentos y scripts de generación de gráficas pueden utilizar Matplotlib durante su ejecución.

En sistemas sin entorno gráfico, sesiones remotas, clústeres o ejecuciones en segundo plano, se debe utilizar el backend no interactivo `Agg` de Matplotlib:

```bash
export MPLBACKEND=Agg
```

Se recomienda establecer esta variable antes de ejecutar `run_with_setups.py`, especialmente cuando se lanzan varios experimentos en una misma ejecución.

Puede comprobarse su valor mediante:

```bash
echo $MPLBACKEND
```

Para eliminar posteriormente la variable de entorno:

```bash
unset MPLBACKEND
```

Esta configuración solo afecta a la terminal actual.

---

## 3. Gestión de archivos grandes con Git LFS

El proyecto utiliza conjuntos de datos y archivos que pueden superar el límite de tamaño permitido por GitHub. Por este motivo, se recomienda utilizar **Git Large File Storage (Git LFS)** para gestionar los archivos pesados.

### 3.1. Instalación

En Ubuntu/Debian:

```bash
sudo apt update
sudo apt install git-lfs
```

Después de instalarlo, inicializar Git LFS:

```bash
git lfs install
```

Puede comprobarse la instalación con:

```bash
git lfs version
```

### 3.2. Añadir archivos a Git LFS

Para indicar que un determinado tipo de archivo debe ser gestionado mediante Git LFS puede utilizarse, por ejemplo:

```bash
git lfs track "*.csv"
```

Este comando crea o modifica el archivo `.gitattributes`. Este archivo también debe añadirse al repositorio:

```bash
git add .gitattributes
git commit -m "Configure Git LFS"
```

Para comprobar qué archivos están siendo gestionados mediante Git LFS:

```bash
git lfs ls-files
```

> **Importante:** `git lfs track` debe configurarse antes de añadir archivos grandes al historial de Git. Si un archivo pesado ya ha sido incluido previamente en el historial, puede ser necesario migrarlo mediante `git lfs migrate`.

---

## 4. Prueba de funcionamiento

El repositorio incluye resultados previamente calculados de un experimento de control. Esta prueba permite comprobar que el entorno ha sido configurado correctamente y que el framework produce los resultados esperados.

### Paso A: Preparar los datos de referencia

Navegar hasta la siguiente ruta:

```text
work/brca/mrna/NB_bal_acc_leanness/5_folds/
```

Localizar la carpeta:

```text
HPE_NSGA2_k3_pop500_uni0-50_gen5_CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)
```

Renombrarla añadiendo el prefijo `OLD_`:

```text
OLD_HPE_NSGA2_k3_pop500_uni0-50_gen5_CrowdCICR_c0.33_m1.0symm_(MV_lassoFI,none)
```

De esta forma, los resultados originales se conservarán y podrán compararse posteriormente con los generados por la nueva ejecución.

### Paso B: Ejecutar el experimento

> **Importante:** los scripts de experimentación deben ejecutarse siempre desde el directorio `work`.

Acceder al directorio:

```bash
cd work
```

Si todavía no se ha configurado el backend de Matplotlib:

```bash
export MPLBACKEND=Agg
```

Ejecutar el experimento de prueba:

```bash
python ../py/run_with_setups.py setups/brca/hp/test_small_nb.ini
```

### Paso C: Validar los resultados

Una vez finalizada la ejecución, volver a:

```text
work/brca/mrna/NB_bal_acc_leanness/5_folds/
```

Se habrá generado nuevamente la carpeta correspondiente al experimento.

Comparar su contenido con la carpeta que contiene los resultados originales, identificada mediante el prefijo `OLD_`.

Si los archivos generados y los resultados numéricos coinciden con los resultados de referencia, el entorno está correctamente configurado.

---

## 5. Ejecución de experimentos

Los experimentos se definen mediante archivos de configuración `.ini` almacenados dentro del directorio `work/setups`.

Las ejecuciones deben realizarse desde `work`:

```bash
cd work
```

Antes de comenzar, se recomienda configurar Matplotlib para utilizar el backend `Agg`:

```bash
export MPLBACKEND=Agg
```

### 5.1. Ejecutar una configuración

Para ejecutar un único experimento:

```bash
python ../py/run_with_setups.py setups/brca/hp/test_small_nb.ini
```

### 5.2. Ejecutar varias configuraciones

`run_with_setups.py` permite proporcionar varios archivos de configuración en una misma ejecución:

```bash
python ../py/run_with_setups.py \
    setups/brca/hp/configuracion_1.ini \
    setups/brca/hp/configuracion_2.ini \
    setups/brca/hp/configuracion_3.ini
```

Cada archivo `.ini` define los parámetros correspondientes al experimento que se desea ejecutar.

---

## 6. Generación de gráficas y análisis de resultados

El proyecto incluye diferentes scripts para generar las gráficas y análisis utilizados durante la evaluación de los experimentos.

Estos scripts deben ejecutarse desde el directorio `work`.

Desde la raíz del repositorio:

```bash
cd work
```

O, si el repositorio se encuentra en la ruta utilizada durante el desarrollo:

```bash
cd ~/tfg/MONOMER_optimizacion_hiperparametro_tfg/work
```

En entornos sin interfaz gráfica se recomienda configurar previamente Matplotlib:

```bash
export MPLBACKEND=Agg
```

### 6.1. Frentes de soluciones y gráficas generales

Para generar las gráficas comparativas de los experimentos:

```bash
PYTHONPATH=../py python ../py/plots/subplots_runner.py
```

### 6.2. Estadísticas resumen

Para generar las gráficas correspondientes a las estadísticas resumen:

```bash
PYTHONPATH=../py python ../py/plots/summary_statistics_plotter.py
```

### 6.3. Análisis de validación cruzada

Para generar los informes y gráficas asociados al análisis de validación cruzada:

```bash
python ../py/plots/cv_analysis_report.py
```

### 6.4. Gráficas utilizadas en el artículo

Para generar las gráficas preparadas para el artículo asociado al proyecto:

```bash
python ../py/plots/article_plots.py
```

### 6.5. Resultados del análisis en cascada

Para generar las gráficas correspondientes al análisis en cascada:

```bash
python ../py/plots/plot_cascade_results.py
```

### 6.6. Set Coverage

El script `plot_set_coverage.py` permite visualizar los resultados de la métrica **Set Coverage** mediante diferentes representaciones.

Matriz:

```bash
python ../py/plots/plot_set_coverage.py --setup big --plot_type matrix
```

Suite:

```bash
python ../py/plots/plot_set_coverage.py --setup big --plot_type suite
```

Pivot grid:

```bash
python ../py/plots/plot_set_coverage.py --setup big --plot_type pivotgrid
```

Big grid:

```bash
python ../py/plots/plot_set_coverage.py --setup big --plot_type biggrid
```

Metric grid:

```bash
python ../py/plots/plot_set_coverage.py --setup big --plot_type metricgrid
```

### 6.7. Análisis de hiperparámetros

Para representar la distribución de los hiperparámetros obtenidos durante la optimización:

```bash
python ../py/plots/plot_hyperparameter_distribution.py
```

Para analizar la relación entre los hiperparámetros evolucionados y los objetivos de optimización:

```bash
python ../py/plots/plot_hyperparameter_objectives.py
```

---
