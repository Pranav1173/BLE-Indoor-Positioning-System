#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <WiFi.h>

#define SCAN_DURATION 1 // in seconds

// Replace these with your WiFi credentials
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";

// Replace this with your server's IP address and port
const char* serverIp = "192.168.74.252";
const int serverPort = 56789;

// Replace this with a unique client name for the ESP32
const char* clientName = "ESP32-Client";

WiFiClient client;

class MyBLEScanCallbacks : public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
        // Device found, send data to the server over WiFi
        sendToServer(advertisedDevice);
    }
};

void sendToServer(BLEAdvertisedDevice device) {
    if (!client.connect(serverIp, serverPort)) {
        Serial.println("Connection to server failed.");
        return;
    }

    Serial.println("Connected to server over WiFi.");

    String data = String(clientName) + "," +
                  String(device.getAddress().toString().c_str()) + "," +
                  String(device.getName().c_str()) + "," +
                  String(device.getRSSI()) + "\n";

    Serial.println("Sending data to server: " + data);

    client.print(data);
    client.flush();
    delay(10);

    Serial.println("Data sent to server.");

    client.stop();
}

void setup() {
    Serial.begin(115200);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }

    Serial.println("Connected to WiFi.");

    BLEDevice::init("");
    BLEScan* pBLEScan = BLEDevice::getScan(); 
    pBLEScan->setAdvertisedDeviceCallbacks(new MyBLEScanCallbacks());
    pBLEScan->setActiveScan(true);
    pBLEScan->setInterval(100);
    pBLEScan->setWindow(99);  
}

void loop() {
    BLEScanResults foundDevices = BLEDevice::getScan()->start(SCAN_DURATION, false);
    BLEDevice::getScan()->clearResults();
    delay(2000); // Wait for a moment before scanning again
}
