## 🗂️ Explorador

- 1. Introducción y Alcance
- 2. Arquitectura Global
- 3. Flujo de Datos (R ↔ Py)
- 4. El Ciclo Evolutivo
- 5. Glosario Técnico
- 6. Documentación de Archivos
- 7. Ciclo Evolutivo (GA)

- R/ Librerías propias preprocess_utils.R multi_omics_data.R Carga de datos load_tcga_ov.R load_tcga_brca.R load_tcga_kir.R luad_lusc.R
- py/ cattelani2023/ cattelani2023_utils.py best_biomarkers_table_plotter.py cattelani2023_gene_boxplots.py cattelani2023_pca_subplots.py hv_variety_subplotter.py performance_by_class_master_subplots.py performance_by_class_subplots.py subplots_for_inner_model.py subplots_runner_alltogether.py summary_statistics_subplotter.py cross_validation/ multi_objective/ cross_evaluator/ confusion_matrices_saver.py cross_hypervolume_cross_evaluator.py feature_stability_mo_cross_eval.py feature_variety_mo_cross_eval.py folds_saver.py hof_saver.py multi_objective_cross_evaluator.py two_objectives_cross_plot.py used_views.py optimizer/ nsga/ nsga_star.py nsga_types.py composite_mo_optimizer_by_fold.py ga_str_utils.py guided_forward.py guided_forward_accepting_fi.py lasso_mo.py mo_optimizer_including_feature_importance.py mo_optimizer_type.py multi_objective_optimizer.py multi_objective_optimizer.py multi_objective_optimizer_accepting_feature_importance.py optimizer_utils.py rfe_mo_optimizer.py so_to_mo_optimizer_adapter.py sweeping_ga_mo_optimizer_fi.py sweeping_ga_multi_objective_optimizer.py sweeping_strategy.py multi_objective_cross_validation.py single_objective/ optimizer/ lasso_optimizer.py single_objective_optimizer.py cross_validation.py folds.py evaluator/ workers_pool_evaluator.py mask_evaluator.py SelectEvaluator.py individual_updater.py external_validation/ run_one_external_validation.py mo_external_evaluator/ external_confusion_matrices_saver.py hof_saver.py mo_external_evaluator.py two_objectives_external_plot.py feature_importance/ feature_importance_anova.py feature_importance_average.py feature_importance_by_cox.py feature_importance_by_fold.py feature_importance_by_lasso.py feature_importance_by_univariate_cox.py feature_importance.py feature_importance_uniform.py multi_outcome_feature_importance.py multi_view_feature_importance.py mv_feature_importance_by_previous.py soft_lasso.py folds_creator/ folds_creator.py input_data_folds_creator.py input_data_k_folds_creator.py k_folds_creator.py split_folds_creator.py ga_components/ bitlist_mutation.py feature_counts_saver.py logbook_saver.py mut_flip_bit.py pop_writer.py sel_best_k.py sel_nsga2_with_secondary.py selection.py symmetric_flip.py tournament.py var_and.py sorter/ pop_sorter.py sorting_strategy.py nsga3.py nsga2_with_secondary_sorting_strategy.py sorter_with_clone_index.py nsga2_with_secondary_comparator.py ga_runner/ secondary_sorting_strategy/ secondary_sorting_strategy.py individual_attribute_manager/ crowding_distance_manager.py individual_attribute_manager.py peculiarity_manager.py social_space_manager.py ga_runner.py contextualized_ga_runner.py flip_ga_runner.py select_ga_runner.py explored_features.py progress_observer.py ga_strategy/ ga_strategy.py ga_strategy_bitlist.py ga_strategy_selector.py hall_of_fame/ hall_of_fame.py hall_of_fame_by_comparator.py hof_by_sum.py hofers.py pareto_front.py population_observer.py population_observer_factory.py hyperparam_manager/ dummy_hp_manager.py hyperparam_manager.py select_hp_manager.py individual/ fitness/ fitness.py high_best_fitness.py peculiar_fitness.py dense_individual.py fit.py Individual.py individual_by_listlike.py individual_with_context.py num_features.py peculiar_individual.py peculiar_individual_by_listlike.py peculiar_individual_dense.py peculiar_individual_sparse.py peculiar_individual_with_context.py predictive_individual.py sparse_individual.py input_data/ brca_input_creator.py class_input_creator.py input_creator.py input_creators_archive.py input_data.py input_data_utils.py kir_input_creator.py luad_lusc_input_creator.py outcome.py prad_input_creator.py swedish_input_creator.py view_prefix.py model/ model.py model_with_coef.py mask.py masked_model.py masked_mv_model.py multi_view_model.py forest.py svm.py survival_model.py objective/ balanced_accuracy_with_deviation.py composite_personal_objective.py objective_computer.py peculiarity.py personal_objective_with_model.py social_objective.py Social_objective_factory.py survival_objective_computer.py plots/ barplot.py best_genes_plotter.py best_solutions_printer.py counts_over_steps.py explored_features_plot.py feature_diversity_plots.py folds_scatter_plots.py generations_plot.py hof_stability_plots.py hof_utils.py monotonic_front.py objective_pairs_plots.py pca_subplots.py performance_by_class.py plot_consts.py plot_labels.py plot_utils.py saved_external_val.py saved_hof.py show_views.py solution_utils.py subplots.py subplots_by_strategy.py subplots_runner.py summary_statistics_plotter.py table_plot.py archives/ automated_hofs_archive.py shallow_saved_hofs_archive_cv.py shallow_saved_hofs_archive_external.py hofs_plotter/ hofs_best_trade_plotter.py hofs_measure_plotter.py hofs_plotter.py hofs_scatterplotter.py plot_setup.py plotter/ gene_boxplotter.py pca_plotter.py performance_by_class_plotter.py plotter.py postprocessing/ external_postprocessing.py postprocessing.py prediction_stats/ confusion_matrix.py stat_creator.py stat_keys.py saved_solutions/ run_best_dice.py run_cross_hypervolume.py run_fold_jaccard.py run_fold_measure.py run_measure.py run_soft_cross_hypervolume.py run_test_hypervolume.py run_weight_overlap.py saved_solution.py solution_from_algorithm.py solutions_from_files.py setup/ allowed_names.py evaluation_setup.py ga_mo_optimizer_setup.py parse_feature_importance.py parse_initial_features.py parse_objectives.py setup_reader.py setup_to_mo_optimizer.py setup_utils.py univariate_feature_selection/ parallel_anova.py univariate_feature_selection.py util/ bit_array.py cached_tuple.py components_transform.py dataframes.py grid.py list_like.py list_math.py mapper.py named.py pickability_check.py plot_results.py preconditions.py randoms.py recursive_feature_importance.py reference.py sequence_utils.py singleton.py sparse_bool_list_by_set.py stability_of_distributions.py summable.py summer.py utils.py wilcoxon_test.py concurrent/ exclusive_number.py cross_hypervolume/ cross_hypervolume.py cross_hypervolume_test.py distribution/ distribution.py uniform_distribution.py average_distribution.py hyperbox/ hyperbox.py printer/ default_log_and_out_printer.py printer.py tagged_printer.py views/ views.py worker/ work_package.py worker_state.py worker_result.py comparators.py consts.py external_validator.py load_omics_views.py load_views.py multi_view_utils.py path_utils.py preprocess_views.py run_ga_2_steps.py run_ga_separated_views.py run_one_setup.py run_with_setups.py social_space.py

# Documentación Técnica

Navega por el menú lateral para ver los detalles de cada módulo.

## 1. Introducción y Alcance

MONOMER(Multi-Objective Network Optimization for Multi-omics ER) es un framework diseñado para el descubrimiento de biomarcadores en cáncer utilizando algoritmos genéticos multiobjetivo.

### 🎯 ¿Qué problema resuelve?

Dado un conjunto de datos multi-ómicos (mRNA, miRNA, Metilación) con alta dimensionalidad (>20,000 features) y pocas muestras, MONOMER busca subconjuntos de características (firmas genéticas) que maximicen simultáneamente:

- Precisión Predictiva: Capacidad de clasificar subtipos o predecir supervivencia.
- Parsimonia (Leanness): Usar el menor número de genes posible.
- Diversidad/Peculiaridad: Encontrar mecanismos biológicos alternativos, no solo el más obvio.

### ⚠️ Alcance y Limitaciones

- Enfoque: Feature Selection (Selección de Características) supervisada.
- No resuelve: Preprocesamiento crudo (FASTQ -> Conteos), ni inferencia de redes regulatorias de novo .
- Estado: Framework de investigación. Requiere conocimientos de Python y R para configuración avanzada.

## 2. Arquitectura Global y Flujo de Ejecución

MONOMER implementa una arquitectura de computación evolutiva paralela. El sistema sigue un patrónOrquestador-Trabajadorcon estado persistente para minimizar el tráfico de datos.

### 🏗️ Vista de Componentes

### 🔄 El Ciclo Evolutivo

La lógica principal reside enga_runner.py. El ciclo incluye pasos específicos para mantener la diversidad genética (Peculiaridad).

### ⚡ Modelo de Datos y Paralelismo

El reto principal es evitar serializar grandes volúmenes de datos ómicos en cada evaluación. Los datos pesados persisten en la RAM de los workers.

`InputData`
`worker_state.py`
#### Intercambio de Mensajes

| Objeto | Rol | Contenido |
| --- | --- | --- |
| WorkPackage | Petición | Muy ligero. Solo contiene el Genotipo (lista de bits). |
| WorkerState | Contexto | Pesado. Contiene todo el Dataset (DataFrames) en memoria. |
| WorkerResult | Respuesta | Ligero. Valores de Fitness y métricas. |

## 3. Flujo de Datos e Interfaces (R ↔ Python)

MONOMER opera mediante un pipeline desacoplado. La fase deIngeniería de Datosse realiza en R (aprovechando el ecosistema Bioconductor) y la fase deAprendizaje Automáticoen Python.

### 🔄 Pipeline de Transformación

### 📂 El Contrato de Interfaz (Filesystem)

La comunicación entre R y Python se realiza exclusivamente a través de archivos CSV planos ubicados enwork/<nombre_dataset>/input/. Python no tiene conocimiento de la biología subyacente, solo ve matrices numéricas.

`InputData`
`NaN`
#### Especificación de Archivos (Inputs)

| Archivo | Rol | Formato Esperado (Pandas-ready) |
| --- | --- | --- |
| *.csv(Vistas) | Matrices de Características (X) | Filas:Muestras (Pacientes). Deben coincidir en orden y cantidad con el outcome.Columnas:Features (Genes, CpG sites).Índice:La primera columna debe ser el ID del paciente (string).Valores:float. Preferiblemente normalizados (ej. Log2 TPM, Z-score). |
| outcome.csv | Variable Objetivo (Y) | Índice:ID del paciente (debe hacer match exacto con las vistas).Columna Target:Nombre de la clase (ej.Subtype_PAM50).Supervivencia:Si es análisis de supervivencia, requiere dos columnas:time(float) yevent(bool/int). |

### 🛡️ Validaciones Automáticas en Python

Al instanciar la claseInputData, el sistema realiza las siguientes comprobaciones de integridad:

- Consistencia de Muestras: Verifica que todas las vistas y el archivo de outcome tengan exactamente el mismo número de filas (pacientes).
- Alineación (Implícita): Python asume que la fila i de mrna.csv corresponde al mismo paciente que la fila i de outcome.csv . Nota: Los scripts de carga en R ( preprocess_utils.R ) garantizan esto usando intersección de IDs antes de guardar.

## 4. El Ciclo Evolutivo (GA Workflow)

El corazón de MONOMER es un algoritmo genético diseñado para evitar la convergencia prematura mediante mecanismos de diversidad social.

### Fases del Ciclo

- Inicialización: Se crea una población de PeculiarIndividual . Se puede usar Feature Importance previa (ANOVA/Lasso) para sesgar la creación inicial (ver ga_strategy_bitlist.py ).
- Evaluación Paralela: El Master envía máscaras de bits a los Workers . Los Workers entrenan modelos (SVM, RF) con esas características y devuelven el fitness.
- Cálculo Social: Antes de seleccionar, se calculan métricas secundarias: Crowding Distance: Densidad en el espacio de objetivos. Peculiarity: Singularidad en el espacio de genotipos (ver peculiarity_manager.py ).
- Selección y Reproducción: Se usa torneo binario favoreciendo soluciones no dominadas y socialmente diversas.

## 5. Glosario Técnico

Referencia rápida de términos específicos utilizados en la arquitectura de MONOMER y sus diferencias con la literatura estándar.

#### Distinción Clave: Diversidad

MONOMER distingue dos tipos de diversidad para evitar óptimos locales:

- Crowding Distance (Fenotipo): ¿Qué tan diferentes son los resultados (Accuracy/Leanness) de esta solución respecto a sus vecinos? (Estándar NSGA-II).
- Peculiarity (Genotipo): ¿Qué tan diferentes son los genes seleccionados por esta solución respecto al promedio de la población? (Innovación de MONOMER).

### Diccionario de Términos

| Término | Definición en el Contexto de MONOMER |
| --- | --- |
| Cross Hypervolume (CHV) | Métrica de evaluación global. Generaliza el concepto de hipervolumen para validación cruzada, ponderando el volumen cubierto en el espacio de objetivos por la relación entre el rendimiento en entrenamiento y test (vercross_hypervolume.py). |
| Hall of Fame (HoF) | No es solo un registro histórico. Es la estructura dinámica que mantiene elFrente de Paretoactual (soluciones no dominadas) durante toda la ejecución. Es la fuente de verdad final del algoritmo. |
| Leanness | Objetivo de maximización definido como $1 / (1 + N_{features})$. Busca la parsimonia: modelos con menos genes tienen mayor Leanness. |
| Social Space | Métrica compuesta que combina laCrowding Distancey laPeculiarity. Se utiliza en la estrategia de ordenamiento secundaria para decidir qué individuos sobreviven cuando hay empate en dominancia. |
| View (Vista) | Una modalidad de datos ómicos específica (ej.mRNA,miRNA,cnv). MONOMER puede fusionarlas (Early Integration) o tratarlas por separado. |
| PeculiarIndividual | La unidad básica de evolución. A diferencia de un individuo estándar de algoritmos genéticos, este objeto transporta su contexto social y mantiene optimizaciones de memoria (Sparse Bitvectors) para manejar miles de genes. |
| Clone Index | Mecanismo de penalización. Si dos individuos tienen el mismo genotipo, se les asigna un índice (0 para el original, 1, 2... para las copias) que degrada artificialmente su rango en el torneo de selección para forzar la diversidad. |
| Early Integration | Estrategia de fusión de datos donde todas las vistas (matrices) se concatenan en una única gran matriz antes de entrar al algoritmo de aprendizaje. |

