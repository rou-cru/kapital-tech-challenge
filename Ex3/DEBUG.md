# Elevada latencia de red en nodo EKS

## Primera busqueda

1. Buscaria saturacion general de nodos

```bash
kubectl top nodes
```

o eventos de presion en el nodo afectado

```bash
kubectl describe node <nombre-nodo>
```

Tambien es bueno revisar a nivel de pods por si es algo mas focalizado

```bash
kubectl top pod -n <namespace-target>
```

Aunque si en lugar de un uso constante la latencia se produce por picos, en lugar de top desde kubectl seria mejor usar top desde netshoot

```bash
top -d 0.1
```

de este modo podriamos ver posibles picos de 100% cpu muy cortos que frenan procesos de red.

2. Si no hay culpable en la presion del nodo o el pod, colocaria una imagen con tools sobre algun pod afectado, si no hay una imagen custom preparada se puede usar netshoot que trae bastantes cosas utiles

```bash
kubectl debug -it <nombre-pod> --image=nicolaka/netshoot --target=<contenedor-en-pod>
```

Ya con el contenedor en el nodo, validaria latencia general a cualquier otro punto de red externo a la infraestructura para descartar problemas fuera del cluster

```bash
time curl -I google.com
```

Si da como resultado algo por debajo de 0.300s descartamos un problema externo.

3. Si no es presion del nodo y no es algo desde internet, el culpable usual es el DNS, revisaria logs de resolucion dentro del cluster

```bash
 kubectl logs deployment/coredns -n kube-system -f
```

## Pruebas adicionales

Podemos intentar encontrar la ruta del nodo hacia otro punto de la VPC y mapear el incremento de latencia entre puntos. Desde el contenedor debug se ejecutaria:

```bash
mtr -rw <IP-target>
```

Seria bueno asegurarse de si hay o no cambios de region por HA para garantizar que se mapeo todas las rutas.

En muchos casos hay bloqueos a ping(usado por mtr) por lo que tambien es util usar tcptraceroute, especialmente si se necesita una ruta hacia algun servicio de AWS y no una IP concreta

```bash
tcptraceroute s3.us-east-1.amazonaws.com 443
```

Pero si el problema es latencia entre pods se puede usar cualquiera de los 2 para apuntar a los endpoints que vemos al ejecutar

```bash
kubectl get endpoints -n <namespace-target>
```

o con los service

```bash
kubectl get service -n <namespace-target>
```


## Cuando se pone raro

Si en pruebas desde contenedor debug parece ir y venir el problema o no queda nada claro como reproducirlo puede ser util observar la salida de nstat para determinar si en realidad el origen esta fuera del cluster:

algo como

```bash
watch -dz "nstat -pz | grep TCP"
```

ejecutado en varios puntos del cluster en paralelo con las pruebas puede usarse para descartar que sea del lado del cluster y en cambio es externo ya que la capa TCP funciona(el problema es por fuera) o no(quiza si hay algo en el cluster)

Si se sabe que el problema si esta relacionado al cluster directamente y quiza a un unico nodo, pero las pruebas con kubectl o el contenedor debug no dan pista del root cause es posible que AWS intencionalmente este limitando a la instancia EC2 que sirve de nodo, para validar esto se puede usar el cli de aws

```bash
aws ec2 describe-instance-types --instance-types <tipo-instancia> --query 'InstanceTypes[*].NetworkInfo.NetworkPerformance'
```

Si en cambio el problema se ha confirmado fuera del cluster pero dentro de la VPC, podria ser justificable el uso de alguna herramienta como VPC Flow Logs enviando a bucket para contener el costo de uso, aunque es un ultimo recurso si se han acabado las ideas

```bash
aws ec2 create-flow-logs --resource-ids vpc-0123456789abcdef0 --resource-type VPC \
--traffic-type ALL --log-destination-type s3 --log-destination arn:aws:s3:::bucket-logs/prefix/
```
