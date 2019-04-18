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

## Aquí termina el readme serio

---
![Hola](https://i.imgflip.com/2uxv5c.png)