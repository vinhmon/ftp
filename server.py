# TODO: 
#	-server needs to send error messages back to client
#	-error checks for input
#	-error checks for file not found
#	-protocol design

import socket
import sys
import subprocess

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

	fileName = data[9:]
	fileObj = open(fileName, "r")

	ephemeralSocket = int(data[:5])

	dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dataConnection.connect((serverAddr, ephemeralSocket))

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

	dataConnection.close()

def main():
	if len(sys.argv) != 2:
        	print("USAGE: python " + sys.argv[0] + " <Server Port>")
		exit()

	listenPort = int(sys.argv[1])

	controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	controlSocket.bind(('', listenPort))
	controlSocket.listen(1)

        print("The server is ready to receive.")

	while 1:
		controlConnection, addr = controlSocket.accept()
		print("--Connection established.")

		while 1:
			data = controlConnection.recv(1024) # receive command and ephemeral port from client through control channel
			if data[0:2] == "ls":
				# create new data connection for data transfer
				ephemeralSocket = int(data[3:])
				dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataConnection.connect(("localhost", ephemeralSocket))

				dataToSend = subprocess.check_output(["ls"])
				dataConnection.send(dataToSend)

				dataConnection.close()
				print("List files success!\n")

			elif data[5:8] == "get":
				sendFile(data, controlConnection)
				print("Query success!\n")

			elif data[5:8] == "put":
                                # create new data connection for data transfer
				ephemeralSocket = int(data[:5])
                                dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                dataConnection.connect(("localhost", ephemeralSocket))

                                fileData = ""
                                recvBuff = ""
                                fileSize = 0	
                                fileSizeBuff = ""

                                fileSizeBuff = receiveFile(dataConnection, 10)
                                fileSize = int(fileSizeBuff)

                                fileData = receiveFile(dataConnection, fileSize)
                                
                                file = open(data[9:], "w")
                                file.write(fileData)
                                file.close()

                                dataConnection.close()

				print("Upload success!\n")

			elif data[0:4] == "quit":
				print("--Connection closed.")
				break

	controlConnection.close()

if __name__ == '__main__':
	main()
