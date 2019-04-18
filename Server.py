import socket
import sys
import binascii
import datetime
import json
import threading
import time


months = 0;
days = 0; 
hours = 0;
minutes = 1;

def extractHeaderDomainOther(message):
    message = bytesToArray(message)
    end_of_string = find_zero(message[12:]) #encuentra indice donde termina la consulta
        
    header = message[:12]
    domain = reconstruct(message[12:end_of_string+12])
    tipo = message[end_of_string+14]
    other = message[end_of_string+13:]
    
    return header,domain,tipo,other


# Toma un arreglo y devuelve el string que lo creó
def reconstruct(arr):
    i=0
    s=""
    limit = 0
    while(i<len(arr)):
        limit = arr[i]
        i = i+1 
        for j in range(i,i+limit):
            s = s + str(chr(arr[j]))
        s = s + "."
        i = i+limit
    s = s[:-1]
    return s

def bytesToArray(arr):
    bits = []
    for i in range(len(arr)):
        bits.append(arr[i])
    return bits

def extractIP(arr):
    start_index = 12+find_zero(arr[12:])+17
    ip_array = arr[start_index:start_index+4]
    s = ""
    for p in ip_array:
        s = s+str(p)+'.'
    s = s[:-1]
    return s

def sendToResolver(message, domain, ip_resolver, port=53, bufferSize=1024):
    actual_date = datetime.datetime.now().isoformat()
    resolver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    bytesToSend = message
    resolver.sendto(bytesToSend, (ip_resolver,port))
    bytesToSend = resolver.recvfrom(bufferSize)[0]
    msgFromResolver = bytesToArray(bytesToSend)

    #Agregamos al cache
    with open('Cache.json') as cache:
        data = json.load(cache)
        data[domain] = {
                'date': actual_date,
                'response': bytesToSend.hex(),

            }

    with open('Cache.json', 'w') as cache:
        json.dump(data, cache, indent=4)    
    
    print("IP:", extractIP(msgFromResolver))
    ip_response = extractIP(msgFromResolver)

    return ip_response, msgFromResolver, bytesToSend

def parsear_respuesta(msgFromResolver):
    print("Respuesta:", msgFromResolver)
    print("Header:", msgFromResolver[:12])
    limit = find_zero(msgFromResolver[12:])+1
    print("Query:", msgFromResolver[12:limit+11])
    print("QType:", msgFromResolver[limit+12:limit+12+2])
    qtype = msgFromResolver[limit+12:limit+12+2]
    print("QClass:", msgFromResolver[limit+12+2:limit+12+4])
    print("Response Name:", msgFromResolver[limit+12+4:limit+12+6])
    print("Response Type:", msgFromResolver[limit+12+6:limit+12+8])
    print("Response class:", msgFromResolver[limit+12+8:limit+12+10])
    print("TTL:", msgFromResolver[limit+12+10:limit+12+14])
    print("RDLENGTH:", msgFromResolver[limit+12+14:limit+12+16])
    rdlength = msgFromResolver[limit+12+14:limit+12+16]
    print("RDATA:", msgFromResolver[limit+12+16:limit+12+16+rdlength[1]])
    return limit+12+4, msgFromResolver[limit+12+16:limit+12+16+rdlength[1]], rdlength[1], qtype

def parsear_pregunta(msgToResolver):
    print("Pregunta:", msgToResolver)
    print("Header:", msgToResolver[:12])
    limit = find_zero(msgToResolver[12:])+1
    print("Query:", msgToResolver[12:limit+11])
    print("QType:", msgToResolver[limit+12:limit+12+2])
    print("QClass:", msgToResolver[limit+12+2:limit+12+4])
    print("Lo demas:", msgToResolver[limit+12+4:])
    

def addToLogs(clientIP, ip_response):
    logs = open('LOGS', 'a+')
    actual_date = datetime.datetime.now().isoformat()
    logs.write(actual_date + ', ' + clientIP + ', ' + ip_response + '\n')
    logs.close()
    return actual_date


"""
def valid_header(header):
    binary = bin(header)[2:]
    QR = binary[16]
    Opcode = binary[17:21]
    TC = binary[23]
    RD = binary[24]
    QDCOUNT = binary[32:48]
    print(QR,Opcode, TC, RD, QDCOUNT)
"""


def find_zero(arr):
    b = -1
    i = 0
    while(b!=0):
        i=i+1
        b = arr[i]
    return i

def cache_clean():
    with open('Cache.json') as cache:
        data = json.load(cache)
        to_delete = []
        for tuple in data:
            if datetime.datetime.strptime(data[tuple]['date'], '%Y-%m-%dT%H:%M:%S.%f') + cache_lifetime < datetime.datetime.now():
                to_delete += [tuple]
        
        for key in to_delete:
            del data[key]
        
    with open('Cache.json', 'w') as cache:
        json.dump(data, cache, indent=4)

def clean_cache_thread():
    while(True):
        cache_clean()
        time.sleep(5)

