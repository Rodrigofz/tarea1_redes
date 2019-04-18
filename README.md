# Tarea 1 - Redes

## Configuración previa
Según lo pedido, se pueden configurar varios parámetros en el proxy. Esto se hace editando el archivo [Config.json](./Config.json). Los parámetros configurables son los siguientes:

- cache_lifetime: Define cuanto tiempo durará una dirección en el caché. Se pueden definir meses, días, horas y minutos.
- filter: Sirve para excluir y redirigir consultas.
    - redirected: Son las consultas que se redirigirán, es un diccionario y las tuplas se agregan de la forma:

    ```{json}
    <link_consultado>:<ip_link_redirigido>
    ```

    - excluded: Es una lista y simplemente se agrega el link que se quiere excluir.

    Para ambos casos se deja un ejemplo en el mismo archivo, estos se pueden borrar sin problema.

Con estas configuraciones definidas, se puede ejecutar correr el servidor.

---

## Ejecución de la tarea

Para ejecutar la tarea se debe ejecutar el siguiente comando desde la terminal, estando en la carpeta root:

```{bash}
python3 Server.py <port> <resolver-ip>
```

- \<port> es el puerto en el que se quiere escuchar las consultas.
- \<resolver-ip> Es la ip del resolver a utilizar. Los más comunes suelen ser 1.1.1.1 de Cloudfare o 8.8.8.8 de Google.

Luego de la ejecución del comando indicado, se debería mostrar el mensaje:

```{bash}
UDP server up and listening
```

Esto significa que el proxy esta listo para recibir consultas.

---

## Logs

Los logs son guardados en el archivo [LOGS](./LOGS). Estos contienen un timestamp correspondiente a cada consulta recibida, el ip del cliente que realiza la consulta y el ip que se le respondió a este.

---

## Cache

El caché es guardado en el archivo [Cache.json](./Cache.json), es leible por seres humanos, pero no es necesario que el usuario lo vea. Cada registro se limpia cuando transcurre el tiempo indicado en la configuración.

---

## Problemas no resueltos

- El caché guarda los bits de la respuesta tal y como vienen del resolver. Esto causa que el caché este asociado a un tipo de consulta, por lo que si luego se realiza una consulta de un tipo distinto al que está guardado, retornará una respuesta incorrecta.

- Sería ideal que al redirigir no fuera necesario ingresar la ip del link al cual se redirige. Sin embargo esto no pudo ser implementado. 

- También con respecto al punto anterior, la redirección no funciona correctamente si es que el tipo de consulta no corresponde al tipo de ip que está guardado. Por ejemplo si se esta redirigiendo [www.wikipedia.com](http://www.wikipedia.com) al link IPv4 [68.183.16.8](http://www.sorry.cl), una consulta de tipo AAAA por wikipedia no se redirigirá correctamente.

---

## Ejemplos

### Consultas normales:

- Consulta de tipo A:
```{bash}
>> dig -t A www.u-cursos.cl @localhost -p 8000

; <<>> DiG 9.10.6 <<>> -t A www.u-cursos.cl @localhost -p 8000
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 52183
;; flags: qr rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;www.u-cursos.cl.		IN	A

;; ANSWER SECTION:
www.u-cursos.cl.	1058	IN	A	200.9.100.69
www.u-cursos.cl.	1058	IN	A	200.9.100.67

;; Query time: 7 msec
;; SERVER: 127.0.0.1#8000(127.0.0.1)
;; WHEN: Thu Apr 18 15:07:25 -04 2019
;; MSG SIZE  rcvd: 76

```

- Consulta de tipo AAAA:

```{bash}
>> dig -t AAAA www.u-cursos.cl @localhost -p 8000

; <<>> DiG 9.10.6 <<>> -t AAAA www.u-cursos.cl @localhost -p 8000
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 48321
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;www.u-cursos.cl.		IN	AAAA

;; AUTHORITY SECTION:
u-cursos.cl.		1199	IN	SOA	ns1.u-cursos.cl. root.u-cursos.cl. 2017111302 1200 300 2419200 1200

;; Query time: 142 msec
;; SERVER: 127.0.0.1#8000(127.0.0.1)
;; WHEN: Thu Apr 18 15:10:40 -04 2019
;; MSG SIZE  rcvd: 89
```

- Consulta de tipo MX:

```{bash}
>> dig -t MX www.u-cursos.cl @localhost -p 8000


; <<>> DiG 9.10.6 <<>> -t MX www.u-cursos.cl @localhost -p 8000
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 1239
;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;www.u-cursos.cl.		IN	MX

;; AUTHORITY SECTION:
u-cursos.cl.		1199	IN	SOA	ns1.u-cursos.cl. root.u-cursos.cl. 2017111302 1200 300 2419200 1200

;; Query time: 12 msec
;; SERVER: 127.0.0.1#8000(127.0.0.1)
;; WHEN: Thu Apr 18 15:11:07 -04 2019
;; MSG SIZE  rcvd: 89
```

- Respuesta de ucursos redirigido a [68.183.16.8](http://www.sorry.cl) en consulta tipo A. Notar que esta a pesar de mostrar un warning, retorna la ip efectivamente cambiada:

```{bash}
>> dig -t A www.ucursos.cl @localhost -p 8000

;; Warning: Message parser reports malformed message packet.

; <<>> DiG 9.10.6 <<>> -t A www.ucursos.cl @localhost -p 8000
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 47901
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;www.ucursos.cl.			IN	A

;; ANSWER SECTION:
www.ucursos.cl.		1199	IN	A	68.183.16.8

;; Query time: 60 msec
;; SERVER: 127.0.0.1#8000(127.0.0.1)
;; WHEN: Thu Apr 18 15:15:08 -04 2019
;; MSG SIZE  rcvd: 48
```
