import csv
import socket
from datetime import datetime

# Replace this with the desired IP address and port to bind the server
SERVER_IP = "192.168.74.252"
SERVER_PORT = 56789

# Replace these with the addresses you want to filter
allowed_addresses = {"ff:ff:c5:16:68:bf", "51:00:23:08:00:86"}

# Master CSV file header
MASTER_CSV_HEADER = ["Time", "Date", "Client Name", "Tag Name", "Address", "Zone", "RSSI Value", "Distance"]

# Dictionary to store received records within a minute for each client
records_within_minute = {}

def setup_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((SERVER_IP, SERVER_PORT))
    server_sock.listen()
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    return server_sock

def read_existing_data(client_name):
    # Read existing data from the respective client's CSV file
    existing_data = []
    try:
        with open(f'{client_name}.csv', 'r') as existing_csv_file:
            csv_reader = csv.reader(existing_csv_file)
            for row in csv_reader:
                existing_data.append(row)
    except FileNotFoundError:
        pass
    return existing_data

def calculate_distance(tag_data):
    # Use a fixed RSSI value of 70 for 1 meter
    fixed_rssi = 70

    # Take the last RSSI value from the tag data
    last_rssi_str = tag_data[-1][6] if tag_data else '0'
    
    # Convert RSSI value to float to handle decimal values
    last_rssi = float(last_rssi_str)

    # Calculate distance based on the fixed RSSI value
    distance = abs(fixed_rssi / last_rssi) if last_rssi != 0 else 0

    return last_rssi, distance

def categorize_zone(distance):
    # Categorize the zone based on distance
    if distance < 0.8:
        return "Immediate"
    elif 0.8 <= distance <= 1.5:
        return "Near"
    else:
        return "Far"

def process_existing_data(client_name, existing_data):
    # Process existing data and calculate distance for each tag
    for row in existing_data:
        device_address = row[4]
        if device_address in allowed_addresses:
            if device_address not in records_within_minute[client_name]:
                records_within_minute[client_name][device_address] = []

            records_within_minute[client_name][device_address].append(row)

            if len(records_within_minute[client_name][device_address]) >= 4:
                # Validate if the records are for the same tag
                tag_names = set([record[3] for record in records_within_minute[client_name][device_address]])
                if len(tag_names) == 1:
                    # Calculate distance for the tag
                    avg_rssi, distance = calculate_distance(records_within_minute[client_name][device_address])

                    # Categorize the zone based on distance
                    zone = categorize_zone(distance)

                    # Prepare data for the master CSV file
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S').split()
                    master_csv_data = [timestamp[1], timestamp[0], client_name, tag_names.pop(), device_address, zone, str(avg_rssi), str(distance)]

                    # Write the record to the master CSV file
                    with open('masterdata.csv', 'a', newline='') as master_csv_file:
                        csv_writer = csv.writer(master_csv_file)
                        if master_csv_file.tell() == 0:
                            # Write header if the file is empty
                            csv_writer.writerow(MASTER_CSV_HEADER)
                        csv_writer.writerow(master_csv_data)
                        print(f"Data written to masterdata.csv: {master_csv_data}")

                    # Clear the records for the client and device address
                    records_within_minute[client_name][device_address] = []

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
    # Format: timestamp, client_name, device_address, tag_name, rssi_value
    # Example: 2022-01-01 12:34:56,ESP32-SL-Client1,00:11:22:33:44:55,TagName,-50
    row = f"{timestamp},{data}"
    print(data)

    # Check if the device address is in the allowed addresses list
    device_address = row.split(',')[2]
    tag_name = row.split(',')[3]
    client_name = row.split(',')[1]  
    
    if client_name not in records_within_minute:
        records_within_minute[client_name] = {}

    if device_address in allowed_addresses:
        # Split the row data
        row_data = row.split(',')

        # Calculate distance based on RSSI value
        rssi_value = int(row_data[4])
        distance = abs(70 / rssi_value) if rssi_value != 0 else 0

        # Prepare data for the client CSV file
        client_csv_data = [timestamp.split()[1], timestamp.split()[0], client_name, tag_name, device_address, str(distance), int(rssi_value)]

        # Write the record to the respective client's CSV file
        with open(f'{client_name}.csv', 'a', newline='') as client_csv_file:
            csv_writer = csv.writer(client_csv_file)
            csv_writer.writerow(client_csv_data)
            print(f"Data written to {client_name}.csv: {client_csv_data}")

        # Check if the client has records within a minute for the device address
        if device_address not in records_within_minute[client_name]:
            records_within_minute[client_name][device_address] = []

        # Add the record to the list for the client and device address
        records_within_minute[client_name][device_address].append(client_csv_data)

        # Check if there are more than 4 records within a minute for the device address
        if len(records_within_minute[client_name][device_address]) > 4:
            # Validate if the records are for the same tag
            tag_names = set([record[3] for record in records_within_minute[client_name][device_address]])
            if len(tag_names) == 1:
                # Calculate distance for the tag
                avg_rssi, distance = calculate_distance(records_within_minute[client_name][device_address])

                # Categorize the zone based on distance
                zone = categorize_zone(distance)

                # Prepare data for the master CSV file
                master_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S').split()
                master_csv_data = [master_timestamp[1], master_timestamp[0], client_name, tag_names.pop(), device_address, zone, str(avg_rssi), str(distance)]

                # Write the record to the master CSV file
                with open('masterdata.csv', 'a', newline='') as master_csv_file:
                    csv_writer = csv.writer(master_csv_file)
                    if master_csv_file.tell() == 0:
                        # Write header if the file is empty
                        csv_writer.writerow(MASTER_CSV_HEADER)
                    csv_writer.writerow(master_csv_data)
                    print(f"Data written to masterdata.csv: {master_csv_data}")

                # Clear the records for the client and device address
                records_within_minute[client_name][device_address] = []

if __name__ == "__main__":
    server_sock = setup_server()

    # Initialize records_within_minute for each client
    for client_num in range(1, 31):
        client_name = f"ESP32-SL-Client{client_num}"
        records_within_minute[client_name] = {}

        # Process existing data from the respective client's CSV file
        existing_data = read_existing_data(client_name)
        process_existing_data(client_name, existing_data)

    try:
        while True:
            receive_data(server_sock)
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        server_sock.close()
