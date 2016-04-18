from time import sleep
import serial
import pymysql
import datetime


ser = serial.Serial('/dev/ttyACM0',9600)

#empty read to let the serial synchronize
ser.readline()

class upload():
    def __init__(self,db,cursor,machineID,rowNum,redScan,greenScan,blueScan,numCans):
        self.db = db
        self.cursor = cursor
        self.dataTime = str(datetime.datetime.now())
        self.machineID = 0
        self.rowNum = 1
        self.rbScan = 0
        self.rgScan = 0
        self.bgScan = 0
        self.wScan = 0
        self.redScan = redScan
        self.blueScan = blueScan
        self.greenScan = greenScan
        self.numCans = numCans
        self.identifyCan()

    def identifyCan(self):
        sql = '''select productID,productName,abs(redScan-%s) as rDiff,
        abs(blueScan-%s) as bDiff,abs(greenScan-%s) as
        gDiff,abs(rbScan-%s) as rbDiff,abs(bgScan-%s)
        as bgDiff,abs(rgScan-%s) as rgDiff,abs(wScan-%s)
        as wDiff,abs(redScan-%s) + abs(blueScan-%s) +
        abs(greenScan-%s) + abs(rbScan-%s) + abs(bgScan-%s) +
        abs(rgScan-%s) + abs(wScan-%s) as totalDiff from knownproducts
        order by (abs(redScan-%s) + abs(blueScan-%s) + abs(greenScan-%s) +
        abs(rbScan-%s) + abs(bgScan-%s) + abs(rgScan-%s) + abs(wScan-%s))'''

        self.cursor.execute(sql,(self.redScan,self.blueScan,self.greenScan,self.rbScan,
        self.bgScan,self.rgScan,self.wScan,self.redScan,self.blueScan,self.greenScan,self.rbScan,
        self.bgScan,self.rgScan,self.wScan,self.redScan,self.blueScan,self.greenScan,self.rbScan,
        self.bgScan,self.rgScan,self.wScan))

        line=self.cursor.fetchone()
        print("numCans:" + str(numCans) + " " + str(line))
        self.canID = line[0]
        self.canName = line[1]
        self.uploadToDB()

    def uploadToDB(self):
        sql = '''INSERT INTO coolerhack.main (machineID,rowNum,dataTime,numCans,firstCanID,firstCanName) VALUES (%s,%s,%s,%s,%s,%s)'''
        self.cursor.execute(sql,(self.machineID,self.rowNum,self.dataTime,self.numCans,self.canID,self.canName))
        self.db.commit()
        db.commit()

def formatStream(val):
    plotStream = (float(val-plotStreamRange[0])/float(plotStreamRangeW))
    plotStream = int(plotStream * plotStreamWidth)
    
    return plotStream

def getNumCans(rowData):
    numCans = 0;
    if rowData < 30:
        numCans = 0;
    elif rowData < 40:
        numCans = 6;
    elif rowData < 50:
        numCans = 5;
    elif rowData < 60:
        numCans = 4;
    elif rowData < 100:
        numCans = 3;
    elif rowData < 180:
        numCans = 2;
    elif rowData < 360:
        numCans = 1;
    else:
        numCans = 0;
    
    return numCans


plotStreamRange = [950,1024]
plotStreamRangeW = plotStreamRange[1] - plotStreamRange[0]
plotStreamWidth = 30
plotStreamChar = "|"
        
db = pymysql.connect(db="coolerHack",user="aaaaaaaaaaaaa",passwd="aaaaaaaaaa",host='''aaaaaaaaaaaaaaaaaaaaaaaaaa''')
cursor = db.cursor()
sleep(0.5)


for i in range(75):
    try:
        #serial line reading limits the rate
        ser.flushInput()
        ser.flushOutput()
        line = ser.readline()
        
        red = int(line[line.index("r: ")+3:line.index("g: ")])
        green = int(line[line.index("g: ")+3:line.index("b: ")])
        blue = int(line[line.index("b: ")+3:line.index("row: ")])
        rowData = int(line[line.index("row: ")+5:line.index("\r\n")])
        
        #exaggerate like the visualization
        red = formatStream(red)
        green = formatStream(green)
        blue = formatStream(blue)

        #Process rowData into NumCans
        numCans = getNumCans(rowData)
        
        print(red,green,blue)
#        numCans = 0
        machineID = 0
        rowNum = 1
        redScan = red
        greenScan = green
        blueScan = blue

        if i > 25:
            upload(db,cursor,machineID,rowNum,redScan,greenScan,blueScan,numCans)
    except ValueError:
        print("Serial went too fast, flushing before resuming...")
    sleep(0.05)

db.close()
cursor.close()






