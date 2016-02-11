# All these algorithms are from 
# http://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
def calcTmp(ambT, objT):
    SCALE_LSB = 0.03125
    it = int(objT >> 2)
    tObj = float(it)*SCALE_LSB
    it = int(ambT >> 2)
    m_tmpAmb = float(it)*SCALE_LSB
    return (m_tmpAmb, tObj)

def calcHum(rawT, rawH):
    temp = -40 + 165.0/65536.0 * rawT # [deg C]
    hum = (float(rawH)/65536) * 100  # [%RH]
    return (temp, hum)

def calcBaro(rawPr):
    pr = rawPr/100.0
    return (pr)

def calcLight(rawL):
    m = rawL & 0x0FFF
    e = (rawL & 0xF000) >> 12
    return (m*(0.01*pow(2.0,e)))
	
	
