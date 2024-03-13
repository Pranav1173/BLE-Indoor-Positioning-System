import os
import csv
from datetime import datetime, timedelta

client_files_directory = '/home/rpi/Desktop/BLE-Positioning/'
master_file_path = 'master.csv'

def process_all_client_files():
    # List all files in the directory
    all_files = os.listdir(client_files_directory)

    # Filter only CSV files
    csv_files = [file for file in all_files if file.endswith('.csv')]

    for csv_file in csv_files:
        file_path = os.path.join(client_files_directory, csv_file)
        print(f"Processing file: {file_path}")

        # Check recent changes before processing
        if check_recent_changes(file_path):
            process_client_file(file_path)
        else:
            print("No recent changes. Skipping file...")

def check_recent_changes(client_file_path):
    # Check for recent changes in the client file
    last_modified_time = datetime.fromtimestamp(os.path.getmtime(client_file_path))
    current_time = datetime.now()
    time_difference = current_time - last_modified_time

    return time_difference < timedelta(minutes=0.5)

def process_client_file(client_file_path):
    # Example: Read data from the client file
    with open(client_file_path, 'r') as client_csv_file:
        client_data = list(csv.reader(client_csv_file))

    # Filter data for the specific client
    client_name = client_data[0][2]  # Assuming the client name is in the first row
    station_number = get_station_number(client_name)

    # Check if there are at least 5 records within the last 0.5 minutes
    if len(client_data) >= 5:
        # Calculate average RSSI for zone determination
        average_rssi = sum(int(row[5]) for row in client_data) / len(client_data)

        # Determine zone based on average RSSI
        if average_rssi > -75:
            zone = 'Immediate'
        elif -90 <= average_rssi <= -75:
            zone = 'Near'
        else:
            zone = 'Far'

        # Get the current time
        current_time = datetime.now()

        # Example: Update master file with the analysis results
        with open(master_file_path, 'a', newline='') as master_csv_file:
            csv_writer = csv.writer(master_csv_file)
            row_data = [current_time.strftime('%H:%M:%S'), current_time.strftime('%Y-%m-%d'), client_name, average_rssi, zone, station_number]
            csv_writer.writerow(row_data)
            print(f"Data written to {master_file_path}: {row_data}")
    else:
        print("Not enough records for analysis. Skipping file...")

def get_station_number(client_name):
    # Extract station number from the client name (assuming the name format is 'ClientX')
    return int(client_name.split('Client')[1])

# Call the function to process all client files
process_all_client_files()
