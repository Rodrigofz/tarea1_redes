import socket
import sys
import binascii
import datetime
 
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


def find_zero(arr):
    b = -1
    i = 0
    while(b!=0):
        i=i+1
        b = arr[i]
    return i


def main(**options):
    puerto = options.get("puerto")
    resolver = options.get("resolver")

    localIP     = "127.0.0.1"
    localPort   = int(puerto)
    bufferSize  = 1024

    msgFromServer       = "Hello UDP Client"
    bytesToSend         = str.encode(msgFromServer)

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
        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
    
        #print(binascii.hexlify(message[:12])) #Header bin(message[:12])[2:]
        #print(message)
        bits = []
        for i in range(len(message)):
            print(i, message[i])
            bits.append(message[i])

        header = bits[:12]
        
        limit = find_zero(bits[12:])

        domain = bits[12:limit+12] #El numero del principio indica el largo de la primera expresion, 
        #luego de ese largo sigue un numero indicando el largo de la siguiente expresion y asi....

        #AAAA: 28
        #A: 1
        #MX: 15
        tipo = bits[limit+13:limit+15]

        print("Header:", header)
        print("Domain:", domain)
        print("Tipo:", tipo)

        logs = open('LOGS', 'a+')
        actual_date = datetime.datetime.now().isoformat()
        logs.write(actual_date + ', ' + clientIP + '\n')
        logs.close()

        print(reconstruct(domain)) #Reconstruye el dominio a caracteres entendibles
        #print(message[:12].decode('utf8')) #Sitio
        #print(clientIP)

        # Sending a reply to client
        UDPServerSocket.sendto(bytesToSend, address)

if __name__ == "__main__":
    main(puerto=sys.argv[1], resolver=sys.argv[2])
