import machine
from machine import UART, Pin
from time import sleep
from binascii import hexlify

tile = UART(2, 115200)
led = Pin(13, Pin.OUT)

gpsPoll = ""
timePoll = ""


def readSerial():
    received = tile.read(800)
    if received is not None:
        data_string = ''.join([chr(b) for b in received])
        print(data_string, end='')
        print('\n')
        return data_string

def makeTileCmd(cmd):
    cbytes = cmd
    cs = 0
    for c in cbytes[1:]:
        cs = cs ^ c
    return cbytes + b'*%02X\n'%cs

def getTime():
    global timePoll
    customWhile = 1
    countLoop = 0
    while customWhile !=0 :
        tile.write(b'$DT @*70\n')
        sleep(1)
        serialData = readSerial()
        serialData1 = str(serialData)
        countLoop = countLoop + 1
        print("Loading Time.......", str(countLoop))
        if len(serialData1) > 20 and len(serialData1) < 25:
            customWhile = 0
        if countLoop == 100:
            machine.deepsleep(300000)
    if serialData is not None:
        parse = serialData[:-3].split(' ')
        if parse[0] == '$DT':
            dateTime = parse
            dateTime = dateTime[1].split(',')
            dateTime = dateTime[0].split('\n')
            dateTimeString = [str(dateTime) for dateTime in dateTime]
            dateTimeStringJoin = "".join(dateTimeString)
            timePoll = dateTimeStringJoin[2:12]
            print(timePoll)

def getGps():
    global gpsPoll
    customWhile = 1
    c = 0
    print(customWhile)
    while customWhile !=0:
        tile.write(b'$GN @*69\n')
        sleep(1)
        serialData = readSerial()
        serialData1 = str(serialData)
        c = c + 1
        print("Loading GPS......... " + str(c) )
        if len(serialData1)> 30:
            #print("Get GPS")
            customWhile = 0
        if c == 100:
            machine.deepsleep(300000)

    if serialData is not None:
        parse = serialData [:-3].split(' ')
        if parse[0] == '$GN':
            gps = parse
            gps = gps[1].split(',')
            #gps = gps[1].split('\n')
            intLong = float(gps[0])
            intLat = float(gps[1])
            longSend = int(intLong * 10000)
            latSend = int(intLat * 10000)
            gpsFull = '{}{}'.format(longSend, latSend)
            gpsJoin = "".join(gpsFull)
            gpsPoll = gpsJoin
            print(gpsPoll)

def sendData():
    try:
        dataString = '{}{}'.format(timePoll, gpsPoll)
        tdCommand = b'$TD '+ hexlify(dataString.encode())
        print(tdCommand)
        #tile.write(b'$MT C=U*12\n')
        sleep(1)

        nmeaString = makeTileCmd(tdCommand)
        print(nmeaString)
        tile.write(nmeaString)
        sleep(1)

    except RuntimeError as error:
        print(error.args[0])
        sleep(2)
    except Exception as error:
        raise error

def timeDeepsleep():
    ow = 60
    menit_interval = int(ow)
    tile.write(b'$DT @*70\n')
    sleep(1)
    serialData = readSerial()
    parse = serialData[:-3].split(' ')
    if parse[0] == '$DT':
        dateTime = parse
        dateTime = dateTime[1].split(',')
        dateTime = dateTime[0].split('\n')
        dateTimeString = [str(dateTime) for dateTime in dateTime]
        dateTimeStringJoin = "".join(dateTimeString)
        menit_end = int(dateTimeStringJoin[10:12])
        #detik_end = int(dateTimeStringJoin[12:14])
    if menit_interval >= 60:
        ds = int((menit_interval-menit_end)*(60000))
    else:
        ds =int(menit_interval*60000)

    print("deepsleep..."  , str(ds/60000), " minutes")
    machine.deepsleep(ds)

def main():
    while True:
        sleep(20)
        getTime()
        getGps()
        sendData()
        timeDeepsleep()

#tile.write(b'$DT 0*00\n')
#tile.write(b'$RT 0*16\n')
#tile.write(b'$GN 0*19\n')
#tile.write(b'$GJ 0*1D\n')
#tile.write(b'$GS 0*04\n')

main()