## A. Árbol de Llamadas Detallado (Static Call Graph)

Este diagrama representa la secuencia exacta de invocación. Incluye el flujo detallado de todos los algoritmos, incluyendo el bucle generacional del Genético.

## B. Detalle del Ciclo Evolutivo (Todos los Archivos)

Este diagrama mapea la totalidad de los archivos Python involucrados en una ejecución de Algoritmo Genético (classic_ga), maximizando el uso del espacio vertical disponible.

## 👋 Bienvenido

Selecciona un archivo del menú lateral para ver su documentación, dependencias y funciones.

## preprocess_utils.R

Librería de utilidades para la carga, preprocesamiento y normalización de datos genómicos (TCGA).
                    Contiene funciones auxiliares invocadas por los scripts de carga.

### Funciones Definidas

| Nombre | Entrada / Salida | Descripción Técnica |
| --- | --- | --- |
| save_view | Input:data, name, dirOutput:.csv file | Verifica la existencia del directorio y guarda el dataframe como CSV. |
| single_to_multi_view | Input:whole, label_posOutput:list(features, labels) | Separa una matriz mixta en una lista conteniendo features y labels por separado. |
| load_tumor | Input:tumor_codeOutput:Matrix | Carga datosRNASeq2GeneNormpara un código de enfermedad específico usandocuratedTCGAData. Filtra muestras primarias ("01"). |
| load_tumours | Input:vector(codes)Output:Matrix | Itera sobreload_tumorpara múltiples cánceres y combina los resultados
                                (cbind). |
| reduce_to_common_patient_ids_and_save | Input:data, ids, dirOutput:Matrix (file) | Intercepta los IDs de pacientes proporcionados con las columnas de datos, transpone la
                                matriz y guarda el resultado. |
| upper_quartile_normalization | Input:dataOutput:data (normalized) | Aplica normalización UQ: divide cada muestra por su percentil 75. |
| rpm_to_tpm | Input:rpm_matrixOutput:tpm_matrix | Convierte RPM a TPM. Descarga anotacionesgencode.v40y usabiomaRtpara calcular longitudes de genes. |

## multi_omics_data.R

Módulo avanzado para la gestión de datos multi-ómicos. Implementa lógica para carga, imputación de
                    valores perdidos, fusión de datasets y análisis diferencial.

### Funciones Definidas

| Nombre | Entrada / Salida | Descripción Técnica |
| --- | --- | --- |
| get_multi_omics_data | Input:cancer, path, flags...Output:List | Carga ficheros CSV.gz (mrna, mirna, meth, cnv). Realiza imputación KNN en metilación,
                                filtra muestras duplicadas y alinea IDs. |
| get_selected_multi_omics_data | Input:cancers_listOutput:List | Wrapper que ejecutaget_multi_omics_datapara múltiples cánceres y fusiona
                                los resultados usando utilidades deCOPS. |
| read_csv_with_retry | Input:pathOutput:data.frame | Intenta leer un CSV hastamax_retryveces en caso de fallo de I/O. |
| nonnegative_transform | Input:List(omics)Output:List(omics) | Transforma datos específicos: RPPA (rank), Metilación (logit a prob), CNV (shift +2). |

## load_tcga_ov.R

Script de ejecución para la generación del dataset de Cáncer de Ovario (OV).

### Configuración

- Dataset: TCGA-OV
- Directorio Salida: work/tcga_ov/input/
- ID Length: 20 caracteres

### Lógica del Pipeline

- Carga de Expresión: Invoca load_tumours("OV") .
- Carga de Etiquetas: Obtiene subtipos desde PanCancerAtlas_subtypes() .
- Intersección: Filtra muestras comunes entre expresión y subtipos usando pan.samplesID .
- Persistencia: Guarda outcome.csv (Subtipos). Guarda mrna.csv (Expresión transpuesta) mediante reduce_to_common_patient_ids_and_save .

## load_tcga_brca.R

Script de ejecución para la generación del dataset de Cáncer de Mama (BRCA).

### Configuración

- Dataset: TCGA-BRCA
- Directorio Salida: work/brca/input/
- Assay: RNASeq2GeneNorm (RSEM TPM UQ)
- Variable Objetivo: BRCA_Subtype_PAM50

### Lógica del Pipeline

- Carga de Datos: Descarga datos mediante curatedTCGAData versión
                        2.0.1.
- Procesamiento de Etiquetas: Obtiene subtipos PAM50 vía TCGAbiolinks y establece el índice por paciente (12 caracteres).
- Validación: Verifica la coincidencia de IDs entre datos clínicos y genómicos;
                        alerta si hay discrepancias.
- Persistencia: Guarda outcome.csv (Solo pacientes con subtipo PAM50 válido). Guarda mrna.csv filtrado por los pacientes comunes.

## load_tcga_kir.R

Script de ejecución para datasets de Riñón (Pan-Kidney: KIRC, KIRP, KICH).

### Configuración

- Datasets: KIRC, KIRP, KICH
- Input Externo: work/tcga_kir/raw/NIHMS958988-supplement-2.xlsx
- Directorio Salida 1: work/tcga_kir/input/ (Etiquetas originales)
- Directorio Salida 2: work/tcga_kir3/input/ (Etiquetas agrupadas)

### Lógica del Pipeline

- Carga Masiva: Invoca load_tumours para los 3 códigos de cáncer.
- Procesamiento de Etiquetas: Lee Excel suplementario. Elimina outcomes "KIRP CIMP" y "PRCC Unc". Filtra filas sin bcr_patient_barcode .
- Generación Dataset 1 (KIR): Intersecta IDs y guarda outcomes y mRNA.
- Generación Dataset 2 (KIR3): Agrupa "PRCC T1" y "PRCC T2" bajo la etiqueta
                        "PRCC". Guarda outcomes modificados y mRNA.

## luad_lusc.R

Script de ejecución para datasets de Pulmón (Combinación LUAD + LUSC).

### Configuración

- Datasets: LUAD, LUSC
- Directorio Salida: work/luad_lusc/input/
- Assay: RNASeq2GeneNorm

### Lógica del Pipeline

- Carga Independiente: Carga LUAD y LUSC por separado.
- Filtrado de Muestras: Selecciona solo muestras de tumor primario ("01") usando splitAssays .
- Estandarización: Normaliza nombres de columnas de subtipos
                        ( Expression.Subtype -> expression_subtype ).
- Intersección Local: Filtra cada dataset (LUAD/LUSC) contra sus propias
                        etiquetas disponibles.
- Fusión: Combina matrices de expresión ( cbind ). Combina tablas de etiquetas ( rbind ).
- Persistencia: Guarda outcome.csv y mrna.csv combinados.

## named.py

Define interfaces abstractas para objetos que requieren una representación de cadena específica o un
                    "apodo" (nickname). Utilizado para estandarizar la salida de logs y nombres de experimentos.

### Clases Definidas

| Clase | Métodos | Descripción Técnica |
| --- | --- | --- |
| Named | name() | Clase base. Proporciona un métodoname()que devuelvestr(self)por defecto. |
| NickNamed | nick()(Abstracto)name() | Hereda deNamed. Fuerza la implementación denick(). Redirigename()para devolver el nickname. |

## preconditions.py

Módulo de programación defensiva para validación de argumentos en tiempo de ejecución.

### Funciones Definidas

| Nombre | Entrada / Salida | Descripción Técnica |
| --- | --- | --- |
| check_none | Input:xOutput:x | Verifica si el objeto esNone. LanzaValueErrorsi lo es,
                                devuelve el objeto si no. |

## dataframes.py

Colección de utilidades para la manipulación, limpieza y validación dePandas
                        DataFrames. Incluye funciones para detección de valores no finitos (NaN/Inf) y
                    normalización estadística.

### Funciones Principales

| Nombre | Entrada / Salida | Descripción Técnica |
| --- | --- | --- |
| standardize_df | Input:DataFrameOutput:DataFrame | Aplica Z-score normalization (media 0, desviación 1) usandoStandardScalerde sklearn, preservando índices y columnas. |
| has_nan / has_inf | Input:DataFrameOutput:bool | Detecta la presencia de valores nulos o infinitos en el dataframe. |
| non_finite_report | Input:DataFrameOutput:str | Genera un reporte textual detallado con el conteo y ubicación de valores inválidos
                                (NaN/Inf). Útil para logs de errores. |
| select_cols_by_mask | Input:df, mask(list[bool])Output:DataFrame | Filtra columnas aplicando una máscara booleana. Esencial para la selección de
                                características (Feature Selection). |
| select_columns_by_prefix | Input:df, prefixOutput:DataFrame | Retorna un subconjunto del dataframe con columnas que comienzan con un prefijo dado. |

## list_math.py

Librería de operaciones matemáticas y estadísticas sobre listas y vectores. Implementa métricas de
                    similitud críticas para la evaluación de estabilidad de biomarcadores.

### Funciones Principales

| Nombre | Entrada / Salida | Descripción Técnica |
| --- | --- | --- |
| jaccard | Input:list_a, list_bOutput:float | Calcula el índice de Jaccard (Intersección sobre Unión) para dos listas binarias o de
                                enteros. |
| dice | Input:list_a, list_bOutput:float | Calcula el coeficiente Dice (2*Intersección / Suma de elementos). Usado para medir
                                estabilidad de características. |
| dot_product | Input:list_a, list_bOutput:float | Calcula el producto escalar usando suma compensada de Kahan (mayor precisión flotante). |
| vector_mean | Input:vectors (list[list])Output:list | Calcula el vector promedio de una secuencia de vectores. |
| top_k_positions | Input:elems, kOutput:indices | Devuelve los índices de loskelementos mayores, ordenados
                                descendentemente. Utiliza ordenamiento estable. |

## utils.py

Utilidades de propósito general: manejo de sistema de archivos, formateo de cadenas, control de I/O y
                    correcciones estadísticas.

### Funciones Principales

| Nombre | Entrada / Salida | Descripción Técnica |
| --- | --- | --- |
| p_adjust_bh | Input:p_valuesOutput:q_values | Implementación de la corrección deBenjamini-Hochbergpara múltiples
                                tests de hipótesis (control de False Discovery Rate). |
| suppress_stdout_stderr | Input:NoneOutput:ContextManager | Context manager para silenciar temporalmente la salida estándar y de error (redirige adevnull). |
| feature_names | Input:cols, active_posOutput:list[str] | Mapea índices de características activas (enteros) a sus nombres reales de columna. |
| pretty_duration | Input:secondsOutput:str | Formatea segundos en cadena legibleDD-HH:MM:SS. |
| files_by_extesion | Input:dir, extOutput:list[path] | Lista todos los archivos en un directorio con la extensión dada. |

## summer.py

Implementa estrategias de suma de punto flotante para mitigar errores de precisión numérica.

### Clases Definidas

- KahanSummer : Implementa el Algoritmo de Suma de Kahan (Summation Compensation). Mantiene una variable de compensación para recuperar bits perdidos.

## sparse_bool_list_by_set.py

Estructura de datos optimizada para vectores binarios dispersos (Sparse Boolean Vectors). En lugar de
                    guardar miles deFalsey unos pocosTrue, almacena solo los índices de los
                    valores verdaderos en unSortedSet.

### Clase: SparseBoolListBySet

Esta clase actúa como una lista booleana pero optimiza drásticamente el espacio y la velocidad de
                    operaciones de conjuntos.

| Método / Función | Entrada / Salida | Propósito |
| --- | --- | --- |
| __init__ | seq,min_size | Inicializa el conjunto disperso. Puede convertir listas normales o copiar otras listas
                                dispersas. |
| dot_product | Input:list_bOutput:int | Calcula el producto punto optimizado (intersección de índices activos) sin recorrer los
                                ceros. |
| union_sparse | Input:iter(SparseBoolList) | Realiza la unión eficiente de múltiples vectores dispersos. |
| jaccard_score | Input:y_true, y_pred | Calcula la similitud de Jaccard aprovechando la estructura de conjuntos (intersección /
                                unión) de forma muy eficiente. |
| top_k_mask | Input:elems, k | Crea una máscara dispersa activando solo los índices de loskvalores más
                                altos de la entrada. |

## bit_array.py

Wrapper para la compresión de arrays booleanos utilizando empaquetado de bits.

### Funcionalidad

- Compresión: Usa numpy.packbits en el constructor para almacenar 8
                        booleanos en 1 byte.
- Descompresión: Método unpack() restaura el array original usando numpy.unpackbits .
- Uso: Reduce la huella de memoria cuando se deben almacenar grandes poblaciones
                        de soluciones en el algoritmo genético.

## randoms.py

Gestión centralizada de semillas aleatorias para garantizar lareproducibilidadcientífica.

### Funciones

| Nombre | Descripción |
| --- | --- |
| set_all_seeds | Establece la semilla tanto para el módulo nativorandomcomo paranumpy.randomsimultáneamente. Valor por defecto: 42. |
| random_seed | Genera una semilla aleatoria nueva en el rango de 32 bits ($0$ a $2^{32}$). |

## summable.py

Definición de Interfaces Abstractas (ABC) para polimorfismo.

- Summable : Define que un objeto debe implementar el método sum() .
- SummableSequence : Intersección de Summable y Sequence .

## wilcoxon_test.py

Script wrapper/test para la prueba de rangos con signo de Wilcoxon.

Importascipy.stats.wilcoxon. Actualmente contiene un bloque de prueba desactivado. Se
                    utiliza probablemente para validación estadística rápida o verificación de dependencias.

## list_like.py

Define la interfaz abstractaListLike, fundamental para manejar estructuras de datos que
                    se comportan como listas pero pueden tener implementaciones internas complejas (como vectores
                    dispersos).

### Clase Abstracta: ListLike

Hereda deSummableSequence. Fuerza la implementación de operaciones de lista estándar
                    (__getitem__,__len__, etc.) y añade métodos optimizables.

| Método | Descripción |
| --- | --- |
| true_positions() | Devuelve unSortedSetcon los índices donde el valor es verdadero (o no
                                cero). Permite iteración eficiente sobre elementos activos. |
| __eq__ / __ne__ | Implementación optimizada de igualdad. Compara longitudes primero y usa iteradores para
                                evitar cargar todo en memoria si es posible. |
| to_numpy() | Contrato para convertir la estructura interna a un array de NumPy estándar. |

## cross_hypervolume.py

Implementación del algoritmoCross Hypervolume (CHV)propuesto en el artículo. Esta
                    métrica generaliza el hipervolumen para escenarios de validación cruzada, permitiendo evaluar
                    frentes de Pareto donde el rendimiento en entrenamiento difiere del rendimiento en test.

### Algoritmo Principal

El cálculo se basa en descomponer el espacio de objetivos en "cajas" (hyperboxes) y calcular
                    volúmenes ponderados por el ratio de rendimiento (Test / Train).

