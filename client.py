import connection

TCP_IP = '127.0.0.1'
TCP_PORT = 6555 #EyeTribe port 
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

if __name__ == '__main__':
	connection.connect(TCP_IP, TCP_PORT, BUFFER_SIZE, MESSAGE)