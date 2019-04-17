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
                'response': str(bytesToSend),

            }

    with open('Cache.json', 'w') as cache:
        json.dump(data, cache, indent=4)

    parsear_respuesta(msgFromResolver)
    
    
    print("IP:", extractIP(msgFromResolver))
    ip_response = extractIP(msgFromResolver)

    return ip_response, msgFromResolver, bytesToSend

def parsear_respuesta(msgFromResolver):
    print("Respuesta:", msgFromResolver)
    print("Header:", msgFromResolver[:12])
    limit = find_zero(msgFromResolver[12:])+1
    print("Query:", msgFromResolver[12:limit+11])
    print("QType:", msgFromResolver[limit+12:limit+12+2])
    print("QClass:", msgFromResolver[limit+12+2:limit+12+4])
    print("Response Name:", msgFromResolver[limit+12+4:limit+12+6])
    print("Response Type:", msgFromResolver[limit+12+6:limit+12+8])
    print("Response class:", msgFromResolver[limit+12+8:limit+12+10])
    print("TTL:", msgFromResolver[limit+12+10:limit+12+14])
    print("RDLENGTH:", msgFromResolver[limit+12+14:limit+12+16])
    rdlength = msgFromResolver[limit+12+14:limit+12+16]
    print("RDATA:", msgFromResolver[limit+12+16:limit+12+16+rdlength[1]])

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

        print("Header:", header)
        print("Domain:", domain)
        print("Tipo:", tipo)
            

        #Cache
        cache = open('Cache.json', 'r')
        data = json.load(cache)

        
        if tipo not in [1,15,28]:
            UDPServerSocket.sendto(str.encode(""), address)
            print("Ignorando...")

        elif domain in config['filter']['excluded']:
            UDPServerSocket.sendto(str.encode(""), address)
            print("Ignorando...")


        #Si tenemos que redirigir el dominio
        elif domain in config['filter']['redirected']:
            print("Redirigir!")
            redirect_to = config['filter']['redirected'][domain]
            print(redirect_to)
            words = redirect_to.split('.')
            
            #Crea bytes para dominio al que debe redirigirse
            bytes_domain = []
            for w in words:
                bytes_domain.append(len(w))
                for char in w:
                    bytes_domain.append(ord(char))
            bytes_domain.append(0)
            
            #Modificar header para que sea una respuesta
            print("Header antes:", header)
            header[2:12] = [129, 128, 0, 1, 0, 1, 0, 0, 0, 1]


            print("Header despues:", header)
            print(bytes_domain)
            print(other)
            print(header + bytes_domain + other)

            bytesToSend = bytes(header + bytes_domain + other)


            #bytesToSend = str.encode(data[domain])
            UDPServerSocket.sendto(bytesToSend, address)

        elif(domain in data):
            print(bytesToArray(data[domain]["response"]))
        
        #Nueva consulta, forwardear
        else:
            #Enviamos a resolver, obtenemos ip
            ip_response, msgFromResolver, bytesToSend = sendToResolver(message, domain, ip_resolver)
            
            #Agregamos a logs
            actual_date = addToLogs(address[0], ip_response)
            
            
        
            print(domain) 

            # Respondemos al cliente
            UDPServerSocket.sendto(bytesToSend, address)



if __name__ == "__main__":
    main(puerto=sys.argv[1], resolver=sys.argv[2])
