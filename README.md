# uart-nmea-reader

Simple Python library to fetch GPS co-orinates via UART. For handling data precission, it uses **mpy_decimal** package - The details of which can be found on github at  **https://github.com/mpy-dev/micropython-decimal-number/tree/main/mpy_decimal**

There are two classes in this library.

a) **GPS**
GPS class is used to initialize the GPS object - It requires a uart object and optionally (timeout and satprecission)

timeout -> The maximum time to wait to successfully identify the current GPS coordinate.

satprecission -> The minimum number of fix satellites that is acceptable to identify the GPS coordinate.

Example Usage: 

uart=machine.UART(0, 9600, tx=machine.Pin(16), rx=machine.Pin(17), bits=8, parity=None, stop=1, timeout=300)

g = GPS(uart, timeout=300, satprecission=2)

c = g.getCurrentGPSLocation()

The method getCurrentGPSLocation() returns GPSCordinates object - Before using, ensure it has all valid data by invoking isValid method.

if c.isValid():

 	 print(c.getLatitude())

 	 print(c.getLongitude())
  
	  print(c.getSpeed())
  
	  print(c.getAltitude())

b) **GPSCordinates**
This class encapsulates the captured GPS coordinates. Use the getter methods

getLatitude

getLatDirection

getLongDirection

getLongitude

getAltitude

getAltitudeUnit

getNumSats

getSpeed

getCurrentTime

isValid
