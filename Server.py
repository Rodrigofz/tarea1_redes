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
    other = message[end_of_string+15:]

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
        #print(i, arr[i])
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

def sendToResolver(message, ip_resolver, port=53):
    resolver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    bytesToSend = message
    resolver.sendto(bytesToSend, (ip_resolver,port))
    msgFromResolver = bytesToArray(resolver.recvfrom(bufferSize)[0])

    print("Resolver: ",msgFromResolver)
    print("IP:", extractIP(msgFromResolver))
    ip_response = extractIP(msgFromResolver)

    return ip_response, msgFromResolver

def addToLogs(clientIP, ip_response):
    logs = open('LOGS', 'a+')
    actual_date = datetime.datetime.now().isoformat()
    logs.write(actual_date + ', ' + clientIP + ', ' + ip_response + '\n')
    logs.close()


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


def main(**options):
    read_config()
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

        header, domain, tipo, _ = extractHeaderDomainOther(message)

        print("Header:", header)
        print("Domain:", domain)
        print("Tipo:", tipo)
            

        #Cache
        cache = open('Cache.json', 'r')
        data = json.load(cache)

        
        if tipo not in [1,15,28]:
            UDPServerSocket.sendto(str.encode("Mensaje en tipo raro, no le hacemos a eso"), address)

        #Si tenemos cacheado ya ese dominio
        elif False:
            bytesToSend = str.encode(data[domain])
            UDPServerSocket.sendto(bytesToSend, address)


        #Nueva consulta, forwardear
        else:
            #Enviamos a resolver, obtenemos ip
            ip_response, msgFromResolver = sendToResolver(message, ip_resolver)
            
            #Agregamos a logs
            addToLogs(clientIP, ip_response)
            
            #Agregamos al cache
            with open('Cache.json') as cache:
                data = json.load(cache)
                data[domain] = {
                        'date': actual_date,
                        'response': ip_response,
                    }

            with open('Cache.json', 'w') as cache:
                json.dump(data, cache, indent=4)
        
            print(domain) 

            # Respondemos al cliente
            UDPServerSocket.sendto(bytesToSend, address)



if __name__ == "__main__":
    main(puerto=sys.argv[1], resolver=sys.argv[2])
