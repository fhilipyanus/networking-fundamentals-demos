import socket

# Create the TCP Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to localhost on port 12345
ip = "127.0.0.1"
server_port = 12345
server_socket.bind((ip, server_port))
server_socket.listen(1)
print(f"Server listening on {ip} and port {server_port}")

# Accept a connection
conn, addr = server_socket.accept()
print(f"Connection from {addr}")

# Receive data from client
data = conn.recv(1024).decode()
print(f'Received from client :{data}')

# Send reply
conn.sendall("world".encode())

# Close connection
conn.close()
server_socket.close()