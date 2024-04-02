import csv
import socket
import threading
from datetime import datetime

# Server IP(Static - preferred); Server Port
SERVER_IP = "192.168.134.252"
SERVER_PORT = 56789

# File paths
input_vin = 'vin_input.csv'
map_vin = 'map_vin.csv'

# Allowed MAC addresses
allowed_addresses = {"ff:ff:c5:16:68:bf", "51:00:23:08:00:86"}

# Initialize last_map_address
last_map_address = None

# Setup server
def setup_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((SERVER_IP, SERVER_PORT))
    server_sock.listen()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    return server_sock

# Handle client connection
def receive_data(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            process_data(data.decode(), addr)

# Process received data
def process_data(data, addr):
    print(f"Data received from {addr}: {data}")
    # Extract client name and process data accordingly
    client_name = data.split(',')[0]
    write_to_client_file(client_name, data)

# Read and clear VIN number
def read_and_clear_vin():
    with open(input_vin, 'r', newline='') as vin_file:
        vin_number = vin_file.readline().strip()
    with open(input_vin, 'w', newline='') as vin_file:
        vin_file.write('')
    return vin_number

# Map VIN number with device address
def map_vin_number(client_name, device_address):
    global last_map_address
    if client_name == "Client1" and device_address in allowed_addresses and device_address != last_map_address:
        vin_number = read_and_clear_vin()
        with open(map_vin, 'a', newline='') as map_file:
            csv_writer = csv.writer(map_file)
            csv_writer.writerow([vin_number, device_address])
            last_map_address = device_address
        return vin_number
    else:
        return get_latest_vin_for_device(device_address)

# Get latest VIN number for device address
def get_latest_vin_for_device(device_address):
    try:
        with open(map_vin, 'r', newline='') as map_file:
            csv_reader = csv.reader(map_file)
            for row in reversed(list(csv_reader)):
                if row[1] == device_address:
                    return row[0]
    except FileNotFoundError:
        print("The mapping file does not exist.")
        return None

# Write data to client's CSV file
def write_to_client_file(client_name, data):
    try:
        device_address = data.split(',')[1]
        tag_name = data.split(',')[2]
        rssi = int(data.split(',')[3])
        
        vin_number = map_vin_number(client_name, device_address)
        if vin_number:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row_data = [timestamp.split()[1], timestamp.split()[0], client_name, tag_name, device_address, rssi, vin_number]
            
            with open(f'{client_name}.csv', 'a', newline='') as client_csv_file:
                csv_writer = csv.writer(client_csv_file)
                csv_writer.writerow(row_data)
                print(f"Data written to {client_name}.csv: {row_data}")
        else:
            print(f"No VIN number found for device {device_address}")
    except Exception as e:
        print(f"Error writing to client file: {e}")

# Server code execution
if __name__ == "__main__":
    server_sock = setup_server()

    try:
        while True:
            conn, addr = server_sock.accept()
            thread = threading.Thread(target=receive_data, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        server_sock.close()

This is server script

