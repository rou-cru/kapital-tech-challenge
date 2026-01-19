# Diseño de dashboard

## Diseño en Grafana

Agregaria la siguiente informacion

- grafico de percentil 99, 95 y 90 de los tiempos de latencia
- grafico de linea para el rate de error de 5 min
- grafico espejo para network IO
- grafico de linea con uso de % de cpu respecto al limite y aparecen todas las replicas
- grafico de linea con uso de % de memoria respecto al limite y aparecen todas las replicas
- contador simple de numero de replicas ready
- contador simple de numero de replicas pending
- contador simple de numero de replicas en algun estado fail

Idea para layout:

>   -----------------   -----------------   ---------------
>   | Replicas Ready|   | Replicas pending| |Replicas fail |
>   -----------------   -----------------   ----------------
>   ----------------------------  --------------------------
>   | network IO espejo        |  | latencia p99, p95, p90 |
>   ----------------------------  --------------------------
>   --------------------------------------------------------
>   |                rate de error 5min                    |
>   --------------------------------------------------------
>   ----------------------------  --------------------------
>   | % de CPU de replicas     |  | % de RAM de replicas   |
>   ----------------------------  --------------------------

En donde a simple vista el error rate mas reciente queda cerca de la latencia, replicas fail y saturacion de ram para facilitar el identificar lo critico y se agrega replicas activas, volumen de red y uso de CPU a la izquierda como data adicional para dar contexto rapido de toda la situacion. replicas pending lo agrego porque da pista sobre un posibe origen en nodo y no en el servicio, ademas de avisar si es garantia que se esta degradando el sistema al ver el numero crecer junto a los graficos empeorando.

## Alertas

### Latencia

Para las alertas considero que el percentil 90 ya es tarde, este representa el volumen de quejas que estan o estaran generandose por lo que es solo una referencia, pero llevaria una alarma de incidencia critica independiente de las otras.

El percentil 95 debe disparar una alerta, esto es ya el punto donde el servicio comienza a generar molestias y debe ser atendido de inmediato para evitar reportes de usuarios, aqui comienza la incidencia pero aun es manejable.

El percentil 99 dispara algun aviso a modo de warning, quiza no es nada grave, pero ya esta sucediendo algo y seria bueno revisar porque ha sucedido. Sin embargo, en conjunto con otros posibles warning si podria cambiar a una alerta de incidencia.

### Error rate

Superado el threshold(que seria un valor bajo) se dispara alarma, lo que sea que este pasando ya ha dañado el sistema y es probable que solo empeore si no hay intervencion. debe ser bajo para contener el volumen de quejas que se va a generar.

### Replicas

Un numero considerado alto de replicas pending debe generar una alerta como warning por si misma, pero en conjunto con latencia o rate error incrementando podria generarse una alarma de incidente por debajo de los thresholds de incidente individuales porque indica que se esta degradando el sistema y la tendencia es empeorar incluso si aun todo dice que esta "bien".

Un numero superior a 1-2 de replicas fail es una alerta de incidente por si misma, no deberia pasar un acumulamiento de replicas fallidas(1-2 podrian llegar a ser normal en algunos escenarios, seria evaluar el caso particular).

### Red

Lo coloco como data para contexto del dashboard en caso de incidente, no agregaria alarmas directamente.

### CPU y RAM

Pondria una alarma de warning para % altos de RAM usada, pero para disparar una alerta de incidente lo condicionaria a que exista al menos otro warning  porque podria solo ser signo de escalamiento lento o ser un pico y no una incidencia como tal.
