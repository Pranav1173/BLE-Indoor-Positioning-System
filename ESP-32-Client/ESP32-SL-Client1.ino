#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <WiFi.h>

#define SCAN_DURATION 1

const char* ssid = "Raspberrypi-WiFi";
const char* password = "ame123AME";
const char* serverIp = "192.168.4.1"; // Raspberry Pi's IP address when acting as an access point
const int serverPort = 56789;
const char* clientName = "ESP32-Client1";

WiFiClient client;

class MyBLEScanCallbacks : public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
        sendToServer(advertisedDevice);
    }
};

void sendToServer(BLEAdvertisedDevice device) {
    if (!client.connect(serverIp, serverPort)) {
		Serial.println("Connection to server failed.");
        return;
    }

    String data = String(clientName) + "," +
                  String(device.getAddress().toString().c_str()) + "," +
                  String(device.getName().c_str()) + "," +
                  String(device.getRSSI()) + "\n";

    client.print(data);
    client.flush();
    delay(10);

    client.stop();
}


void setup() {
    Serial.begin(115200);

    // Connect to the Raspberry Pi's access point
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
    delay(2000);
}