| Función | Entrada / Salida | Lógica Clave |
| --- | --- | --- |
| cross_hypervolume | Input:train_boxes, test_boxesOutput:float | Punto de entrada. Filtra soluciones dominadas en el conjunto de entrenamiento y llama across_hypervolume_on_front. |
| cross_hypervolume_on_front | Input:train_boxes, test_boxesOutput:float | Calcula el CHV.Calculavolume_ratios: Volumen de la caja de test dividido por
                                        volumen de la caja de train.Integra las contribuciones dimensionales usandoKahanSummerpara
                                        precisión. |
| dimension_contribution | Input:hyperboxes, ratios, d | Calcula la contribución al hipervolumen a lo largo de una dimensióndespecífica, proyectando las cajas y calculando integrales sobre intervalos disjuntos. |
| hypervolume | Input:hyperboxesOutput:float | Cálculo estándar de hipervolumen (sin componente "cross"). Útil como línea base o para
                                optimización de un solo conjunto. |

## cross_hypervolume_test.py

Suite de pruebas unitarias para validar la corrección matemática de las funciones de hipervolumen.

### Casos de Prueba Verificados

- Hipervolumen de conjuntos vacíos (debe ser 0.0).
- Hipervolumen de una caja unitaria [0, 1] (debe ser 1.0).
- Cross Hypervolume: Caso identidad (Train=Box1, Test=Box1) -> 1.0. Caso reducción (Train=Box1, Test=HalfBox) -> 0.5. Caso expansión (Train=HalfBox, Test=Box1) -> 1.0 (limitado por la lógica de proyección).

## distribution.py

Define la clase abstractaDistributiony sus implementaciones concretas. Modela una
                    secuencia de probabilidades no negativas que suman 1.0, esencial para la selección estocástica en
                    algoritmos evolutivos.

### Clases Definidas

| Clase | Métodos Clave | Descripción Técnica |
| --- | --- | --- |
| Distribution | extract(),cumulative() | Clase base. Proporciona métodos para extraer un índice aleatorio basado en las
                                probabilidades (usando suma acumulativa). |
| CachedDistribution | extract()(Binary Search) | Decorador que cachea las sumas acumulativas para acelerar la extracción aleatoria usandoBúsqueda Binaria($O(\log n)$) en lugar de lineal ($O(n)$). |
| ConcreteDistribution | __init__ | Implementación básica que normaliza cualquier secuencia de números para que sumen 1.0. |

## uniform_distribution.py

Implementación eficiente en memoria de una distribución uniforme (donde $P(i) = 1/N$).

En lugar de almacenar un array de $N$ floats iguales, simplemente almacena el tamaño $N$ y calcula el
                    valor al vuelo, ahorrando $O(N)$ de memoria.

## average_distribution.py

Crea una distribución que es el promedio aritmético de una secuencia de otras distribuciones. Útil
                    para ensembles o mezclas de poblaciones.

## hyperbox.py

Biblioteca de geometría computacional para definirHipercajas (Hyperboxes)n-dimensionales. Es la base estructural para el cálculo del algoritmoCross
                        Hypervolume.

### Jerarquía de Clases

- Hyperbox (ABC): Define operaciones geométricas genéricas (intersección,
                        volumen, proyección).
- Interval (ABC): Caso especial de Hipercaja de 1 dimensión.
- Hyperbox0B / Interval0B: Variantes optimizadas donde el límite inferior es
                        siempre 0.0 (común en métricas de rendimiento que van de 0 a 1).

### Funcionalidad Clave

| Método | Descripción |
| --- | --- |
| dominates | Determina si una caja domina a otra (es mayor o igual en todas las dimensiones y
                                estrictamente mayor en al menos una). Clave para optimización multi-objetivo. |
| project(d) | Proyecta la hipercaja en un subespacio ortogonal a la dimensión $d$ (elimina una
                                dimensión). Usado en la integración recursiva del hipervolumen. |
| volume | Calcula el producto de las longitudes de todos los intervalos. |

## mapper.py

Abstracción para paralelismo. Define la interfazMapperpara aplicar funciones a
                    iterables, permitiendo implementaciones secuenciales o paralelas (multiprocessing).

## grid.py

Funciones helper simples para conversión entre índices lineales (1D) y coordenadas de rejilla
                    (2D/Matriz).

- row_col_by_index : Convierte $i \to (row, col)$.

## input_data.py

#### 📋 Ficha Técnica

- Rol: Contenedor inmutable de Vistas (X) y Outcomes (Y).
- Uso: Se instancia una vez y se pasa a todos los workers (solo lectura).
- Validación: Asegura alineación de muestras al iniciarse.

Define la claseInputData, el contenedor principal que encapsula todo el estado de los datos de un experimento.

### Clase: InputData

| Método | Descripción |
| --- | --- |
| collapsed_views | Concatena horizontalmente todas las vistas en un único DataFrame grande (Early Integration). |
| standardize_features | Aplica estandarización Z-score a cada columna de cada vista. |

## outcome.py

Modelado de la variable objetivo (Target). Soporta tanto clasificación categórica (ej. Subtipos de
                    Cáncer) como análisis de supervivencia.

### Tipos de Outcome

- CategoricalOutcome: Para problemas de clasificación estándar. Calcula
                        automáticamente las etiquetas de clase.
- SurvivalOutcome: Para datos de tiempo al evento (Time-to-event).

## views.py

Abstracción para manejar conjuntos de datos multi-vista (Multi-View Data). Permite tratar múltiples
                    fuentes de datos (ej. mRNA, Metilación) como una entidad coherente.

### Clases

| Clase | Propósito |
| --- | --- |
| Views (ABC) | Interfaz base. Define el contratoview(key)ycollapsed(). |
| JustViews | Implementación simple basada en un diccionario de DataFrames. |
| CachedViews | Decorador que almacena en memoria la versión colapsada (concatenada) de las vistas para
                                evitar recomputarla repetidamente durante el entrenamiento. |

## preprocess_views.py

Script de limpieza de tipos de datos. Asegura que todas las columnas numéricas en las vistas sean de
                    tipofloatpara evitar errores en cálculos matemáticos posteriores (como ennumbaonumpy).

## input_creator.py

Clase base abstracta que define elPipeline de Creación de Datos.

### Patrón Template Method

El métodocreate()define el esqueleto del algoritmo:

- Llama a inner_create() (abstracto, implementado por subclases) para cargar los
                        datos crudos.
- Ejecuta pca2d() automáticamente para generar gráficos de control de calidad (QC) y
                        detectar outliers visualmente.
- Retorna el objeto InputData listo.

### Métodos Auxiliares

- _common_preprocessing : Orquesta la limpieza de tipos, el filtrado de
                        características univariante (eliminar genes con varianza 0) y la generación de gráficos de
                        densidad.

## brca_input_creator.py

Implementación concreta para el dataset deCáncer de Mama (BRCA).

### Lógica de Carga

- Vistas: Carga las ómicas solicitadas desde ./brca/input/ .
- Outcomes (Variables Objetivo): Pam50: Clasificación molecular (LumA, LumB, Basal, Her2, Normal). Survival: Calcula el tiempo de supervivencia tomando el
                                máximo absoluto entre days_to_death y days_to_last_followup .
- Estratificación: Define Pam50 como la variable para estratificar
                        los folds de validación cruzada.

## luad_lusc_input_creator.py

Implementación concreta para el dataset deCáncer de Pulmón (LUAD + LUSC).

### Lógica de Carga

- Fuente: Directorio ./luad_lusc/input/ .
- Outcome: Utiliza la columna expression_subtype cargada desde el
                        fichero de outcomes para crear un objeto CategoricalOutcome .

## fitness.py

Define la claseFitness, que mide la calidad de una solución. Está inspirada en el
                    frameworkDEAP, pero con modificaciones clave para flexibilidad en tiempo de
                    ejecución.

### Diferencias con DEAP

### Funcionalidad Clave

| Método / Propiedad | Descripción |
| --- | --- |
| weights | Tupla de flotantes. Positivo indica maximización, negativo minimización. Multiplica a
                                los valores crudos (`values`) para obtener `wvalues`. |
| dominates(other) | Implementación del concepto deDominancia de Pareto: RetornaTruesi esta solución es igual o mejor en todos los objetivos y
                                estrictamente mejor en al menos uno. |
| valid | Propiedad booleana que indica si la solución ya ha sido evaluada. |

#### 🧩 Concepto: El Individuo

En MONOMER, un "Individuo" no es solo una solución, es una entidad compleja que debe gestionar:

- Genotipo: Qué genes están activos (Bitlist).
- Fenotipo: El modelo predictivo resultante y sus métricas.
- Contexto Social: Su relación con otros individuos (Crowding, Peculiarity).

Por eficiencia, distinguimos entre implementacionesDense(listas normales) ySparse(conjuntos de índices), siendo esta última crítica para trabajar con >20k genes.

## Individual.py

Interfaz abstracta base para cualquier solución evolutiva.

Al heredar deListLike, cualquier individuo se comporta como una lista de booleanos (gen
                    seleccionado/no seleccionado), pero abstrae la implementación subyacente.

## Implementaciones de Individuos

Dos estrategias de memoria para almacenar el cromosoma (conjunto de genes seleccionados).

| Clase | Estructura Base | Caso de Uso Ideal |
| --- | --- | --- |
| DenseIndividual | Pythonlistestándar | Cuando el número de características seleccionadas es alto o el dataset es pequeño. |
| SparseIndividual | util.SparseBoolListBySet | Big Data Ómico:Cuando tenemos 20,000 genes pero
                                seleccionamos solo 5 o 10. Ahorra memoria y acelera operaciones de conjunto
                                (cruce/mutación) drásticamente. |

## bitlist_mutation.py

Define operadores de mutación para cromosomas binarios (bitlists).

### Estrategias

- FlipMutation : Mutación estándar. Invierte cada bit con una probabilidad
                        independiente $P = 1/L$.
- SymmetricFlipMutation : Variante que intenta mantener el número de bits activos
                        constante, invirtiendo pares de bits (uno 0->1 y otro 1->0).

## selection.py

Estrategias de selección ambiental (supervivencia) para reducir la población al tamaño original tras
                    generar la descendencia.

- ElitistSelection (Default): Simplemente trunca la población ordenada, quedándose
                        con los N mejores.
- TournamentExtraction : Selecciona supervivientes mediante torneos iterativos,
                        favoreciendo diversidad pero manteniendo presión selectiva.

## tournament.py

Selección de padres para reproducción (Mating Selection).

### Variantes

- TournamentByComparator : Torneo binario clásico. Compara dos individuos usando un
                        comparador personalizado (ej. Dominancia + Crowding Distance).
- TournamentByPosition : Asume que la población ya está ordenada globalmente y
                        simplemente compara índices (el índice menor gana). Más rápido.

## sorting_strategy.py

Clase Maestra de Configuración.Define cómo se combinan el algoritmo de ordenamiento
                    (NSGA-II/III), el torneo de selección y la selección de supervivientes.

### Configuraciones Predefinidas (Presets)

- SortingStrategyCrowd : NSGA-II estándar (usando Crowding Distance).
- SortingStrategySocial : NSGA-II modificado usando Social Space en
                        lugar de Crowding Distance.
- SortingStrategyCrowdCI / SocialCI : Variantes que añaden el Clone Index
                            (CI) para penalizar duplicados genéticos.
- SortingStrategyNsga3 : Uso del algoritmo NSGA-III para muchos objetivos.

## nsga2_with_secondary_sorting_strategy.py

Extensión modular de NSGA-II. Permite inyectar "Attribute Managers" que calculan métricas secundarias
                    antes de ordenar.

### Innovación: Social Space

La claseNsga2WithSocialSpaceinyecta:

- CrowdingDistanceManager
- PeculiarityManager
- SocialSpaceManager

Esto permite ordenar soluciones no solo por densidad en el frente de Pareto, sino por su
                    "peculiaridad" o distancia social a otras soluciones.

## sorter_with_clone_index.py

Implementa el concepto deClone Handling.

Problema:En algoritmos genéticos, muchas soluciones convergen a ser idénticas
                    (clones), reduciendo la diversidad.Solución:Este sorter agrupa clones y les asigna un "índice de clon".- Original: Clone Index 0 (Mejor rango).- 1ª Copia: Clone Index 1 (Peor rango).- 2ª Copia: Clone Index 2 (Aún peor rango).

Esto fuerza a los clones a la cola de la población, permitiendo su eliminación natural.

## nsga3.py

Implementación de NSGA-III basada en DEAP, adaptada para trabajar con la estructura dePeculiarIndividual.

Utiliza puntos de referencia (Reference Points) distribuidos uniformemente para mantener diversidad
                    en problemas con 3 o más objetivos (Many-Objective Optimization).

## pop_sorter.py

Interfaz abstracta base para cualquier algoritmo de ordenamiento poblacional.

## nsga2_with_secondary_comparator.py

Implementación base de NSGA-II que delega el criterio de desempate (dentro del mismo frente de
                    Pareto) a unComparatorexterno.

Este módulo orquesta el bucle principal. Es agnóstico al problema (Feature Selection vs Model Selection), delegando la lógica específica a laGAStrategyinyectada.

## ga_runner.py

Define la clase abstractaGARunnery la función librerun_ga, que
                    implementa el **bucle evolutivo principal**.

### El Bucle Evolutivo (run_ga)

Orquesta el ciclo de vida de la evolución:

- Inicialización: Crea la población inicial y evalúa su fitness.
- Registro: Inicializa el Logbook de DEAP y el HallOfFame .
- Generaciones (Bucle): Selección de Padres: Ejecuta el torneo. Variación: Aplica cruce (Mating) y mutación. Clone Repurposing: (Opcional) Modifica clones para mantener diversidad. Evaluación: Calcula el fitness de los nuevos descendientes. Selección de Supervivientes: Elige la población para la siguiente
                                generación usando la SortingStrategy (ej. NSGA-II).

## contextualized_ga_runner.py

PatrónWrapper / Decoratoralrededor de unGARunner.

