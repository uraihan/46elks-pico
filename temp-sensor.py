import machine
import onewire
import ds18x20
import network
import urequests
import base64
import time

# Initialize the communications protocol with the temperature device (OneWire bus on GPIO 5)
ds_pin = machine.Pin(7) # Double check to make sure which pin is connected to the sensor
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('I am now connected to your DS device, with address:', roms)

# Add wifi credentials
ssid = "NAMENAMENAME" # The name of wifi
password = "password" # The wifi password

# Add the 46elks credentials
api_username = 'xxxxxxxxx' # 46elks API token
api_password = 'xxxxxxxxx' # 46elks token password

# The SMS parameters
sms_from = 'Name'  # Change if desired
sms_to = '+358123456789'  # Replace with actual phone number

# Connecting to wifi and keep on trying during 30 seconds at 5 seconds intervals
def connect_to_wifi(ssid, password, timeout_sec=30, retry_interval_sec=5):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    # Waiting to be connected to wifi
    start_time = time.time()
    while not wifi.isconnected() and time.time() - start_time < timeout_sec:
        print("Wait. I'm connecting to your wifi..")
        wifi.connect(ssid, password)
        time.sleep(retry_interval_sec)

    # Prints if connected or if there was no connection within the timelimit (retry in that case)
    if wifi.isconnected():
        print("I'm now connected to the wifi!\n\n")
    else:
        print("Wifi connection failed within the specified time of 30 seconds. Please try again.")

# Call the connect_wifi function and connect to the wifi
connect_to_wifi(ssid, password)

# Send an SMS once the desired temperature is reached
def send_sms(temperature):
    url = 'https://api.46elks.com/a1/sms'
    auth_string = f"{api_username}:{api_password}"
    headers = {
        "Authorization": "Basic " + base64.b64encode(auth_string.encode()).decode('utf-8'),
        "Content-type": "application/x-www-form-urlencoded"
    }
    sms_content = f"\n\nWarning! The temperature has now reached {temperature}°C"
    data_str = f"from={sms_from}&to={sms_to}&message={sms_content}"

    response = urequests.post(url, headers=headers, data=data_str.encode())
    print("\nThis is the SMS response from the API:\n", response.text) # Printing the response for debugging purposes

# Keep measuring the temperature and print it
while True:
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temperature = ds_sensor.read_temp(rom)
        print('The temperature is now:', temperature, '°C')

        # Will send an SMS once the desired temperature is reached
        if temperature >= 25.0: # Temperature threshold
            print("\nSending warning SMS via the 46elks API!")
            send_sms(temperature)
            time.sleep(60)  # Wait for 60 seconds until next SMS gets send, to avoid spam		