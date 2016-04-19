from __future__ import print_function
from time import sleep
from coolerClass.filecfg import filecfg
import serial
import pymysql
import datetime

#get configuration info from cfg file
cfg = filecfg('config.cfg')

#initialise the serial connection
ser = serial.Serial(cfg.ser_interface,9600)

#empty read to let the serial synchronize
ser.readline()

class upload():
    def __init__(self,db,cursor,machineID,rowNum,redScan,greenScan,blueScan,numCans):
        #set up attributes
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

#convert raw rgb intensity into weighted and scaled values
def formatStream(val):
    plotStream = (float(val-plotStreamRange[0])/float(plotStreamRangeW))
    plotStream = int(plotStream * plotStreamWidth)
    
    return plotStream

#convert rowData raw resistance read into the number of cans
def getNumCans(rowData):
    numCans = 0;
    if rowData < 30:
        numCans = 0;
    elif rowData < 41:
        numCans = 6;
    elif rowData < 53:
        numCans = 5;
    elif rowData < 68:
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

#config data for formatStream
plotStreamRange = [950,1024]
plotStreamRangeW = plotStreamRange[1] - plotStreamRange[0]
plotStreamWidth = 30
plotStreamChar = "|"

#set up database connection
db = pymysql.connect(db=cfg.db_db,user=cfg.db_user,passwd=cfg.db_passwd,host=db_host)
cursor = db.cursor()

#wait a sec for connections
sleep(0.5)

#Junk data trials to skip while sensor data stabilizes
junkTrials = 15;

for i in range(100):
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

        #print raw sensor data if the junkTrials are done, otherwise just rgb vals
        if i > junkTrials:
            print("rowData:"+str(rowData).ljust(4)+"\t("+str(red)+","+str(green)+","+str(blue)+")\t",end="")
        else:
            print(str(i).ljust(3),"rowData:",rowData,red,green,blue)
        machineID = 0
        rowNum = 1
        redScan = red
        greenScan = green
        blueScan = blue

        #log the events to the main database
        if i > junkTrials:
            upload(db,cursor,machineID,rowNum,redScan,greenScan,blueScan,numCans)
    except ValueError:
        #caught partial data from serial mismatch
        print("Serial went too fast, flushing before resuming...")
    sleep(0.05)

#clean up
db.close()
cursor.close()






