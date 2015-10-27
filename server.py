# TODO: -replace current data connections with emphemeral connections, this should cover all the test ports
#	-server needs to send error messages back to client
#	-error checks for input
#	-error checks for file not found
#	-protocol design

import socket
import sys
import subprocess

def receiveFile(socket, numBytes):
	recvBuff = ""
	tmpBuff = ""

	while len(recvBuff) < numBytes:
		tmpBuff =  socket.recv(numBytes)
		if not tmpBuff:
			break
		recvBuff += tmpBuff
	return recvBuff

def sendFile(data, sock):
	serverAddr = "localhost"

	fileName = data
	fileObj = open(fileName, "r")

	dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	dataConnection.connect((serverAddr, 1231))

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
	testSocket = 9999	# test socket number

	controlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	controlSocket.bind(('', listenPort))
	controlSocket.listen(1)

	while 1:
		controlConnection, addr = controlSocket.accept()
		print("Connected.")

		while 1:
			data = controlConnection.recv(8192) # receive command from client through control channel
			if data[0:2] == "ls":
				dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataConnection.connect(("localhost", testSocket))

				dataToSend = subprocess.check_output(["ls"])
				dataConnection.send(dataToSend)

				dataConnection.close()
				print("List files success!\n")

			elif data[0:3] == "get":
				sendFile(data[4:], controlConnection)
				print("Query success!\n")

			elif data[0:3] == "put":
                                dataConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                dataConnection.connect(("localhost", 1232))

                                fileData = ""
                                recvBuff = ""
                                fileSize = 0	
                                fileSizeBuff = ""

                                fileSizeBuff = receiveFile(dataConnection, 10)
                                fileSize = int(fileSizeBuff)

                                print("The file size is: ", fileSize)
                                fileData = receiveFile(dataConnection, fileSize)
                                print("The file name is: " + data[4:])

                                file = open(data[4:], "w")
                                file.write(fileData)
                                file.close()

                                dataConnection.close()

				print("Upload success!")

			elif data[0:4] == "quit":
				print("Connection closed.")
				break

	controlConnection.close()

if __name__ == '__main__':
	main()
