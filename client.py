import socket
import sys
import os
import random
import threading

if len(sys.argv)<6:
    print("Wrong Input")

serverName=str(sys.argv[1])
sportNum=int(sys.argv[2])
fileName=str(sys.argv[3])
windowSize=int(sys.argv[4])
MSS=int(sys.argv[5])

if sportNum!=7735:
    print("Use 7735 as the Port Number")
    raise SystemExit
if fileName not in os.listdir(os.getcwd()):
    print("File not found in the current directory")
    raise SystemExit

cportNum=random.randrange(1025,60000)
client=('', cportNum)
server=(serverName,sportNum)
clientSock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    clientSock.bind(client)
    print("Started listening on", client)
    clientSock.settimeout(0.05)
    print("Timeout value is set to 0.05 seconds")
except socket.error:
    print("Port already in use")
    raise SystemExit

segments=[]
fileSize=os.path.getsize(fileName)
with open(fileName,"rb") as f:
    data=f.read()
    f.close()

start=0
end=MSS
while fileSize>=0:
    if fileSize < MSS:
        end=start+fileSize
    segments.append(data[start:end])
    start+=MSS
    end+=MSS
    fileSize-=MSS

def checksum(segment, length):
    if (length % 2 != 0):
        segment += "0".encode('utf-8')
    x = segment[0] + ((segment[1]) << 8)
    y = (x & 0xffff) + (x >> 16)

    for i in range(2, len(segment), 2):
        x = segment[i] + ((segment[i + 1]) << 8)
        y = ((x + y) & 0xffff) + ((x + y) >> 16)
    return '{:16b}'.format(~y & 0xffff)

dataPkt='0101010101010101'
buffer=windowSize
prevSqn=sqnNum=0

def rdt_send(clientSock):
    global buffer,sqnNum
    while sqnNum < len(segments):
        while buffer > 0:
            sqnSent='{:032b}'.format(sqnNum)
            checksumSent=checksum(segments[sqnNum],len(segments[sqnNum]))
            segmentSent=sqnSent.encode('utf-8')+checksumSent.encode('utf-8')+dataPkt.encode('utf-8')+segments[sqnNum]
            sqnNum = (sqnNum+1)%2**31-1
            buffer-=1
            clientSock.sendto(segmentSent, server)

def acknowledgments(conn):
    global buffer,sqnNum,prevSqn
    while True:
        try:
            lastAck=conn.recv(1024)
            lastAck=lastAck.decode('utf-8')
            if lastAck[0:32]=='{:032b}'.format(prevSqn):
                buffer+=1
                prevSqn+=1
        except socket.timeout:
            print("Timeout, sequence number = ",prevSqn)
            buffer=windowSize
            sqnNum=prevSqn
        if sqnNum==len(segments):
            clientSock.sendto("0000000000000000000000000000000000000000000000000000000000000000Done".encode('utf-8'), server)
            clientSock.close()
            break

sendThread=threading.Thread(target=rdt_send, args=(clientSock,))
ackThread=threading.Thread(target=acknowledgments, args=(clientSock,))
sendThread.start()
ackThread.start()

while True:
    if KeyboardInterrupt:
        sendThread.join()
        ackThread.join()
        raise SystemExit