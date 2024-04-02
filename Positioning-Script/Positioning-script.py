import os
import csv
from datetime import datetime, timedelta

client_files_directory = '/home/rpi/Desktop/BLE-Positioning/'
master_file_path = 'master.csv'
position_path = 'finalposition.csv'

def process_all_client_files():
    all_files = os.listdir(client_files_directory)
    csv_files = [file for file in all_files if file.startswith('Client') and file.endswith('.csv')]

    for csv_file in csv_files:
        file_path = os.path.join(client_files_directory, csv_file)
        print(f"Processing file: {file_path}")
        if check_recent_changes(file_path):
            process_client_file(file_path)
        else:
            print("No recent changes. Skipping file...")

def check_recent_changes(client_file_path):
    last_modified_time = datetime.fromtimestamp(os.path.getmtime(client_file_path))
    return (datetime.now() - last_modified_time) < timedelta(minutes=0.5)

def process_client_file(client_file_path):
    with open(client_file_path, 'r') as client_csv_file:
        client_data = list(csv.reader(client_csv_file))

    if len(client_data) < 1:
        print("No records found. Skipping file...")
        return

    recent_records = client_data[-5:]
    recent_timestamp = datetime.strptime(recent_records[0][0], '%H:%M:%S')  # Adjust the timestamp format

    if not check_recent_changes(client_file_path):  # Remove the recent_timestamp argument
        print("Records are not recent. Skipping file...")
        return

    print("Client Data:", recent_records)  # Print client data for debugging

    client_name = recent_records[0][2]
    station_number = int(client_name.split('Client')[1])

    average_rssi = sum(int(row[5]) for row in recent_records) / 5
    zone = 'Far' if average_rssi <= -90 else ('Near' if average_rssi <= -75 else 'Immediate')
    vin_number = recent_records[0][6]  # Assuming VIN is in the 7th column

    update_master_file(client_name, recent_records[0][3], recent_records[0][4], average_rssi, zone, station_number, vin_number)
    if zone == 'Immediate':
        update_final_position_file(client_name, recent_records[0][3], recent_records[0][4], average_rssi, zone, station_number, vin_number)

def update_master_file(client_name, tag_name, device_address, average_rssi, zone, station_number, vin_number):
    current_time = datetime.now()
    row_data = [current_time.strftime('%H:%M:%S'), current_time.strftime('%Y-%m-%d'), client_name, tag_name, device_address, average_rssi, zone, station_number, vin_number]

    with open(master_file_path, 'a', newline='') as master_csv_file:
        csv_writer = csv.writer(master_csv_file)
        if os.path.getsize(master_file_path) == 0:
            csv_writer.writerow(['Time', 'Date', 'Client Name', 'Tag Name', 'Device Address', 'Average RSSI', 'Zone', 'Station Number', 'VIN'])
        csv_writer.writerow(row_data)
        print(f"Data written to {master_file_path}: {row_data}")

def update_final_position_file(client_name, tag_name, device_address, average_rssi, zone, station_number, vin_number):
    current_time = datetime.now()
    row_data = [current_time.strftime('%H:%M:%S'), current_time.strftime('%Y-%m-%d'), client_name, tag_name, device_address, average_rssi, zone, station_number, vin_number]

    with open(position_path, 'a', newline='') as position_csv_file:
        csv_writer = csv.writer(position_csv_file)
        if os.path.getsize(position_path) == 0:
            csv_writer.writerow(['Time', 'Date', 'Client Name', 'Tag Name', 'Device Address', 'Average RSSI', 'Zone', 'Station Number', 'VIN'])
        csv_writer.writerow(row_data)
        print(f"Data written to {position_path}: {row_data}")

process_all_client_files()