Mientras que el GA trabaja con índices numéricos (ej. gen #45 activado), este runner intercepta los
                    resultados finales y los "contextualiza", mapeando los índices de vuelta a sus nombres reales (ej.
                    "Gen BRAC1"). Devuelve unContextualizedGAResult.

## Implementaciones de Runner

Clases concretas que configuran la estrategia genética según el tipo de problema:

| Clase | Propósito | Estrategia Usada |
| --- | --- | --- |
| FlipGARunner | Selección de Características.El problema se modela como
                                activar/desactivar genes. Usa mutación de bits (Flip). | GAStrategyBitlist |
| SelectGARunner | Optimización de Hiperparámetros.El problema es seleccionar una opción
                                de una lista (ej. Kernel SVM: Linear vs RBF). | GAStrategySelector |

## explored_features.py

Clase de análisis que rastrea elEspacio de Búsqueda Explorado.

Mantiene una máscara booleana global que representa la unión de todas las características que han
                    sido seleccionadas por al menos un individuo en cualquier generación. Útil para saber si el
                    algoritmo está explorando nuevas áreas o está estancado.

## progress_observer.py

Implementación del patrónObserverpara monitorear la ejecución del algoritmo
                    genético sin acoplar código de impresión dentro del bucle principal.

### Clases

- ProgressObserver (ABC) : Interfaz con métodos como notify_generation_end .
- SmartProgressObserver : Implementación que imprime logs solo si ha pasado cierto
                        tiempo (ej. cada 30 minutos) para no saturar la salida en ejecuciones largas.

## workers_pool_evaluator.py

El motor de paralelización del framework. Gestiona un pool de procesos de Python
                    (multiprocessing.Pool) para evaluar individuos en paralelo.

### Arquitectura de Evaluación

- Worker State: Al iniciar el pool, cada proceso trabajador recibe una copia de
                        los datos inmutables (Vistas, Outcomes) para no tener que serializarlos en cada evaluación (lo
                        cual sería muy lento).
- Work Package: El proceso principal envía paquetes ligeros que solo contienen el
                        individuo (la máscara de genes o índices) a evaluar.
- Map-Reduce: Utiliza pool.map para distribuir la carga y recolectar
                        los resultados (Fitness).

## Implementaciones de Evaluador

Adaptadores específicos para el tipo de problema a resolver:

| Clase | Contexto | Descripción |
| --- | --- | --- |
| MaskEvaluator | Feature Selection | El individuo es una máscara binaria. UsaDummyHpManagerporque no hay
                                hiperparámetros que tunear, solo genes que seleccionar. |
| SelectEvaluator | Model Selection | El individuo es una lista de índices. UsaSelectHpManagerpara mapear esos
                                índices a configuraciones de clasificadores (ej. SVM con C=1.0). |

## individual_updater.py

Clase auxiliar que actúa como puente entre la población (Lista de Individuos) y el Evaluador.

Su método principal,eval_invalid, filtra los individuos que han sido modificados (cuya
                    fitness no es válida), los envía al pool de evaluación en lote y actualiza sus valores de retorno.

## ga_strategy.py

Clase abstracta que define el comportamiento de alto nivel del algoritmo evolutivo.

### Responsabilidades

- Inyectar dependencias (Evaluador, Sorting Strategy).
- Definir la interfaz para los operadores genéticos: create_individual , mate (cruce), mutate .
- Clone Repurposing: Implementa la lógica para detectar individuos duplicados
                        (clones) y reemplazarlos por nuevos individuos aleatorios para inyectar diversidad fresca.

## ga_strategy_bitlist.py

Estrategia concreta para problemas deSelección de Características (Feature
                        Selection).

### Características

- Individuo: PeculiarIndividualSparse (Bitlist dispersa).
- Inicialización Inteligente: No crea individuos puramente aleatorios. Utiliza la
                        distribución de feature_importance (si se proporciona) para sesgar la creación
                        inicial hacia genes prometedores.
- Cruce: Implementa cx_uniform optimizado para listas dispersas.

## ga_strategy_selector.py

Estrategia concreta para problemas deSelección de Modelos/Hiperparámetros.

### Características

- Individuo: PeculiarIndividualDense (Lista de enteros). Cada entero
                        es un índice que apunta a una configuración específica.
- Operadores: Utiliza operadores estándar de enteros ( random.randint para mutación/creación).

## work_package.py

Define el objeto de transferencia de datos (DTO) mínimo que se envía desde el proceso maestro a los
                    procesos trabajadores.

Contiene únicamente elPeculiarIndividualByListlike(la máscara genética), minimizando
                    el tráfico de red/IPC.

## worker_result.py

Objeto de retorno de la evaluación de un trabajador.

### Contenido

- fit : Lista de valores flotantes (el fitness multiobjetivo).
- predictors : Lista de objetos MVPredictor entrenados (opcional, si el
                        objetivo requiere devolver el modelo final).

## worker_state.py

El "cerebro" residente en cada proceso trabajador. Mantiene en memoria una copia local de los datos
                    para realizar evaluaciones rápidas sin recarga.

### Mecanismo de Inicialización Paralela

Utiliza una variable global_state_for_processinicializada medianteparallel_init. Esto permite que el estado persista entre diferentes llamadas aevaluate()dentro del mismo proceso.

### Flujo de Evaluación (evaluate)

- Fijar Semilla: Restaura la semilla aleatoria para garantizar determinismo
                        absoluto en la evaluación (vital para comparar individuos justamente).
- Filtrado: Aplica la máscara del individuo a las vistas colapsadas (Feature
                        Selection).
- Cálculo de Objetivos: Itera sobre la lista de PersonalObjective .
                        Si el objetivo requiere un modelo (ej. SVM Accuracy), entrena y valida usando validación cruzada
                        interna.
- Retorno: Empaqueta los resultados y restaura el estado aleatorio original del
                        proceso.

## model.py

Define la interfaz base para todos los modelos de aprendizaje automático en el sistema.

### Jerarquía

- Model : Fábrica que produce predictores ( fit(x, y) -> Predictor ).
- Predictor : Objeto entrenado capaz de inferir ( predict(x) ).

## model_with_coef.py

Infraestructura para envolver modelos descikit-learn.

### Funcionalidad Clave

- SklearnModelWrapperWithFallback : Maneja casos extremos (ej. dataset vacío)
                        devolviendo un clasificador "Dummy" (frecuencia mayoritaria) para evitar que el código se rompa
                        durante la evolución genética.
- LogisticWithFallback / NBWithFallback : Implementaciones concretas para
                        Regresión Logística y Naive Bayes.

## svm.py

Implementación de Support Vector Machine (SVM).

Configuración fija: KernelRBF, clases balanceadas, estandarización de datos
                    (StandardScaler) automática mediante Pipeline.

## forest.py

Implementación de Random Forest.

Configuración: 30 estimadores, min_samples_leaf=2, clases balanceadas.

## survival_model.py

Soporte para análisis de supervivencia utilizandoModelos de Riesgos Proporcionales de
                        Cox(via libreríalifelines).

### Métricas

- score_concordance_index : Evalúa el modelo usando el índice de concordancia
                        (C-index), estándar en supervivencia.

## mask.py

Clase de utilidad para aplicar máscaras booleanas a DataFrames.

Es el mecanismo fundamental para realizarFeature Selection: transforma el cromosoma
                    binario del algoritmo genético en una operación de filtrado de columnas (slicing) en los datos
                    reales.

## masked_model.py

Decorador que envuelve cualquier clasificador (SVM, RF) y le aplica automáticamente una máscara de
                    características antes de entrenar o predecir.

Esto permite que el modelo subyacente sea agnóstico a la selección de características: siempre recibe
                    solo los datos relevantes.

## Modelos Multi-Vista

Extensiones para manejar entradas que consisten en múltiples diccionarios de vistas (ej.{'mrna': df1, 'mirna': df2}).

Actualmente implementan una estrategia deEarly Integration: colapsan todas las
                    vistas en una sola matriz antes de pasarla al modelo clásico.

## multi_objective_optimizer.py

Define la interfaz que todos los algoritmos de búsqueda deben cumplir.

### Contrato

- optimize(...) : Recibe datos y devuelve una secuencia de MultiObjectiveOptimizerResult .

### Clase Resultado (Result)

Encapsula elHall of Fame (HoF): la lista de las mejores soluciones encontradas (no
                    dominadas), listas para ser evaluadas en el conjunto de test.

## nsga_star.py

#### 📋 Ficha Técnica

- Rol: Implementación de alto nivel del algoritmo NSGA (II o III).
- Dependencias Clave: GAStrategy , SortingStrategy .
- Complejidad: Alta. Orquesta la lógica evolutiva principal.

Wrapper de alto nivel para configurar y ejecutar algoritmos de la familia NSGA (Non-dominated Sorting Genetic Algorithm).

### Funcionalidad

- Configura dinámicamente si usar NSGA-II o NSGA-III basándose en la SortingStrategy inyectada.
- Calcula características activas locales (para filtrar ruido antes de empezar).
- Ejecuta FlipGARunner y recopila las estadísticas finales.

## lasso_mo.py

Adaptación deLasso (L1-regularized Logistic Regression)para generar un frente de
                    Pareto.

### Estrategia Multi-Objetivo

Lasso es inherentemente mono-objetivo. Para generar múltiples soluciones (trade-offs), este
                    optimizador:

- Empieza con una regularización baja ($C=1.0$).
- Iterativamente reduce $C$ (aumenta la regularización) multiplicándolo por un shrink_factor (0.8).
- En cada paso, guarda la solución si tiene menos características que la anterior.

Esto produce una trayectoria de soluciones desde "muchos genes, alta precisión" hasta "pocos genes,
                    menor precisión".

## rfe_mo_optimizer.py

Adaptación deRecursive Feature Elimination (RFE).

### Estrategia

Similar a Lasso, RFE es mono-objetivo. Este optimizador:

- Entrena un modelo y calcula la importancia de características.
- Elimina las $N$ características menos importantes (Step).
- Guarda el subconjunto resultante como una solución candidata.
- Repite hasta quedarse sin características.

La colección de todos los subconjuntos intermedios forma el frente de Pareto aproximado.

## sweeping_ga_multi_objective_optimizer.py

Implementa una estrategia avanzada deBarrido (Sweeping).

Ejecuta el Algoritmo Genético en dos fases o ciclos iterativos para refinar la búsqueda, utilizandorun_ga_2_steps. Probablemente diseñado para escapar de óptimos locales o refinar
                    soluciones prometedoras.

## multi_objective_cross_evaluator.py

Interfaz base para todos los evaluadores post-optimización.

Define el métodoevaluate(input_data, folds, predictors), que recibe las soluciones
                    finales de todos los folds y realiza análisis globales.

## cross_hypervolume_cross_evaluator.py

Calcula métricas de hipervolumen para evaluar la calidad y generalización del frente de Pareto
                    encontrado.

### Métricas Calculadas

- Inner CV Hypervolume: Rendimiento estimado durante la optimización (dentro del
                        GA).
- Train Hypervolume: Rendimiento al re-evaluar las soluciones finales en todo el
                        conjunto de entrenamiento.
- Test Hypervolume: Rendimiento real en el conjunto de test (datos no vistos).
- Cross Hypervolume (CHV): La métrica propuesta que integra Train y Test para
                        penalizar soluciones que se degradan al generalizar.

## feature_stability_mo_cross_eval.py

Analiza la robustez de los biomarcadores seleccionados a través de los diferentes folds.

### Métodos de Estabilidad

- By Weights: Compara las frecuencias de selección de genes.
- By Unions: Compara el conjunto total de genes vistos en cada fold.
- By Spearman: Correlación de rango de la importancia de características.
- By Top-K: Estabilidad considerando solo los $K$ genes más frecuentes (ej. top
                        50).

## feature_variety_mo_cross_eval.py

Mide la diversidaddentrode un mismo frente de Pareto. Calcula el índice de Jaccard
                    promedio entre todas las soluciones de un fold.

Un valor bajo es bueno aquí, indicando que el algoritmo ha encontrado soluciones diversas (genes
                    distintos) para el mismo problema.

## hof_saver.py

Guarda los resultados finales en disco.

- solution_features_fold_X.csv : Matriz binaria indicando qué genes activó cada
                        solución.
- solution_fitnesses_fold_X.csv : Valores de los objetivos (Accuracy, Leanness) para
                        cada solución.

## confusion_matrices_saver.py

Genera y guarda matrices de confusión para cada solución en el frente de Pareto, permitiendo un
                    análisis detallado de errores por clase.

## two_objectives_cross_plot.py

Generador de gráficos de dispersión (Scatter Plots) para visualizar el compromiso (trade-off) entre
                    pares de objetivos.

### Funcionalidad

Para cada par de objetivos (ej. Accuracy vs. Leanness):

- Itera sobre cada fold de la validación cruzada.
- Extrae los valores de los objetivos para las soluciones en el Hall of Fame .
- Calcula los valores en tres conjuntos de datos: Train: Datos usados para entrenar. Inner CV: Estimación interna durante la optimización. Test: Rendimiento real en datos no vistos.
- Genera un gráfico PNG donde se puede visualizar el "gap de generalización" (diferencia entre
                        Train y Test).

## used_views.py

En un contexto multi-ómico, analiza qué "vistas" (ej. mRNA vs miRNA) contribuyeron más
                    características a las soluciones finales.

## objective_computer.py

Define la lógica matemática para calcular métricas de rendimiento.

### Métricas Implementadas

| Clase | Cálculo | Propósito |
| --- | --- | --- |
| Leanness | $1 / (1 + N_{features})$ | Maximizar la parsimonia. Premia modelos con menos genes. Rango (0, 1]. |
| SoftLeanness | $1 / (1 + \sqrt{N_{features}})$ | Versión suavizada de Leanness. Penaliza menos agresivamente el aumento de
                                características inicial. |
| BalancedAccuracy | Promedio del recall por clase. | Métrica robusta para clases desbalanceadas (común en cáncer). |
| MacroF1 | Promedio del F1-score por clase. | Equilibrio entre precisión y recall. |

## social_objective.py

Define la interfazSocialObjective. Un objetivo social puede depender no solo de los
                    datos, sino también del estado de otros individuos en la población.

- PersonalObjective : Subclase para objetivos tradicionales que solo dependen del
                        individuo (ej. Accuracy).

## peculiarity.py

Implementa laPeculiaridad, un objetivo dinámico diseñado para mantener la
                    diversidad genética.

Cálculo:Mide la desviación absoluta media (MAE) del genotipo de un individuo
                    respecto al "individuo promedio" de la generación actual.

Efecto:En un GA multiobjetivo, maximizar la peculiaridad empuja al algoritmo a
                    explorar soluciones genéticamente distintas, evitando la convergencia prematura a un único óptimo
                    local.

## survival_objective_computer.py

Adaptador para métricas de análisis de supervivencia.

- CIndex : Concordance Index. Mide qué tan bien el modelo ordena los tiempos de riesgo
                        de los pacientes.

## balanced_accuracy_with_deviation.py

Decorador de seguridad para la métrica de Accuracy.

Si la desviación estándar de la accuracy entre los folds de validación cruzada interna supera un
                    umbral (max_sd, por defecto 0.05), penaliza la fitness a 0.0. Esto descarta modelos
                    inestables.

## composite_personal_objective.py

Clase contenedora que asocia un cálculo matemático (ObjectiveComputer) con un modelo
                    específico (ej. "Calcular Accuracy usando SVM").

## personal_objective_with_model.py

Especialización para objetivos que requieren entrenar un modelo predictivo (a diferencia de Leanness,
                    que solo requiere contar genes).

## Social_objective_factory.py

Patrón Factory para instanciar objetivos. Necesario porque algunos objetivos sociales (como
                    Peculiarity) necesitan reinicializarse o actualizarse en cada generación.

## objective_computer.py

Define la lógica matemática para calcular métricas de rendimiento.

### Métricas Implementadas

| Clase | Cálculo | Propósito |
| --- | --- | --- |
| Leanness | $1 / (1 + N_{features})$ | Maximizar la parsimonia. Premia modelos con menos genes. Rango (0, 1]. |
| SoftLeanness | $1 / (1 + \sqrt{N_{features}})$ | Versión suavizada de Leanness. Penaliza menos agresivamente el aumento de
                                características inicial. |
| BalancedAccuracy | Promedio del recall por clase. | Métrica robusta para clases desbalanceadas (común en cáncer). |
| MacroF1 | Promedio del F1-score por clase. | Equilibrio entre precisión y recall. |

## social_objective.py

Define la interfazSocialObjective. Un objetivo social puede depender no solo de los
                    datos, sino también del estado de otros individuos en la población.

- PersonalObjective : Subclase para objetivos tradicionales que solo dependen del
                        individuo (ej. Accuracy).

## peculiarity.py

Implementa laPeculiaridad, un objetivo dinámico diseñado para mantener la
                    diversidad genética.

Cálculo:Mide la desviación absoluta media (MAE) del genotipo de un individuo
                    respecto al "individuo promedio" de la generación actual.

Efecto:En un GA multiobjetivo, maximizar la peculiaridad empuja al algoritmo a
                    explorar soluciones genéticamente distintas, evitando la convergencia prematura a un único óptimo
                    local.

## survival_objective_computer.py

Adaptador para métricas de análisis de supervivencia.

- CIndex : Concordance Index. Mide qué tan bien el modelo ordena los tiempos de riesgo
                        de los pacientes.

## balanced_accuracy_with_deviation.py

Decorador de seguridad para la métrica de Accuracy.

Si la desviación estándar de la accuracy entre los folds de validación cruzada interna supera un
                    umbral (max_sd, por defecto 0.05), penaliza la fitness a 0.0. Esto descarta modelos
                    inestables.

## composite_personal_objective.py

Clase contenedora que asocia un cálculo matemático (ObjectiveComputer) con un modelo
                    específico (ej. "Calcular Accuracy usando SVM").

## personal_objective_with_model.py

Especialización para objetivos que requieren entrenar un modelo predictivo (a diferencia de Leanness,
                    que solo requiere contar genes).

## Social_objective_factory.py

Patrón Factory para instanciar objetivos. Necesario porque algunos objetivos sociales (como
                    Peculiarity) necesitan reinicializarse o actualizarse en cada generación.

## hyperparam_manager.py

Define la interfaz para traducir unIndividuo(genotipo) a unaMáscara de
                        Características(fenotipo).

### Propósito

El algoritmo genético trabaja con abstracciones numéricas (listas de bits o enteros). Sin embargo,
                    los evaluadores necesitan saber qué columnas del DataFrame activar. Esta clase hace esa conversión.

### Métodos Clave

- active_features_mask(hyperparams) : Devuelve la máscara booleana lista para filtrar
                        datos.
- to_tuple(hyperparams) : Convierte la configuración en una tupla hashable. Esencial
                        para detectar Clones (individuos duplicados) y aplicar el Clone
                            Repurposing .

## dummy_hp_manager.py

Implementación de Identidad. Se usa paraFeature Selectiondirecto.

Lógica:Si el individuo es `[1, 0, 1]`, la máscara resultante es `[True, False,
                    True]`. No hay transformación intermedia; el cromosoma *es* la selección.

## select_hp_manager.py

Implementación de Indirección. Se usa paraOptimización de Hiperparámetroso
                    selección de bloques.

### Lógica

El individuo es una lista de índices enteros, ej:[2, 5].

- El índice 0 del individuo (valor 2) mira en la "Población de la Vista 0" y selecciona la
                        configuración #2.
- El índice 1 del individuo (valor 5) mira en la "Población de la Vista 1" y selecciona la
                        configuración #5.

Finalmente, concatena las máscaras seleccionadas de cada vista en una sola máscara global. Esto
                    permite al GA mezclar y combinar configuraciones pre-calculadas de diferentes fuentes ómicas.

`HallOfFame`
## Infraestructura Base del Hall of Fame

### Conceptos Clave

- PopulationObserver: Interfaz para objetos que reciben actualizaciones de la
                        población en cada generación. Permite monitoreo pasivo.
- HallOfFame (HoF): Almacén persistente de los mejores individuos encontrados
                        durante toda la ejecución (no solo la última generación). Realiza copias profundas (deepcopy)
                        para evitar modificaciones accidentales.
- Hofers: Un contenedor inmutable (snapshot) que se devuelve al final de la
                        ejecución. Es lo que reciben los evaluadores y "savers".

## pareto_front.py

Implementación del Hall of Fame paraOptimización Multi-Objetivo.

### Lógica de Actualización

Cada vez que se intenta añadir un nuevo individuo:

- Si el nuevo individuo es dominado por alguno ya existente en el frente, se descarta.
- Si el nuevo individuo domina a algunos existentes, estos se eliminan y el nuevo entra.
- Si es no-dominado respecto a todos, coexiste con ellos.

Garantiza que al final solo tengamos el conjunto de soluciones óptimas de compromiso.

## Hall of Fame por Comparador (Single Objective)

Variantes para optimización mono-objetivo o criterios simples.

- HallOfFameByComparator : Mantiene una lista ordenada de los N mejores individuos
                        según un criterio arbitrario.
- HofBySum : Caso concreto que guarda los individuos con la suma más alta (útil para
                        debug o métricas simples).

## population_observer_factory.py

PatrónFactorypara instanciar observadores.

Permite que el optimizador (`NsgaStar`) cree nuevas instancias limpias del Hall of Fame para cada
                    fold de la validación cruzada sin acoplarse a la clase concreta.

## folds_creator.py

Interfaz abstracta base para cualquier generador de pliegues (folds).

Define el contratocreate_folds(x, y, seed), que debe devolver una lista de tuplas(train_indices, test_indices).

## input_data_folds_creator.py

Especialización de la interfaz para trabajar con objetos complejosInputData.

Permite acceder a la lógica de negocio (ej. "¿Cuál es la variable de estratificación definida para
                    este cáncer?") antes de generar los pliegues.

## k_folds_creator.py

Implementación estándar deK-Fold Cross Validation Estratificadousandosklearn.model_selection.StratifiedKFold.

## input_data_k_folds_creator.py

La implementación por defecto del sistema.

Extrae automáticamente los datos de la columna objetivo definida eninput_data.stratify_outcome_data()y genera K folds estratificados sobre ella. Esto
                    garantiza que todos los folds tengan la misma proporción de subtipos de cáncer o eventos de
                    supervivencia.

## split_folds_creator.py

Generador de un único pliegue (Hold-out) 50/50. Útil para pruebas rápidas o validaciones muy
                    específicas donde no se requiere validación cruzada completa.

## run_one_external_validation.py

Script de orquestación para experimentos deValidación Externa.

### Flujo de Trabajo

- Carga de Datos: Carga dataset interno (entrenamiento) y externo (prueba).
- Armonización: Reduce ambos datasets a las características comunes (intersección
                        de genes) y estandariza cada uno por separado para evitar data leakage .
- Entrenamiento: Ejecuta do_final_optimization sobre el dataset
                        interno completo para obtener el Frente de Pareto de modelos.
- Validación: Evalúa esos modelos sobre el dataset externo usando los evaluadores
                        definidos en mo_external_evaluator .

## mo_external_evaluator.py

Interfaz base para los evaluadores externos.

Similar aCrossEvaluator, pero recibe explícitamente dos datasets:input_data(donde se entrenó) yexternal_data(donde se valida).

## two_objectives_external_plot.py

Genera gráficos de dispersión comparando el rendimiento interno vs. externo.

Permite visualizar visualmente si los modelos que funcionaban bien en el entrenamiento generalizan
                    bien al dataset externo o si sufren una caída drástica de rendimiento (overfitting).

## hof_saver.py (External)

Guarda los resultados de la validación externa en disco, incluyendo las características seleccionadas
                    y los valores de fitness en ambos datasets.

## external_confusion_matrices_saver.py

Calcula y guarda matrices de confusión utilizando las predicciones sobre el dataset externo.

## feature_importance.py

Interfaz abstracta base.

Define el métodocompute(x, y)que debe devolver unaDistribution(probabilidades normalizadas que suman 1.0), indicando la relevancia relativa de cada columna enx.

## feature_importance_by_lasso.py

Calcula la importancia basada en los coeficientes de unaRegresión Logística con penalización
                        L1 (Lasso).

Para problemas multiclase, colapsa la matriz de coeficientes (Clases x Genes) sumando los valores
                    absolutos por columna.

## feature_importance_anova.py

Calcula la importancia estadística univariante usando el testANOVA F-value.

Convierte los p-valores resultantes en probabilidades usando la corrección de Benjamini-Hochberg
                    (FDR) y luego invirtiendo la escala (1.0 - FDR), dando más peso a los genes más significativos.

## feature_importance_average.py

Estrategia de ensamble (Ensemble).

Permite combinar múltiples métodos de importancia (ej. Lasso + ANOVA) promediando sus distribuciones
                    resultantes. Útil para obtener una estimación más robusta.

## feature_importance_by_fold.py

Permite variar la importancia de características dinámicamente según el fold de validación cruzada.

DestacaFeatureImportanceByPrevious, que carga los resultados de una ejecución anterior
                    del optimizador y usa la frecuencia de selección de genes en el pasado como la importancia para la
                    nueva ejecución (Guided Forward Search).

## feature_importance_by_cox.py

Intento experimental de usar coeficientes del Modelo de Cox para datos de supervivencia.

## feature_importance_uniform.py

Implementación base (Baseline). Asigna la misma probabilidad ($1/N$) a todos los genes. Equivale a
                    una inicialización puramente aleatoria del algoritmo genético.

## feature_importance_by_univariate_cox.py

Cálculo de importancia paraSupervivencia. Evalúa cada gen individualmente
                    entrenando un modelo de Cox simple y midiendo su C-Index mediante validación cruzada de 2 pliegues.

Paralelización:Dado que calcular esto para 20.000 genes es costoso, utilizaProcessPoolExecutorpara distribuir el trabajo en todos los núcleos disponibles.

## soft_lasso.py

Estrategia híbrida:Promedio(Uniforme, Lasso).

Motivación:Lasso es muy agresivo seleccionando características (Sparse). Si usamos
                    solo Lasso para inicializar el GA, la diversidad genética inicial sería muy baja. SoftLasso
                    "suaviza" esta distribución, dando una oportunidad justa a los genes descartados por Lasso pero
                    manteniendo el sesgo hacia los prometedores.

## multi_view_feature_importance.py

Orquestador para datasets Multi-Vista. Aplica el algoritmo de importancia seleccionado (ej. ANOVA) a
                    cada vista (mRNA, miRNA, etc.) independientemente y devuelve una lista de distribuciones.

## multi_outcome_feature_importance.py

Manejador para problemas Multi-Objetivo complejos (ej. Clasificación + Supervivencia simultánea).

Calcula la importancia para cada objetivo por separado (usando algoritmos distintos si es necesario,
                    ej. ANOVA para clase y Cox para supervivencia) y combina los resultados en una distribución promedio
                    ponderada.

## mv_feature_importance_by_previous.py

Implementación concreta para la estrategiaGuided Forward. Carga los conteos de uso
                    de genes de una ejecución previa (guardados en disco) y los convierte en una distribución de
                    probabilidad.

## parallel_anova.py

Implementación paralela del test estadísticoANOVA (Analysis of Variance).

Funcionalidad:Para cada gen, calcula si existe una diferencia estadísticamente
                    significativa en su expresión media entre las diferentes clases (ej. Subtipos de Cáncer). Si el
                    p-value es mayor que un umbral (por defecto 0.05), el gen se descarta.

Optimización:UtilizaProcessPoolExecutorpara realizar miles de tests
                    F en paralelo.

## univariate_feature_selection.py

Biblioteca de utilidades para el filtrado previo de características.

### Filtros Disponibles

- filter_all_nan : Elimina columnas donde todos los valores son NaN.
- filter_zero_variance : Elimina genes que tienen el mismo valor en todas las muestras
                        (varianza 0), ya que no pueden discriminar nada.
- filter_low_variance : Elimina genes con varianza extremadamente baja (casi
                        constante), que suelen ser ruido.
- compute_active_features_sv_multi_target : Combina filtros de varianza y ANOVA para
                        múltiples variables objetivo, generando una máscara de "genes activos" que el GA usará como
                        universo de búsqueda.

## evaluation_setup.py

Clase de datos (DTO) que contiene toda la configuración de un experimento.

Define parámetros como el dataset a usar, el algoritmo (NSGA-II vs Sweeping), probabilidades de mutación, tamaño de población, etc. Actúa como la fuente de la verdad para la ejecución.

## setup_reader.py

Parser de archivos de configuración.ini.

Lee los argumentos de la línea de comandos (sys.argv) y carga los archivos de configuración solicitados, devolviendo instancias deEvaluationSetup.

## setup_to_mo_optimizer.py

La Gran Fábrica.

Toma un objetoEvaluationSetup(configuración plana) e instancia el grafo de objetos completo necesario para ejecutar el algoritmo:

- Carga los datos ( InputData ).
- Configura los objetivos (Accuracy, Leanness).
- Instancia la estrategia de ordenamiento (Social Space, Crowding Distance).
- Instancia el optimizador (NSGA-II, Lasso, RFE).

## ga_mo_optimizer_setup.py

Define perfiles de configuración predefinidos ("Small" vs "Big").

- Small: Para pruebas rápidas y debug (Población pequeña, pocas generaciones).
- Big: Para ejecuciones de producción (Población grande, muchas generaciones).

## parse_objectives.py

Traduce cadenas de texto como"balanced_accuracy"o["accuracy", "svm"]en instancias reales dePersonalObjectivecon el modelo subyacente correcto.

## allowed_names.py

Repositorio central de constantes de cadena. Define los nombres válidos para algoritmos, modelos y métricas en los archivos de configuración, evitando errores tipográficos.

## setup_utils.py

Utilidades para la gestión de directorios de salida.

Genera rutas de guardado canónicas basadas en la configuración del experimento (ej../BRCA/mRNA/accuracy_leanness/5_folds/...) para mantener los resultados organizados automáticamente.

## parse_initial_features.py

Configura la estrategia para decidir cuántos genes se activan en la población inicial.

- Uniform : Cada individuo tiene un número de genes activo elegido al azar entre min y max.
- Binomial : Se usa una distribución binomial centrada en un promedio.

## parse_feature_importance.py

Factoría que instancia los objetos de importancia de características.

Interpreta cadenas como"anova","lasso"o rutas de directorios (paraGuided Forward) y devuelve el objetoFeatureImportancecorrespondiente configurado.

## barplot.py

Utilidad genérica para generar gráficos de barras con barras de error (desviación estándar). Usado para comparar el rendimiento promedio de diferentes algoritmos.

## best_genes_plotter.py

Genera tablas visuales (mapas de calor) que muestran losgenes más seleccionados.

Agrega los resultados de todos los folds para identificar la "firma genética" robusta: aquellos genes que el algoritmo selecciona consistentemente independientemente de la partición de datos.

## best_solutions_printer.py

Extrae y formatea en texto plano las soluciones del Frente de Pareto final. Muestra qué genes componen los mejores modelos encontrados.

## counts_over_steps.py

Genera gráficos de áreas apiladas (stacked plots) para visualizar la evolución de contadores a lo largo de las generaciones.

## default_labels_map.py

Diccionario de configuración que mapea los nombres internos de las variables (ej."bal_acc") a etiquetas legibles para la publicación (ej."Balanced Accuracy").

## explored_features_plot.py

Monitoriza la exploración del espacio de búsqueda.

Grafica el número total de características únicas (genes) que han sido visitadas por el algoritmo genético acumuladas generación tras generación.

## feature_diversity_plots.py

Visualiza la estabilidad y diversidad de las características.

- Stability Plot: Muestra si el algoritmo converge siempre a los mismos genes o si es caótico.
- Common Features: Cuántos genes son comunes entre diferentes folds.

## folds_scatter_plots.py

Genera los gráficos de dispersión (Scatter Plots) clave para evaluar elOverfitting.

Pinta cada solución como un punto, mostrando su rendimiento en Entrenamiento (Train), Validación Interna (Inner CV) y Prueba (Test). Si los puntos de Test caen muy por debajo de los de Train, indica sobreajuste.

## generations_plot.py

Gráfico clásico de evolución de algoritmo genético.

Muestra las curvas de Min, Max y Promedio de los objetivos (Fitness) a lo largo de las generaciones para diagnosticar la convergencia.

## hof_stability_plots.py

Conjunto de gráficos para evaluar la robustez de los resultados a través de los folds.

- Jaccard/Dice Plot: Mide la superposición de genes seleccionados entre diferentes particiones de datos.
- Stability by Weights: Considera la frecuencia de aparición de cada gen.

## hof_utils.py

Capa de Acceso a Datos (DAO) para los resultados experimentales.

Contiene funciones para localizar, leer y parsear los archivos CSV generados por el optimizador (ej.solution_features_fold_0.csv), abstrayendo la estructura de directorios del resto de scripts de visualización.

## monotonic_front.py

Utilidad visual para limpiar el Frente de Pareto.

Dado un conjunto de puntos (soluciones), calcula y dibuja la envolvente monótona (el "mejor borde"), facilitando la comparación visual entre diferentes algoritmos en gráficos de dos objetivos.

## objective_pairs_plots.py

Genera matrices de gráficos de dispersión (Scatter Plots) comparando todos los pares de objetivos posibles.

Ejemplo: Si optimizas Accuracy, Leanness y Peculiarity, genera gráficos 2D para (Acc vs Leanness), (Acc vs Pec) y (Leanness vs Pec).

## pca_subplots.py

Genera visualizaciones de Análisis de Componentes Principales (PCA) de los datos de entrada.

Útil para visualizar la complejidad del dataset original y si las clases son linealmente separables antes de aplicar cualquier selección de características.

## performance_by_class.py

Desglosa el rendimiento del modelo por clases individuales.

Genera gráficos que muestran la Precisión, Recall o F1-Score específica para cada subtipo de cáncer (ej. "Basal" vs "Luminal A"), permitiendo detectar si el algoritmo sesga sus predicciones hacia clases mayoritarias.

## plot_consts.py

Define la paleta de colores y estilos globales para asegurar coherencia visual en todas las figuras del paper (ej.tab:orange,colorblindpalette).

## plot_labels.py

Diccionario de traducción.

Mapea los identificadores internos del código (ej."nsga2_chs","lasso_mo") a nombres formateados y limpios para publicación (ej."NSGA-II (Clone Repurposing)","LASSO-MO").

## plot_utils.py

Biblioteca de bajo nivel para interactuar conmatplotlibyseaborn.

Maneja la creación de figuras, guardado inteligente (creando directorios si no existen) y configuración de ejes.

## saved_hof.py

Clase envoltorio que representa unHall of Fame guardado en disco.

Abstrae la lectura de archivos CSV. Permite cargar resultados pasados (fitness, características, matrices de confusión) simplemente indicando la ruta del directorio, facilitando el análisis post-hoc sin re-ejecutar la optimización.

## saved_external_val.py

Similar aSavedHoF, pero específico para resultados de validación externa (donde no hay folds, sino un único conjunto de test externo).

## subplots.py

Utilidad genérica para crear grillas de gráficos (Grid Layout).

Calcula automáticamente cuántas filas y columnas se necesitan basándose en el número de gráficos a pintar.

## subplots_by_strategy.py

Crea matrices de gráficos organizados por estrategia algorítmica.

Permite visualizar, por ejemplo, una grilla donde cada celda compara NSGA-II vs LASSO para un dataset diferente, o diferentes métricas para el mismo dataset.

## subplots_runner.py

Script Ejecutable.Genera los grandes gráficos comparativos del paper.

Recorre todos los datasets (BRCA, LUAD, etc.) y todas las validaciones externas, generando gráficos de dispersión (Scatter Plots) y de compromiso (Trade-off Plots) para cada combinación.

## summary_statistics_plotter.py

Calcula y grafica estadísticas globales agregadas.

Genera los gráficos de barras que comparan métricas comoHypervolumen,Índice de Jaccard (Estabilidad)yDiceentre todos los algoritmos probados, sirviendo como resumen final del rendimiento.

## solution_utils.py

Ayudantes para extraer listas planas de soluciones a partir de las estructuras jerárquicas de directorios de resultados.

## table_plot.py

Renderiza DataFrames de pandas como imágenes PNG (tablas visuales).

Útil para incluir tablas de resultados numéricos directamente en los informes visuales generados automáticamente.

## show_views.py

Genera diagnósticos visuales de los datos de entrada en crudo:

- Boxplots: Para ver la distribución de expresión de los primeros genes/muestras.
- Histogramas: Para ver la distribución global de valores y detectar necesidad de normalización.

## automated_hofs_archive.py

Utilidad para la localización automática de resultados.

En lugar de definir manualmente la ruta de cada archivo CSV, este script genera las rutas basándose en convenciones de nombres (Dataset -> Algoritmo -> Modelo Interno), permitiendo cargar todos los resultados de un experimento complejo con una sola llamada.

## shallow_saved_hofs_archive_cv.py

Repositorio de configuraciones paraValidación Cruzada.

Contiene listas predefinidas de objetosSavedHoFque apuntan a los resultados más relevantes de los experimentos internos (ej.TCGA_BRCA_500), listos para ser pasados a los generadores de gráficas.

## shallow_saved_hofs_archive_external.py

Repositorio de configuraciones paraValidación Externa.

Define pares de (Entrenamiento, Validación) que se han ejecutado, como por ejemplo entrenar en TCGA-BRCA y validar en el dataset sueco (Swedish), para generar las comparativas de generalización.

## hofs_plotter.py

Interfaz abstracta para estrategias de dibujado.

Define el contratoplot(ax, saved_hofs), que recibe un eje de matplotlib y una lista de resultados guardados, y debe "pintar" algo sobre ese eje.

## plot_setup.py

Objeto de configuración (DTO) para los gráficos.

Centraliza parámetros visuales como límites de ejes (x_min, x_max), transparencia (alpha), tamaño de fuente y mapas de traducción de etiquetas, asegurando que todos los subgráficos de una figura compuesta tengan el mismo estilo.

## hofs_scatterplotter.py

Estrategia para dibujarGráficos de Dispersión (Scatter Plots).

Toma dos columnas de objetivos (ej. columna 1="Nº Características", columna 0="Balanced Accuracy") y pinta cada solución del Hall of Fame como un punto en el espacio 2D.

## hofs_best_trade_plotter.py

Estrategia para dibujarFrentes de Pareto (Trade-off Curves).

En lugar de pintar todos los puntos, dibuja la línea que conecta las mejores soluciones no dominadas, permitiendo visualizar limpiamente la frontera de eficiencia de cada algoritmo.

## hofs_measure_plotter.py

Estrategia para dibujarGráficos de Barrasde métricas agregadas.

Utiliza una instancia deRunMeasure(comoRunCrossHypervolume) para calcular un valor escalar para cada algoritmo y lo representa como una barra con desviación estándar.

## plotter.py

Interfaz abstracta básica para cualquier objeto capaz de dibujar en un eje de Matplotlib.

Contrato simple:plot(ax, color=None).

## gene_boxplotter.py

Dibuja diagramas de caja (Boxplots) de la expresión de genes específicos.

Funcionalidad:Toma un conjunto de nombres de genes, extrae sus datos de expresión (mRNA), los estandariza (Z-score) y genera un gráfico comparativo agrupado por subtipo de cáncer. Útil para verificar visualmente si un biomarcador encontrado realmente discrimina entre clases.

## pca_plotter.py

Dibuja el gráfico de Análisis de Componentes Principales (PCA) 2D.

Proyecta los datos de alta dimensionalidad en los dos primeros componentes principales y colorea los puntos según su clase real. Sirve para visualizar la separabilidad intrínseca del dataset.

## performance_by_class_plotter.py

Dibuja la evolución del rendimiento (Precision, Recall, Balanced Accuracy) desglosado por clase.

Muestra cómo varía la calidad de la predicción para cada subtipo específico a medida que cambia el número de características seleccionadas en el Frente de Pareto.

## cattelani2023_utils.py

Configuración Global del Paper.

Define las constantes específicas para reproducir el estudio, como:

- Rutas de directorios donde están los resultados guardados.
- Listas de algoritmos a comparar (excluyendo variantes descartadas como NSGA-III).
- Límites visuales fijos para los ejes de los gráficos (ej. Accuracy siempre de 0.5 a 1.0) para asegurar que todas las figuras sean comparables.

## best_biomarkers_table_plotter.py

Genera la tabla de los mejores biomarcadores encontrados. Escanea las soluciones en el Frente de Pareto y extrae los genes que logran el mejor compromiso entre precisión y simplicidad para Cáncer de Mama, Riñón, Pulmón y Ovario.

## cattelani2023_gene_boxplots.py

Validación biológica visual. Genera boxplots para genes específicos mencionados en el texto del artículo (ej.BIRC5, ESR1), demostrando visualmente su capacidad para separar los subtipos de cáncer en los datasets utilizados.

## subplots_runner_alltogether.py

Script maestro para generar la mayoría de las figuras de resultados.

Recorre todos los datasets del estudio (internos y validación externa) y genera matrices de gráficos de dispersión (Scatter Plots) comparando el algoritmo propuesto (NSGA-II) contra los métodos base (Lasso, RFE).

## subplots_for_inner_model.py

Variante del script anterior que desglosa los resultados según el clasificador interno utilizado (SVM vs Random Forest vs Naive Bayes), probablemente para el material suplementario.

## performance_by_class_master_subplots.py

Genera gráficos detallados de rendimiento por clase (Subtipo de Cáncer).

En lugar de una precisión global, muestra cómo de bien se detecta cada subtipo individualmente, ayudando a identificar si algún algoritmo falla en las clases minoritarias.

## performance_by_class_subplots.py

Genera sub-paneles específicos para el análisis por clase, organizados por dataset y modelo.

## cattelani2023_pca_subplots.py

Genera la Figura de PCA (Análisis de Componentes Principales) para los 8 datasets clave del estudio (BRCA, Kidney, Lung, Ovary, tanto internos como externos).

## summary_statistics_subplotter.py

Genera las figuras de barras resumen.

Compara métricas globales comoHypervolumen(calidad del frente de Pareto) yJaccard(estabilidad) entre todos los algoritmos probados.

## hv_variety_subplotter.py

Script especializado que genera una figura compuesta relacionando el rendimiento (Hypervolume) con la diversidad de soluciones encontradas.

## saved_solution.py

Clase fundamental que representa unaSolución Recuperadadel disco.

Reconstruye un objeto utilizable a partir de datos fragmentados:

- Fitnesses: Valores de los objetivos en entrenamiento y test.
- Features: La lista de genes seleccionados.
- Confusion Matrix: La matriz guardada (si existe) para calcular métricas detalladas a posteriori.

Incluye utilidades comounion_of_featurespara analizar qué genes aparecen en un conjunto de soluciones.

## solution_from_algorithm.py

Clase contenedora (Wrapper) que asocia unaSavedSolutioncon el nombre del algoritmo que la generó (ej. "NSGA-II" vs "Lasso").

Es vital para generar gráficos comparativos donde necesitamos saber quién produjo qué punto en el frente de Pareto.

## solutions_from_files.py

El Cargador (Loader).

Contiene la lógica "sucia" de I/O. Lee coordinadamente los múltiples archivos CSV de un directorio de resultados (fitness de test, fitness de train, características, matrices de confusión) y los ensambla en una lista de objetosSavedSolutioncoherentes.

## run_test_hypervolume.py

Calcula elHipervolumendel frente de Pareto de test. Es una métrica estándar para medir la calidad de un conjunto de soluciones multiobjetivo (cuanto mayor volumen, mejor compromiso entre objetivos).

## run_soft_cross_hypervolume.py

Calcula una variante robusta del hipervolumen ("Soft Cross Hypervolume").

Utiliza "cajas difusas" (soft hyperboxes) basadas en la desviación estándar o márgenes de error, proporcionando una evaluación más realista de la generalización del frente de Pareto cuando hay incertidumbre estadística.

## run_weight_overlap.py

Métrica de estabilidad basada en pesos.

Calcula cuánto se solapan las características seleccionadas entre diferentes ejecuciones o folds, ponderando por la frecuencia de aparición. Útil para determinar si el algoritmo está convergiendo a biomarcadores robustos o si elige genes al azar.

## postprocessing.py

Infraestructura para la generación automática de informes post-ejecución.

### Concepto

Define la clase abstractaPostprocessingy una lista estándar de tareas (POSTPROCESSING_ARCHIVE) que se ejecutan al finalizar un experimento. Estas tareas incluyen:

- GenerationsPlotsPostprocessing : Curvas de convergencia.
- ExploredFeaturesPlotsPostprocessing : Análisis de exploración del espacio de búsqueda.
- FeatureDiversityPlotsPostprocessing : Gráficos de diversidad genética.
- HofStabilityPlotsPostprocessing : Análisis de estabilidad de los Hall of Fames.
- SingleFrontPlotEveryHofPostprocessing : Dibujado de frentes de Pareto.

## external_postprocessing.py

Tareas de post-procesamiento específicas paraValidación Externa.

Al validar con datos externos, no tenemos generaciones (el modelo ya está entrenado), por lo que las gráficas de convergencia no tienen sentido. Este módulo se enfoca en métricas de rendimiento final, como el desglose de acierto por clase (PerformanceByClassPlotsExternalPostprocessing).

## confusion_matrix.py

Define la claseConfusionMatrix, una envoltura orientada a objetos sobre arrays de NumPy.

Funcionalidad:Almacena los resultados de predicción (Verdaderos Positivos, Falsos Negativos, etc.) y calcula métricas derivadas on-the-fly, como:

- Sensibilidad (Recall): Capacidad de detectar casos positivos.
- Especificidad: Capacidad de descartar casos negativos.
- Balanced Accuracy: Promedio de sensibilidad y especificidad (crucial para datos desbalanceados).

## stat_keys.py

Repositorio de constantes de cadena.

Define las claves estandarizadas para los diccionarios de estadísticas (ej."accuracy","F-score"), evitando errores tipográficos ("magic strings") en todo el código.

## stat_creator.py

Motor de cálculo estadístico exhaustivo.

A partir de vectores de predicciones y valores reales (o una matriz de confusión pre-calculada), genera un diccionario completo con decenas de métricas, incluyendo:

- F-Score, G-Score.
- Prevalencia de Falsos Positivos/Negativos.
- Valor Predictivo Negativo/Positivo.
- Cohen's Kappa.

## recursive_feature_importance.py

Infraestructura para el cálculo recursivo de importancia (RFE).

Define clases abstractas para algoritmos que necesitan recalcular la importancia de las características iterativamente a medida que se eliminan las menos relevantes. Soporta escenarios multi-objetivo (Clasificación + Supervivencia) promediando las distribuciones de importancia.

## pickability_check.py

Herramienta de diagnóstico para multiprocesamiento.

Python usapicklepara enviar objetos a otros procesos. Si un objeto contiene referencias no serializables (como lambdas o conexiones abiertas), el programa falla. Este módulo prueba si un objeto es seguro de serializar antes de enviarlo, proporcionando errores detallados si falla.

## components_transform.py

Transformaciones de vectores para análisis de estabilidad.

- HigherKComponents : Mantiene solo los $K$ valores más altos de un vector y pone el resto a cero. Usado para comparar si los algoritmos coinciden en sus "Top K" genes más importantes.

## stability_of_distributions.py

Calcula matemáticamente la estabilidad de un conjunto de distribuciones.

Utiliza la diferencia absoluta media "todos contra todos" para determinar si múltiples ejecuciones del algoritmo (o múltiples folds) han llegado a una distribución de importancia de características similar.

## cached_tuple.py

Optimización de rendimiento.

Una tupla inmutable que calcula su suma la primera vez que se pide y la guarda en caché. Útil para estructuras de datos que se leen muchas veces en el bucle principal del algoritmo genético.

## plot_results.py

Utilidades gráficas básicas.

Contiene funciones para dibujar matrices de confusión (Heatmaps) y histogramas de frecuencias. Es código de visualización de bajo nivel usado por los módulos deplots/.

## sequence_utils.py

Biblioteca de manipulación de listas e iterables.

Funciones auxiliares como:

- flatten_iterable_of_iterable : Aplana listas de listas.
- stable_uniques : Elimina duplicados manteniendo el orden original.
- binary_search_iterative : Búsqueda eficiente.

## reference.py

Clase envoltorio mutable. Permite pasar tipos inmutables (como enteros o strings) por referencia, de modo que una función pueda modificar el valor original.

## singleton.py

Metaclase para implementar el patrón Singleton. Asegura que una clase solo tenga una única instancia en todo el programa.

## recursive_feature_importance.py

Infraestructura para el cálculo recursivo de importancia (RFE).

Define clases abstractas para algoritmos que necesitan recalcular la importancia de las características iterativamente a medida que se eliminan las menos relevantes. Soporta escenarios multi-objetivo (Clasificación + Supervivencia) promediando las distribuciones de importancia.

## pickability_check.py

Herramienta de diagnóstico para multiprocesamiento.

Python usapicklepara enviar objetos a otros procesos. Si un objeto contiene referencias no serializables (como lambdas o conexiones abiertas), el programa falla. Este módulo prueba si un objeto es seguro de serializar antes de enviarlo, proporcionando errores detallados si falla.

## components_transform.py

Transformaciones de vectores para análisis de estabilidad.

- HigherKComponents : Mantiene solo los $K$ valores más altos de un vector y pone el resto a cero. Usado para comparar si los algoritmos coinciden en sus "Top K" genes más importantes.

## stability_of_distributions.py

Calcula matemáticamente la estabilidad de un conjunto de distribuciones.

Utiliza la diferencia absoluta media "todos contra todos" para determinar si múltiples ejecuciones del algoritmo (o múltiples folds) han llegado a una distribución de importancia de características similar.

## cached_tuple.py

Optimización de rendimiento.

Una tupla inmutable que calcula su suma la primera vez que se pide y la guarda en caché. Útil para estructuras de datos que se leen muchas veces en el bucle principal del algoritmo genético.

## plot_results.py

Utilidades gráficas básicas.

Contiene funciones para dibujar matrices de confusión (Heatmaps) y histogramas de frecuencias. Es código de visualización de bajo nivel usado por los módulos deplots/.

## sequence_utils.py

Biblioteca de manipulación de listas e iterables.

Funciones auxiliares como:

- flatten_iterable_of_iterable : Aplana listas de listas.
- stable_uniques : Elimina duplicados manteniendo el orden original.
- binary_search_iterative : Búsqueda eficiente.

## reference.py

Clase envoltorio mutable. Permite pasar tipos inmutables (como enteros o strings) por referencia, de modo que una función pueda modificar el valor original.

## singleton.py

Metaclase para implementar el patrón Singleton. Asegura que una clase solo tenga una única instancia en todo el programa.

## exclusive_number.py

Mecanismo de sincronización entre procesos basado en el sistema de archivos.

La claseExclusiveNumberpermite que múltiples procesos paralelos obtengan un identificador único secuencial (0, 1, 2...) sin condiciones de carrera. Funciona intentando crear archivos temporales de bloqueo (lock files). Es crucial para que los trabajadores paralelos no escriban en los mismos archivos de log o resultados.

## printer.py

Sistema de abstracción de entrada/salida.

- Printer : Interfaz base.
- OutPrinter : Escribe en la consola estándar (stdout).
- LogPrinter : Escribe en un archivo de texto, asegurando que el directorio exista.
- CompositePrinter : Patrón Composite. Permite enviar el mismo mensaje a múltiples destinos a la vez (ej. consola Y archivo).

## tagged_printer.py

Decorador para impresoras.

Añade automáticamente una etiqueta o prefijo a cada línea impresa. Útil en entornos paralelos para saber qué proceso o hilo generó un mensaje específico (ej.[Worker-1]> Iniciando cálculo...).

## default_log_and_out_printer.py

Punto de acceso global (Singleton implícito).

Proporciona una instancia compartida deLogAndOutPrinterque escribe simultáneamente en la consola y en un archivolog.txtpor defecto.

## parallel_anova.py

Implementación paralela del test estadísticoANOVA (Analysis of Variance).

Funcionalidad:Evalúa cada característica individualmente para ver si separa significativamente las clases. Si el p-value es mayor que un umbral (0.05), la característica se descarta antes de entrar al algoritmo genético.

Rendimiento:UtilizaProcessPoolExecutorpara paralelizar el cálculo de miles de tests F simultáneamente.

## univariate_feature_selection.py

Biblioteca de filtros de limpieza de datos.

### Filtros Clave

- filter_all_nan : Elimina columnas vacías.
- filter_zero_variance : Elimina genes que tienen el mismo valor en todas las muestras (no aportan información).
- filter_low_variance : Elimina genes casi constantes.
- compute_active_features_mv : Orquestador que aplica estos filtros en cascada (Varianza -> ANOVA) a un dataset multi-vista para generar la máscara inicial de "genes activos".

## input_creators_archive.py

Registro central de todos los datasets disponibles en el sistema.

Define constantes (ej.TCGA_BRCA_MRNA_MIRNA) y un diccionario maestro que asigna un nombre de dataset a su instanciaInputCreatorcorrespondiente. Es lo que permite que el archivo de configuración digadataset = "tcga_brca"y el sistema sepa qué cargar.

## class_input_creator.py

Clase base genérica para crear datasets de clasificación simple.

Automatiza la tarea rutinaria de cargar vistas ómicas y una columna de etiqueta (outcome) desde un directorio, renombrar la columna objetivo y empaquetarlo todo en un objetoInputData.

## swedish_input_creator.py

Cargador específico para el dataset de cáncer de mama sueco (Swedish).

Realiza pre-procesamiento específico:

- Corta valores negativos a 0.0.
- Elimina columnas (genes) que tienen un 70% o más de ceros (baja expresión/ruido).
- Prepara datos de supervivencia (Días y Evento).

## kir_input_creator.py

Cargador para el dataset TCGA-KIR (Kidney Renal Clear Cell Carcinoma).

Carga las vistas y la variable objetivo "PanKidney Pathology".

## prad_input_creator.py

Cargador para el dataset TCGA-PRAD (Prostate Adenocarcinoma).

## view_prefix.py

Utilidad para gestionar nombres de características en entornos Multi-Vista.

Para evitar colisiones si el mismo gen aparece en mRNA y miRNA, o para saber de dónde viene una característica seleccionada, añade prefijos numéricos (ej.0_TP53,1_TP53). Permite también eliminar estos prefijos para obtener el nombre biológico limpio.

## input_data_utils.py

Funciones auxiliares para manipular objetos de datos.

- select_outcomes_in_objectives : Filtra el dataset para mantener solo las variables objetivo (outcomes) que realmente van a ser utilizadas por los objetivos de optimización definidos, ahorrando memoria.

## sel_best_k.py

Operador de selección simple.

Selecciona loskmejores individuos de la población basándose estrictamente en un comparador dado. Se usa típicamente para elitismo o para seleccionar los padres finales.

## sel_nsga2_with_secondary.py

Variante avanzada de la selección NSGA-II.

El algoritmo estándar NSGA-II usa la "distancia de apiñamiento" (crowding distance) para desempatar soluciones en el mismo frente de Pareto. Esta implementación permite inyectar uncomparador secundario personalizado(ej. complejidad del modelo) para guiar la selección cuando hay empates en dominancia.

## var_and.py

Pipeline de variación evolutiva.

Implementa el algoritmovarAnd(Cruce Y Mutación). A diferencia de la versión estándar de DEAP, esta no borra los valores de fitness si un individuo permanece intacto, ahorrando recálculos costosos.

## symmetric_flip.py

Mutación especializada para vectores dispersos (Sparse).

En selección de características, la mayoría de los genes están "apagados" (0). Un bit-flip estándar encendería demasiados genes. Esta mutaciónsimétricaajusta las probabilidades para que la frecuencia de encendido (0->1) y apagado (1->0) esté equilibrada, manteniendo la dispersión deseada.

## mut_flip_bit.py

Mutación estándar con soporte de máscara.

Realiza un flip de bits clásico, pero acepta unaactive_mask. Esto permite restringir la mutación solo a ciertos genes pre-seleccionados (ej. por el filtrado ANOVA), asegurando que el algoritmo no pierda tiempo explorando genes irrelevantes.

## feature_counts_saver.py

Guarda la frecuencia de selección de genes.

En cada generación, cuenta cuántas veces aparece cada gen en la población. Al final, genera un CSV que permite rastrear la "carrera" de los genes y ver cuáles ganan popularidad a medida que evoluciona el algoritmo.

## logbook_saver.py

Exportador de estadísticas.

Convierte elLogbookinterno de DEAP (que rastrea min, max, promedio de fitness por generación) a formatos persistentes como CSV o DataFrames para su análisis posterior.

## pop_writer.py

Observador de progreso en tiempo real.

Imprime en el log o consola el estado actual de la población (fitness promedio, tamaño, diversidad) en puntos clave del ciclo (antes de selección, después de cruce, etc.), facilitando la depuración.

## high_best_fitness.py

Define una fitness donde"más es mejor"para todos los objetivos.

En DEAP, la dirección de la optimización se define por los pesos (weights). Esta clase fija todos los pesos a1.0, simplificando la configuración para problemas de maximización pura (ej. Maximizar Accuracy y Maximizar Simplicidad).

## peculiar_fitness.py

Una extensión de la fitness estándar para algoritmos avanzados.

Además de los objetivos principales de optimización, almacena métricas secundarias para desempatar o guiar la diversidad:

- Crowding Distance: Métrica estándar de NSGA-II para mantener la diversidad en el frente de Pareto.
- Peculiarity: Una métrica personalizada que mide cuánto se distingue este individuo del resto de la población (usada para preservar innovaciones raras).
- Social Space: Espacio ocupado en el entorno social de la población.

## num_features.py

Estrategias para decidir cuántos genes activar en la población inicial.

- UniformNumFeatures : Elige el número de genes activos uniformemente al azar entre un min y max (ej. 0 a 30).
- BinomialNumFeatures : Usa una distribución binomial centrada en un promedio. Es más realista biológicamente, favoreciendo soluciones con una complejidad media esperada.

## fit.py

Interfaz base mínima. Define cualquier objeto que posea una medida de rendimiento (fitness) en el conjunto de prueba (Test).

## predictive_individual.py

Un individuo que "sabe predecir".

Extiende la definición básica de individuo genético para incluir una lista deClasificadores entrenados(ej. el objeto SVM o Random Forest real). Esto permite usar el individuo no solo para evolucionar, sino para hacer predicciones reales sobre nuevos pacientes.

## peculiar_individual.py

El ciudadano principal de la población evolutiva.

Implementa un individuo diseñado para optimización multiobjetivo avanzada. Rastrea métricas de "singularidad" social:

- Crowding Distance: Qué tan "apiñado" está su vecindario en el frente de Pareto.
- Peculiarity: Métricas personalizadas para premiar soluciones que exploran nichos genéticos únicos.

## Implementaciones: Dense vs Sparse

Optimizaciones de memoria para el almacenamiento del genoma:

- PeculiarIndividualDense : Usa arrays de bits convencionales. Rápido para cromosomas pequeños.
- PeculiarIndividualSparse : Almacena solo los índices de los genes activos. Vital cuando se trabaja con >20,000 genes pero se seleccionan <50, ahorrando drásticamente memoria RAM.

## individual_by_listlike.py

Clase puente (Mixin) que conecta la interfaz abstracta deIndividualcon implementaciones concretas de almacenamiento tipo lista (comoBitArrayoSparseBoolList).

## individual_with_context.py

El Traductor (Genotipo -> Fenotipo).

Un individuo en sí mismo es solo una cadena de bits (0s y 1s). Esta clase envuelve al individuo junto con unHyperparamManagerpara interpretar esos bits.

Permite preguntar"¿Qué genes están activos realmente?"traduciendo la estructura interna del cromosoma (que puede ser compleja si hay múltiples vistas) a una máscara plana de características utilizable por Scikit-Learn.

## peculiar_individual_by_listlike.py

Implementación concreta intermedia.

Fusiona la lógica abstracta dePeculiarIndividualcon la capacidad de almacenamiento de lista. Es aquí donde se añaden los campos para almacenar:

- Estadísticas (Stats): Diccionario para guardar métricas arbitrarias.
- Predictores: Lista de clasificadores entrenados (uno por objetivo).

## peculiar_individual_sparse.py

Optimización crítica de memoria.

Implementa unPeculiarIndividualusando almacenamiento disperso (solo guarda los índices de los genes activos). Incluye lógica especializada dedeepcopypara clonar individuos eficientemente durante la evolución sin duplicar innecesariamente objetos inmutables.

## peculiar_individual_with_context.py

Wrapper de solo lectura para evaluación.

Combina unPeculiarIndividualcon suHyperparamManager. Actúa como un proxy: cuando se le piden los "genes activos", consulta al manager para traducir el genotipo comprimido del individuo en una máscara de características utilizable.

## secondary_sorting_strategy.py

Define la política de desempate en la selección evolutiva.

En algoritmos multiobjetivo, muchas soluciones son "incomparables" (están en el mismo frente de Pareto). Esta clase define qué criterio secundario usar para ordenarlas:

- crowding_distance_strategy : La estrategia clásica de NSGA-II. Prefiere individuos aislados para mantener diversidad.
- social_space_strategy : Una estrategia novedosa que considera la "peculiaridad" y el espacio social, premiando soluciones genéticamente únicas incluso si están en zonas densas del frente de Pareto.

## individual_attribute_manager.py

Interfaz base para calculadores de métricas poblacionales.

Define el contratocompute(individuals)que debe analizar toda la población y asignar un valor (atributo) a cada individuo (ej. su distancia a los vecinos).

## crowding_distance_manager.py

Implementación estándar de NSGA-II.

Calcula laDistancia de Apiñamiento(Crowding Distance). Mide el perímetro del cuboide formado por los vecinos más cercanos en el espacio de objetivos. Se usa para favorecer la dispersión a lo largo del frente de Pareto.

## peculiarity_manager.py

Calculadora de Singularidad Genética.

Calcula y asigna la métrica dePeculiaridad. A diferencia del Crowding Distance (que mira los objetivos/fitness), la peculiaridad mira losgenes(genotipo). Un individuo es "peculiar" si tiene una combinación de genes muy diferente a la del resto de la población, ayudando a preservar innovaciones genéticas raras.

## social_space_manager.py

Calculadora de Espacio Social.

Asigna el valor de "espacio social", una métrica compuesta utilizada en variantes avanzadas del algoritmo para equilibrar la presión de convergencia con la diversidad genotípica.

## mo_optimizer_type.py

Metadatos del Optimizador.

Define la interfazMOOptimizerTypeque identifica a un algoritmo. Proporciona su nombre, su apodo (nick) para archivos y una banderauses_inner_modelsque indica si el optimizador entrena modelos predictivos internos (como un SVM) o si solo selecciona características.

## mo_optimizer_including_feature_importance.py

Pipeline de optimización con filtrado previo.

Implementa un decorador que:

- Calcula la importancia de las características (ej. usando ANOVA o Lasso) sobre los datos de entrada.
- Pasa esta información (ranking o pesos) al optimizador interno.
- Ejecuta la optimización restringida o guiada por esa importancia.

## composite_mo_optimizer_by_fold.py

Orquestador para Validación Cruzada.

Crea un optimizador específico para cada fold. Se asegura de que la selección de características (Feature Importance) se recalcule usandosolo los datos de entrenamiento de ese fold específico, evitando la fuga de información (data leakage) desde el conjunto de validación.

## guided_forward.py

Algoritmo de búsqueda:Guided Forward Selection.

Una alternativa determinista al algoritmo genético. En lugar de evolucionar una población, construye soluciones paso a paso:

- Comienza con soluciones vacías o pequeñas.
- Añade iterativamente las características más prometedoras (según un ranking previo o resultados de optimizadores anteriores).
- Mantiene un Frente de Pareto de las mejores combinaciones encontradas durante el crecimiento.

## guided_forward_accepting_fi.py

Adaptador para Guided Forward.

Permite que el algoritmoGuidedForwardacepte una distribución de importancia de características externa (Feature Importance) para guiar su orden de búsqueda.

## ga_str_utils.py

Utilidades de nombrado.

Genera los nombres estandarizados y "nicks" para los experimentos (ej."pop500_gen100_mut0.1"). Garantiza que los nombres de carpetas y archivos de resultados sean consistentes y descriptivos de los hiperparámetros usados.

## multi_objective_optimizer.py

Interfaz base del sistema de optimización.

Define el contratooptimize(...)que toma los datos de entrada y devuelve un objetoMultiObjectiveOptimizerResultque contiene:

- Frente de Pareto: La lista de soluciones óptimas (hiperparámetros).
- Predictores: Los modelos entrenados asociados a cada solución.

## multi_objective_optimizer_accepting_feature_importance.py

Interfaz extendida para optimizadores "informados".

Define algoritmos que pueden aceptar una distribución de probabilidad inicial sobre las características (Feature Importance) para guiar o sesgar su búsqueda hacia genes prometedores.

## so_to_mo_optimizer_adapter.py

Patrón Adaptador.

Envuelve un optimizador de un solo objetivo (como Lasso o SVM-RFE) y lo hace parecer un optimizador multiobjetivo. Devuelve un "Frente de Pareto" que contiene un único punto (la solución única del algoritmo original). Esto es vital para poder usar el mismo pipeline de evaluación y gráficos comparativos para todos los métodos.

## sweeping_ga_mo_optimizer_fi.py

Configurador del Algoritmo Genético principal.

Instancia la versión más completa del optimizador: Algoritmo Genético con estrategia de barrido (sweeping), inyección de importancia de características (FI) y clonación de soluciones para validación cruzada interna.

## sweeping_strategy.py

Define la estrategia de "Barrido" de parámetros.

En lugar de una ejecución estática, el algoritmo puede realizar múltiples pasadas (sweeps) con diferentes configuraciones (ej. aumentar progresivamente el número de generaciones o cambiar la presión de selección) para asegurar la convergencia robusta.

## optimizer_utils.py

Pegamento del sistema de evaluación.

Contiene la funciónindividuals_to_hofs, que toma una población final de individuos (genotipos), crea los folds de validación interna, entrena los modelos reales y evalúa su rendimiento para generar el Hall of Fame definitivo.

## mo_optimizer_type.py

Metadatos del Optimizador.

Define la interfazMOOptimizerTypeque identifica a un algoritmo. Proporciona su nombre, su apodo (nick) para archivos y una banderauses_inner_modelsque indica si el optimizador entrena modelos predictivos internos (como un SVM) o si solo selecciona características.

## mo_optimizer_including_feature_importance.py

Pipeline de optimización con filtrado previo.

Implementa un decorador que:

- Calcula la importancia de las características (ej. usando ANOVA o Lasso) sobre los datos de entrada.
- Pasa esta información (ranking o pesos) al optimizador interno.
- Ejecuta la optimización restringida o guiada por esa importancia.

## composite_mo_optimizer_by_fold.py

Orquestador para Validación Cruzada.

Crea un optimizador específico para cada fold. Se asegura de que la selección de características (Feature Importance) se recalcule usandosolo los datos de entrenamiento de ese fold específico, evitando la fuga de información (data leakage) desde el conjunto de validación.

## guided_forward.py

Algoritmo de búsqueda:Guided Forward Selection.

Una alternativa determinista al algoritmo genético. En lugar de evolucionar una población, construye soluciones paso a paso:

- Comienza con soluciones vacías o pequeñas.
- Añade iterativamente las características más prometedoras (según un ranking previo o resultados de optimizadores anteriores).
- Mantiene un Frente de Pareto de las mejores combinaciones encontradas durante el crecimiento.

## guided_forward_accepting_fi.py

Adaptador para Guided Forward.

Permite que el algoritmoGuidedForwardacepte una distribución de importancia de características externa (Feature Importance) para guiar su orden de búsqueda.

## ga_str_utils.py

Utilidades de nombrado.

Genera los nombres estandarizados y "nicks" para los experimentos (ej."pop500_gen100_mut0.1"). Garantiza que los nombres de carpetas y archivos de resultados sean consistentes y descriptivos de los hiperparámetros usados.

## nsga_types.py

Definiciones de tipos para los algoritmos evolutivos.

Define las constantesNSGA2_TYPEyNSGA3_TYPEque actúan como identificadores de los algoritmos en el sistema, especificando que ambos son optimizadores multiobjetivo que utilizan modelos internos.

## single_objective_optimizer.py

Interfaz base para optimizadores de un solo objetivo.

Define el contratooptimize(views, y)que recibe los datos y devuelve un únicoModelo Predictivojunto con los hiperparámetros (características seleccionadas) encontrados.

## lasso_optimizer.py

Implementación de referencia basada enLasso (L1 Regularization).

Utiliza una Regresión Logística con penalización L1 para realizar simultáneamente la clasificación y la selección de características (las características irrelevantes obtienen un coeficiente cero). Se usa para comparar si el complejo algoritmo genético multiobjetivo realmente aporta valor sobre un método estándar y rápido como Lasso.

## comparators.py

Motor de ordenamiento para la selección evolutiva.

Define clases funtoras (objetos que actúan como funciones de comparación) utilizadas para ordenar los individuos de la población. Es vital para algoritmos como NSGA-II que requieren múltiples criterios de ordenación en cascada:

- Dominancia: ¿Es A objetivamente mejor que B en todo?
- Crowding Distance: Si empatan, ¿quién aporta más diversidad?
- Social Space / Peculiarity: Criterios avanzados de desempate.

## consts.py

Configuración global del sistema.

Centraliza constantes mágicas para evitar "hardcoding" disperso. Define:

- Límites de recursión (para permitir el pickling de estructuras profundas).
- Número máximo de workers paralelos.
- Convenciones de nombres para archivos de log y resultados.

## external_validator.py

Script Ejecutable (Entry Point).

Es el punto de entrada para ejecutarValidaciones Externas. Lee la configuración de los argumentos del sistema, inicializa el entorno seguro para multiprocesamiento (logs exclusivos) y lanza la evaluación de un modelo previamente entrenado sobre un dataset totalmente nuevo.

## multi_view_utils.py

Manipulación de DataFrames Multi-Vista.

Funciones críticas para fusionar y separar datos:

- collapse_views : Toma un diccionario de vistas (mRNA, miRNA, etc.) y las fusiona en un único DataFrame gigante, añadiendo prefijos a las columnas para evitar colisiones de nombres (ej. 0_TP53 vs 1_TP53 ).
- mv_select_all_sets : Divide coordinadamente todas las vistas en conjuntos de entrenamiento y test según los índices de un fold.

## load_views.py

Cargador genérico de CSVs.

Funciones de bajo nivel para leer archivos CSV y convertirlos en DataFrames de Pandas, gestionando errores básicos de existencia de archivos.

## load_omics_views.py

Cargador especializado en Biología Computacional.

Extiende la carga básica para aplicar transformaciones específicas del dominio:

- Detecta vistas de tipo ARN (mRNA, miRNA).
- Aplica automáticamente una transformación logarítmica ( log2(x + 1) ) para normalizar la escala de expresión génica, estándar en bioinformática.

## run_with_setups.py

#### 📋 Ficha Técnica

- Rol: Ejecutable principal para lanzar experimentos.
- Input: Argumentos de línea de comandos (sys.argv) o archivos .ini .
- Output: Estructura completa de carpetas de resultados.
- Estabilidad: Alta. Raramente se modifica.

El Punto de Entrada Principal (Main Entry Point).

Es el script que se invoca desde la línea de comandos para lanzar experimentos. Su flujo es:

- Inicializa el sistema de logging seguro (usando ExclusiveNumber para evitar conflictos de escritura).
- Detecta el hardware (CPUs) y configura límites de recursión.
- Lee los argumentos de entrada (setups) que definen qué datasets y algoritmos ejecutar.
- Itera sobre cada setup y lanza run_one_setup .

## run_one_setup.py

El Orquestador de Experimentos.

Gestiona el ciclo de vida completo de un experimento individual:

- Crea la estructura de carpetas para guardar resultados.
- Instancia el optimizador (ej. NSGA-II) y el evaluador cruzado.
- Lanza optimize_with_evaluation para ejecutar la validación cruzada.
- Si se solicita, ejecuta la optimización final con todos los datos.
- Genera automáticamente todos los gráficos y reportes post-hoc.

## social_space.py

Núcleo Matemático de la Diversidad.

Implementa la lógica para calcular el "Espacio Social" de los individuos, que combina:

- Crowding Distance (Fenotipo): Diversidad en objetivos (error vs features).
- Peculiarity (Genotipo): Diversidad en genes seleccionados.

Calcula coeficientes dinámicos para equilibrar ambas métricas y asigna un valor único que permite al algoritmo genético preservar soluciones raras que serían descartadas por algoritmos estándar.

## run_ga_2_steps.py

Estrategia de ejecución avanzada en dos fases.

Ejecuta una optimización jerárquica: primero utiliza un algoritmo genético ligero para pre-seleccionar características prometedoras y luego lanza un segundo algoritmo más exhaustivo (Master Runner) sobre los resultados del primero, refinando la búsqueda.

## run_ga_separated_views.py

Estrategia de ejecución por vistas aisladas.

En lugar de fusionar todos los datos ómicos (mRNA, miRNA, etc.) al principio, este script ejecuta algoritmos genéticos independientes para cada vista. Útil para analizar el poder predictivo individual de cada fuente de datos biológicos antes de intentar combinarlas.

## path_utils.py

Pequeñas utilidades para estandarizar la creación de rutas de directorios, asegurando que los nombres de carpetas de resultados (basados en los nicks de los algoritmos) sean consistentes en todo el sistema.
