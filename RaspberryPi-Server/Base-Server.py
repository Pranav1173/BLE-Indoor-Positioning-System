import csv
import socket
from datetime import datetime

# Replace this with the desired IP address and port to bind the server
SERVER_IP = "192.168.74.252"
SERVER_PORT = 56789

# Replace these with the addresses you want to filter
allowed_addresses = {"ff:ff:c5:16:68:bf", "51:00:23:08:00:86"}

def setup_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((SERVER_IP, SERVER_PORT))
    server_sock.listen()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    return server_sock

def receive_data(server_sock):
    conn, addr = server_sock.accept()
    print(f"Connected by {addr}")

    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            process_data(data.decode())

def process_data(data):
    # Parse the received data and save it to a CSV file
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Extract the relevant information from the received data
    # Format: timestamp, device_address, device_name, rssi_value
    # Example: 2022-01-01 12:34:56,00:11:22:33:44:55,DeviceName,-50
    row = f"{timestamp},{data}"
    print(data)
    # Check if the device address is in the allowed addresses list
    device_address = row.split(',')[2]
    if device_address in allowed_addresses:
        with open('espdataclient1.csv', 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(row.split(','))
            print(f"Data received and saved: {row}")

if __name__ == "__main__":
    server_sock = setup_server()

    try:
        while True:
            receive_data(server_sock)
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        server_sock.close()
