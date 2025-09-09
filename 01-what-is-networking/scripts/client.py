import socket

# Create the socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
ip = "127.0.0.1"
server_port = 12345
client_socket.connect((ip, server_port))

# send message
client_socket.sendall("hello".encode())

# receive reply
data = client_socket.recv(1024).decode()
print(f"Received from server: {data}")

client_socket.close()