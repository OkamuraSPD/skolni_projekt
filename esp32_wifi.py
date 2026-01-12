import socket

# ================== KONFIGURACE ==================
HOST = "0.0.0.0"   # poslouchá na všech síťových rozhraních
PORT = 5000        # musí odpovídat ESP32

# ================== VYTVOŘENÍ SOCKETU ==================
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # rychlý restart
server.bind((HOST, PORT))
server.listen(1)
print("Server běží, čekám na ESP32...")

# ================== ČEKÁNÍ NA KLIENTA ==================
conn, addr = server.accept()
print(f"Připojeno z: {addr}")

# ================== BUFFER PRO PŘIJÍMÁNÍ ==================
buffer = ""  # sem se ukládají přijaté bajty, dokud nedojde \n

# ================== HLAVNÍ SMYČKA ==================
while True:
    try:
        # přijímáme max 1024 bajtů
        data = conn.recv(1024)

        # pokud klient zavřel spojení
        if not data:
            print("ESP32 se odpojilo")
            break

        # přidáme do bufferu
        buffer += data.decode()

        # zpracováváme všechny kompletní zprávy (oddělené '\n')
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)  # rozdělíme první zprávu
            line = line.strip()  # odstraníme mezery a \r
            if not line:
                continue

            print("Přijato:", line)

            # ============== PARSOVÁNÍ pin:value; ==============
            inputs = {}
            pairs = line.split(";")
            for pair in pairs:
                if ":" in pair:
                    pin_str, value_str = pair.split(":", 1)
                    try:
                        pin = int(pin_str)
                        value = int(value_str)
                        inputs[pin] = value
                    except ValueError:
                        # špatná data – ignorujeme
                        continue
            print("Rozparsováno:", inputs)

            # ============== LOGIKA SERVERU ==============
            # jednoduchý příklad: mapování vstupy -> výstupy
            outputs = {}
            # pokud vstup 34=1, zapni výstup 2
            outputs[2] = 1 if inputs.get(34, 0) == 1 else 0
            # výstupy 4 a 13 prostě kopírují hodnoty vstupů
            outputs[4] = inputs.get(35, 0)
            outputs[13] = inputs.get(32, 0)

            # ============== VYTVOŘENÍ ODPOVĚDI ==============
            response = ""
            for pin, value in outputs.items():
                response += f"{pin}:{value};"

            # přidáme \n jako konec zprávy
            response += "\n"

            # ============== ODESLÁNÍ ZPĚT NA ESP32 ==============
            conn.sendall(response.encode())
            print("Odesláno:", response.strip())

    except ConnectionResetError:
        print("ESP32 se neočekávaně odpojilo")
        break
    except Exception as e:
        print("Chyba:", e)
        break

# ================== UKLID ==================
conn.close()
server.close()
print("Server ukončen")
