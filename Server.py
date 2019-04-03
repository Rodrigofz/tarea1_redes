import socket
import sys
import binascii
 
def format_hex(hex):
    """format_hex returns a pretty version of a hex string"""
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)

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
    
        print(binascii.hexlify(message[:12])) #Header
        print()
        print(clientIP)

        # Sending a reply to client
        UDPServerSocket.sendto(bytesToSend, address)

if __name__ == "__main__":
    main(puerto=sys.argv[1], resolver=sys.argv[2])
