# TODO: 
#	-server needs to send error messages back to client
#	-error checks for input
#	-error checks for file not found
#	-protocol design

import socket
import sys

def receiveFile(sock, numBytes):
	recvBuff = ""
	tmpBuff = ""

	while len(recvBuff) < numBytes:
		tmpBuff =  sock.recv(numBytes)
		if not tmpBuff:
			break
		recvBuff += tmpBuff
	return recvBuff

def sendFile(data, sock):
	serverAddr = "localhost"

	fileName = data[4:]
	fileObj = open(fileName, "r")

	dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSocket.bind(("", 0))

	s = str(dataSocket.getsockname()[1]) + data

        sock.send(s)
	dataSocket.listen(1)

        
        dataConnection, addr = dataSocket.accept()
        print("Data transfer channel connection up.\n")

        numSent = 0
        fileData = None

        while True:
                fileData = fileObj.read(65536)
                if fileData:
                        dataSizeStr = str(len(fileData))
                        while len(dataSizeStr) < 10:
                                dataSizeStr = "0" + dataSizeStr
                        fileData = dataSizeStr + fileData
                        numSent = 0
                        while len(fileData)> numSent:
                                numSent += dataConnection.send(fileData[numSent:])
                else:
                        break

        print("The sent file size is: ", (numSent-10))
        print("The file name is: " + fileName)

        dataConnection.close()

def main():
	if len(sys.argv) != 3:
        	print("USAGE: python " + sys.argv[0] + " <Server Host> <Server Port>")
		exit()

	serverAddr = sys.argv[1]
	serverPort = int(sys.argv[2])

	controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	controlSocket.connect((serverAddr, serverPort))
	print("Now connected to server.")

	data = raw_input("ftp> ")
	while data != "quit":
		if data[0:2] == "ls":
			dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            		dataSocket.bind(("", 0))

			s = data + " " + str(dataSocket.getsockname()[1])
			
            		# send ephemeral port number and command to the server
            		controlSocket.send(s)
            		dataSocket.listen(1)
			
			
                        dataConnection, addr = dataSocket.accept()
                        print("Data transfer channel connection up.\n")

                        serverData = dataConnection.recv(8192)
                        print(serverData)

                        dataConnection.close()

		elif data[0:3] == "get":
			if len(sys.argv) != 2:	# bug here
				print("USAGE: get <FILE NAME>")

                                dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            			dataSocket.bind(("", 0))

				s = str(dataSocket.getsockname()[1]) + data
			
            			# send ephemeral port number and command to the server
            			controlSocket.send(s)
            			dataSocket.listen(1)

                                dataConnection, addr = dataSocket.accept()
				print("Data transfer channel connection up.\n")

                                fileData = ""
                                recvBuff = ""
                                fileSize = 0	
                                fileSizeBuff = ""

                                fileSizeBuff = receiveFile(dataConnection, 10)
                                fileSize = int(fileSizeBuff)

                                print("The received file size is: ", fileSize)
                                fileData = receiveFile(dataConnection, fileSize)
                                print("The file name is: " + data[4:])

                                file = open(data[4:], "w")
                                file.write(fileData)
                                file.close()

                                dataConnection.close()

		elif data[0:3] == "put":
			if len(sys.argv) != 2:	# bug here
				print("USAGE: put <FILE NAME>")

                        sendFile(data, controlSocket)
				
		else:
			print("Use commands: ls, get <FILE NAME>, put <FILE NAME>, or quit")

		data = raw_input("ftp> ")	# get next input from client

	controlSocket.send(data)	# send "quit" to server
	controlSocket.close()

if __name__ == '__main__':
	main()
