import time
from machine import Pin
from machine import UART
from mpy_decimal import *


class GPSCordinates:
    
    latitude = -1
    latDirection = ""
    longitude = -1
    longDirection = ""
    currenttime = -1
    altitude = -1
    altitudeunit = ""
    speed = -1
    numsats = 0
    satprecission = 0
    
    def __init__(self, satprecission=1):
        self.satprecission = satprecission

    def doMath(self, data, direction):
        if data == -1 or direction == '':
            return None
        
        number = DecimalNumber(data)
        number = number/100
        
        degWhole = number.to_int_truncate()
        rem = (number - degWhole)*100/60
        deg = degWhole + rem
        
        if direction == "W" or direction == "S":
            deg = deg * -1
        
        strd = str(deg)
        
        try:
            index = strd.index('.')
            num = strd[0:index+5]
            return num
        except ValueError:
            print(strd)
            i = strdeg.index(".")
            return deg

    def __str__(self):
        print("Satellites :", self.numsats, "\nCurrent Time : ", self.currenttime, "\nLatitude : ", self.doMath(self.latitude, self.latDirection) , "(", self.latDirection , ")\nLongitude : ", self.doMath(self.longitude, self.longDirection), "(", self.longDirection, ")", "\nAltitude : ", self.altitude, "(", self.altitudeunit, ")", "\nSpeed : ", self.speed) 
    
    def setLatitude(self, latitude):
        self.latitude = latitude
    
    def getLatitude(self):
        result = self.doMath(self.latitude, self.latDirection)
        return result
    
    def setLatDirection(self, latDirection):
        self.latDirection = latDirection
    
    def getLatDirection(self):
        return self.latDirection

    def setLongDirection(self, longDirection):
        self.longDirection = longDirection
    
    def getLongDirection(self):
        return self.longDirection
    
    def setLongitude(self, longitude):
        self.longitude = longitude
        
    def getLongitude(self):
        result = self.doMath(self.longitude, self.longDirection)
        return result
    
    def getAltitude(self):
        return self.altitude
    
    def setAltitude(self, altitude):
        self.altitude = altitude
        
    def getAltitudeUnit(self):
        return self.altitudeunit

    def setAltitudeUnit(self, altitudeunit):
        self.altitudeunit = altitudeunit
        
    def setSpeed(self, speed):
        self.speed = speed
        
    def getNumSats(self):
        return self.numsats
    
    def setNumSats(self, numsats):
        self.numsats = numsats
    
    def getSpeed(self):
        return self.speed
        
    def setCurrentTime(self, currenttime):
        self.currenttime = currenttime
    
    def getCurrentTime(self):
        return self.currenttime;
    
    def isValid(self):
        if self.latitude == -1 or self.longitude == -1 or self.currenttime == -1 or self.latDirection == "" or self.longDirection == "" or self.altitude == -1 or self.altitudeunit == '' or self.speed == -1 or int(self.numsats) < self.satprecission :
            return False
        else:
            return True
    
 

# Create a GPS object
class GPS:
    lastgpslocation = None
    satprecission = None
    def __init__(self, uart, timeout=10, satprecission=3):
        self.uart = uart
        self.timeout = timeout
        self.satprecission = satprecission
        print("Initializing UART with ", uart)
        print("Using timeout ", timeout," seconds")
    
    # Returns last good known GPS location
    def getLastGPSLocation(self):
        return self.lastgpslocation
    
    # Returns current GPS Location
    # Note - Use isValid on the GPSCordinates object before consuming
    def getCurrentGPSLocation(self):
        if self.uart != None:
            result = GPSCordinates(self.satprecission)
            endtime = time.time() + self.timeout
            
            # Attempt to get current GPS location within the timeout
            try:
                while True:
                    curTime = time.time()
                    if(curTime > endtime or result.isValid() == True):
                        break
                    nmealinebytes = uart.readline()
                    if nmealinebytes == None:
                        time.sleep(0.5)
                        continue
                    # Convert byte received via readline to str
                    try:
                        nmealinestr = nmealinebytes.decode('utf-8')
                    except UnicodeError as error:
                        print("Error occured.. Will re-try in 3 seconds")
                        time.sleep(3)
                        continue
                    
                    
                    # Interested only in $GPGGA, $GPRMC and $GPVTG
                    if nmealinestr.startswith("$GPGGA") or nmealinestr.startswith("$GPRMC") or nmealinestr.startswith("$GPVTG"):
                        #print(nmealinestr)
                        data = nmealinestr.split(",")
                        if data[0] == "$GPGGA":
                            # Check Quality - If it is zero, no point in checking the rest of the data
                            quality = data[6]
                            if quality == 0:
                                continue
                            
                            curtime = data[1]
                            lat = data[2]
                            latdir = data[3]
                            long = data[4]
                            longdir = data[5]
                            numsats = data[7]
                            # Altitude available only for $GPGGA entry
                            altitude = data[9]
                            altitudeunit = data[10]
                            
                            result.setLatitude(lat)
                            result.setLongitude(long)
                            result.setCurrentTime(curtime)
                            result.setLongDirection(longdir)
                            result.setLatDirection(latdir)
                            result.setAltitude(altitude)
                            result.setAltitudeUnit(altitudeunit)
                            result.setNumSats(numsats)
                        elif data[0] == "$GPRMC":
                            position_status = data[2]
                            if position_status != 'A':
                                continue
                            
                            curtime = data[1]
                            lat = data[3]
                            latdir = data[4]
                            long = data[5]
                            longdir = data[6]
                            # Speed available only for $GPRMC entry
                            speed = data[7]
                            result.setLatitude(lat)
                            result.setLongitude(long)
                            result.setCurrentTime(curtime)
                            result.setLongDirection(longdir)
                            result.setLatDirection(latdir)
                            #result.setSpeed(speed)
                        else:
                            speed = data[7]
                            result.setSpeed(speed)
            except KeyboardInterrupt:
                    print("Terminating..")
            return result
        else:
           return GPSCordinates()


uart=machine.UART(0, 9600, tx=machine.Pin(16), rx=machine.Pin(17), bits=8, parity=None, stop=1, timeout=300)
g = GPS(uart, timeout=300, satprecission=2)
c = g.getCurrentGPSLocation()
print(c.isValid())
if c.isValid():
    print(c.getLatitude())
    print(c.getLongitude())
    print(c.getSpeed())
    print(c.getAltitude())




        