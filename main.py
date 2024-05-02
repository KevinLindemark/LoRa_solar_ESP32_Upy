from micropython_rfm9x import *
from machine import SPI, Pin, deepsleep, I2C
from time import sleep
# INA219 demo - uses https://github.com/robert-hh/INA219
import ina219

i = I2C(1, scl=Pin(22), sda=Pin(21))
print("I2C Bus Scan: ", i.scan(), "\n")

sensor = ina219.INA219(i)
sensor.set_calibration_16V_400mA()
 
# my test circuit is Solar/battery supply through 218 ohm resistance
r_1 = 218
r_s = 0.1  # shunt resistor on INA219 board


#ESP32 Example

#CS = Pin(33, Pin.OUT)
RESET = Pin(14, Pin.OUT)
#spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(5), mosi=Pin(18), miso=Pin(19))
CS = Pin(5, Pin.OUT)
#RESET = Pin(22, Pin.OUT)
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

RADIO_FREQ_MHZ = 433.0
# Initialze RFM radio
rfm9x = RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
print("Sent Hello World message!")

# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 252 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for packets...")
count = 0
while True:
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
        #print("sending to RPI")
            # current is returned in milliamps
        print("Current       / mA: %8.3f" % (sensor.current))
        rfm9x.send(bytes("Current       / mA: %8.3f \n" % (sensor.current), "utf-8"))
        # shunt_voltage is returned in volts
        print("Shunt voltage / mV: %8.3f" % (sensor.shunt_voltage * 1000))
        rfm9x.send(bytes("Shunt voltage / mV: %8.3f \n" % (sensor.shunt_voltage * 1000), "utf-8"))
        # estimate supply voltage from known resistance * sensed current
        print("3V3 (sensed)  / mV: %8.3f" % ((r_1 + r_s) * sensor.current))
        
        rfm9x.send(bytes("3V3 (sensed)  / mV: %8.3f \n" % ((r_1 + r_s) * sensor.current), "utf-8"))
        #rfm9x.send(bytes("Hello from ESP32!\r\n", "utf-8"))
    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
    count += 1
    if count > 3:
        print("going to sleep for xx seconds!")
        deepsleep(10000)
        