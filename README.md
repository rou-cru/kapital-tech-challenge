# MLOps Technical Challenge: Python & AWS Focus

## Decisiones generales

1. Se utilizo Devbox para simplificar el uso de herramientas y gestion de paquetes
2. Se uso Docker Compose para levantar LocalStack y realizar pruebas relacionadas al ejercicio 1
3. Se recreo un proyecto de inferencia minimalista para mantener realismo en las implementaciones solicitadas, no se espera que genuinamente pueda inferir fuera del dataset de entrenamiento.
4. Dada la indicacion de logica sobre ejecucion real, se uso LLMs para parte de la implementacion de FastAPI, particularmente con un bug que aparecio tras agregar prometheus_client y tratar de ejecutar UTs. No se uso para redacciones, diseño y tampoco se dejo implementaciones libres sin verificacion.
5. Se realizaron agregados a los requerimientos originales para tratar de lograr un diseño parecido a lo que realmente se haria para produccion, particularmente en el pipeline de GA
6. Se uso Code Rabbit para revision final previo a entrega

## Ejercicio 1: Infraestructura y Seguridad

- Se decidio usar una estructura plana para evitar un arbol de directorios mas complejo ya que no se espera que se requiera ir agregando elementos nuevos
- Se incluyo data mock de VPC para el cluster EKS asumiendo que se tendria ya la VPC donde incorporar el cluster al no ser mencionado en los requisitos
- Se agrego un generador aleatorio para cumplir el requisito de nombre unico de AWS para el S3
- No se maneja estado con backend remoto al no tener un backend para las pruebas
- Se agregaron tags generales por considerarlo una buena practica estandar, en produccion agregaria algunos especificos para FinOps
- Se agrego versionado del bucket para tener trazabilidad contra el modelo en git y la imagen de contenedor desplegada

> Nota: Se ejecuto Checkov sobre el proyecto, se agregaron notas de skip por considerar que se salian del scope y no necesariamente se requieren en produccion real

El resultado del ejercicio 1 fue probado y confirmado como funcional tanto para terraform como el script python, ambos sobre Localstack (Ex1/docker-compose.yml)

## Ejercicio 2: Automatización del Ciclo de Vida

### Implementacion de Inferencia

- Para cumplir con varios de los requisitos se implemento un script de entrenamiento por RandomForest y el clasico dataset "Iris" disponible en Kaggle, con lo que se puede generar un modelo y regenerarlo para pruebas.
- Tambien este usa el modelo para cargar en el API de inferencia, permitiendo un suite de UTs con pytest que realice asserts sobre la inferencia.
- La inferencia se ejecuta sobre una entrada del dataset, no es una inferencia real pero garantiza determinismo para las implementacion y aporta realismo del concepto.

### Imagen Docker

- Se realiza por etapas para aligerar la imagen final
- Se utiliza un usuario no root como se solicito
- Se analizo con Checkov para validar diseño seguro, se decidio ignorar CKV_DOCKER_2 por no ser un problema relevante al ya tener medidas en la implementacion del codigo
- Se cumple con el requisito de usar el modelo como guia para el tag, al no estar definido otros escenarios se asume que cambios en codigo o dockerfile tambien generan construccion pero no cambio de tag, el despliegue accidental al hacer esto se evita asumiendo que en los manifest se controla la imagen usando SHA y no el tag.
- El requisito "detectar la presencia de un archivo nuevo en una carpeta /models" se cumple de manera implicita, se utiliza un Hash del modelo confiando en que si git detecta cambios el Hash resultante cambiara y si no, resultara en el mismo ya usado anteriormente por lo que es seguro calcular el tag en cada ocasion. Por facilidad de uso se usan solo los primeros 8 digitos basandose en la premisa de lo altamente improbable que es una colision de Hash

### Pruebas y Pipeline

- Se ejecuta un suite disponible directamente en el source code imitando lo que se haria en un proyecto real, se ejecuta como primera parte del pipeline
- En el pipeline se agrego un "Smoke Test" bajo la premisa de que la construccion del Dockerfile podria alterar los resultados que ya ha confirmado el suite de pytest por lo que se valida 1 inferencia usando los mismos valores que el UT.
- Se agregaron validaciones de endpoints relacionados con el ejercicio 3, se realizo a nivel de pipeline al considerarse un requisito de IT y no de desarollo por lo que solo se requiere validar previo a liberar una nueva imagen y en algun caso podria desearse el omitirlas
- Se confirmo que la imagen construye, es etiquetada correctamente, pasa todas las pruebas pero no se empuja a un registry por simplificar el ejercicio y tampoco se agregaron validaciones extra como calidad o analisis adicional de seguridad por considerarse fuera del scope.

### Despliegue continuo

- Se asume un cluster EKS sin herramientas adicionales para GitOps o estrategias de despliegue avanzado
- Se asume que no se debe requerir intervencion manual y por tanto se descarta estrategias no nativas de K8s vanilla
- Se asume la cooperacion a nivel desarrollo para la garantia del zero downtime y se explica el riesgo que eso implica para el objetivo. Se ha implementado los endpoints mencionados en el app de inferencia.

## Ejercicio 3: Observabilidad y Debugging

- Se ha agregado la generacion de metricas al servicio de inferencia generado para el ejercicio 2 y se confirmo que se exponen
- Se realizo una descripcion de que y porque se incluiria en el dashboard junto a un layout basico para referencia. el dashboard se penso con Grafana como referencia.
- Se asume que la salida de las alertas es funcional y adecuada, tambien se asume que es posible algun grado de logica para inhibicion y agrupacion de los triggers de alarma
- Dada las buenas practicas de no permitir root, manipulacion de filesystem y demas en los pods, ademas de las restricciones de EKS para el acceso de nodos y demas, se describe un debugging pensando en identificar si se tiene origen a nivel network interno o externo al cluster como medio principal del debugging siendo un proceso de descarte/evidencia sugerente el determinar si en realidad es Python el origen
- Se asume que existe acceso a nicolaka/netshoot o una imagen equivalente para debug en pods
- Se asume que hay permisos para awscli y se omite intencionalmente el uso de consola basado en la pregunta "que comandos Linux"
- Se omite al proposito el uso de herramientas que generarian costo adicional como VPC Reachability Analyzer
- Se asume que no es factible modificar Security Groups y restricciones de seguridad como parte del debugging