def read_config():
    global months, days, hours, minutes, cache_lifetime 
    with open('Config.json') as config:
        data = json.load(config)
        months = data["cache_lifetime"]["months"]
        days = data["cache_lifetime"]["days"]
        hours = data["cache_lifetime"]["hours"]
        minutes = data["cache_lifetime"]["minutes"]

    cache_lifetime = datetime.timedelta(
    days=days + 30*months,
    hours=hours,
    minutes=minutes,
    )
    return data

def readBytes(arr):
    i=0
    array = []
    while(i<len(arr)):
        if(arr[i]=="\\" and arr[i+1]=="\\"):
            array.append(arr[i+2]*16 + arr[i+3])
            i += 4
        else:
            array.append(arr[i])
            i += 1
    return array

def main(**options):
    config = read_config()
    threading._start_new_thread(clean_cache_thread, ())
    puerto = options.get("puerto")
    ip_resolver = options.get("resolver")
    

    localIP     = "127.0.0.1"
    localPort   = int(puerto)
    bufferSize  = 1024

    msgFromServer       = "Hello UDP Client"
    
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))
    print("UDP server up and listening")

    # Listen for incoming datagrams
    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientIP  = "Client IP Address:{}".format(address)

        header, domain, tipo, other = extractHeaderDomainOther(message)

        """print("Header:", header)
        print("Domain:", domain)
        print("Tipo:", tipo)"""
            

        #Cache
        cache = open('Cache.json', 'r')
        data = json.load(cache)

        
        if tipo not in [1,15,28]:
            UDPServerSocket.sendto(str.encode(""), address)
            print("Ignorando...")
            continue

        elif domain in config['filter']['excluded']:
            UDPServerSocket.sendto(str.encode(""), address)
            print("Ignorando...")
            continue


        #Si tenemos que redirigir el dominio
        elif domain in config['filter']['redirected']:
            print("Redirigir!")
            redirect_to = config['filter']['redirected'][domain]
            print(redirect_to)
            
            ip_response, msgFromResolver, bytesToSend = sendToResolver(message, domain, ip_resolver)
            indice_respuesta,rdata,rdlength, qtype = parsear_respuesta(msgFromResolver)

            #Cambiar las respuestas por solo 1
            hexage = bytesToSend.hex()
            numberResponses = int(hexage[15])
            hexage = hexage[:14] + '01' + hexage[16:]
            print("HEXAGE:")
            print(hexage)

            
            
            new_ip = config['filter']['redirected'][domain]
            print(new_ip)

            #Para comprobar si se tiene que reemplazar la ip o no
            replace = False
            print(qtype)
            if(qtype[1]==1):
                #A
                if("." in new_ip):
                    print("hola")
                    new_ip = new_ip.split(".")
                    replace = True

            elif(qtype==28):
                #AAAA
                if(":" in new_ip):
                    new_ip = new_ip.split(":")
                    replace = True

            elif(qtype==15):
                #MX
                break

            #Si replace es False, no seguir con el reemplazo
            if (not replace):
                pass

            #Sacar el hexadecimal de la ip nueva
            hexa_newip = ''
            for i in new_ip:
                if(int(i)<16):
                    hexa_newip += '0' + i
                else:
                    hexa_newip += hex(int(i))[2:]

            #Encontrar la ip antigua en hexa_rdata
            hexa_oldip = ''
            for i in rdata:
                if(int(i)<16):
                    hexa_oldip += '0' + str(i)
                else:
                    hexa_oldip += hex(i)[2:]

            print("HEXARDATA: " + hexa_oldip) 
            
            #Reemplazar la ip antigua con la ip nueva
            hexage = hexage.replace(hexa_oldip, hexa_newip)
            print(hexa_newip)

            #Borrar las demas ips
            #Ahora hay que borrar las respuestas que no nos interesan
            #Sabemos que hay 12 bytes fijos de respuesta + RDLENGTH
            #hay que eliminar desde: indice_respuesta + (12 + rdlength)
            #hasta:                  indice_respuesta + (numberResponses-1)*(12 + rdlength)
            hexage = hexage[0:(indice_respuesta + (12 + rdlength))*2] #+ hexage[(indice_respuesta + (12 + rdlength))*2:(indice_respuesta + (numberResponses-1)*(12 + rdlength))*2] 


            UDPServerSocket.sendto(bytes.fromhex(hexage), address)
            continue

        #Si esta cacheado
        elif(domain in data):
            respuesta_cacheada = data[domain]["response"]
            mensaje_inicial = message.hex() 
            respuesta_cliente =  mensaje_inicial[0:4] + respuesta_cacheada[4:] 
            UDPServerSocket.sendto(bytes.fromhex(respuesta_cliente), address)
            continue

        
        #Nueva consulta, forwardear
        
        #Enviamos a resolver, obtenemos ip
        ip_response, msgFromResolver, bytesToSend = sendToResolver(message, domain, ip_resolver)

        
        #Agregamos a logs
        actual_date = addToLogs(address[0], ip_response)
        
        
    
        print(domain) 

        # Respondemos al cliente
        UDPServerSocket.sendto(bytesToSend, address)



if __name__ == "__main__":
    main(puerto=sys.argv[1], resolver=sys.argv[2])