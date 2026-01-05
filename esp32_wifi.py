import socket

HOST = "0.0.0.0"   # poslouchá na všech IP
PORT = 5000        # port (musí sedět s ESP32)

# vytvoření socketu
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Server spuštěn, čekám na ESP32...")

conn, addr = server.accept()
print("Připojeno z:", addr)

while True:
    data = conn.recv(1024)   # přijme data (max 1024 B)

    if not data:
        print("Klient se odpojil")
        break

    hodnota = data.decode().strip()
    if hodnota != "":
        print("Přijatá hodnota:", hodnota)

conn.close()
server.close()
