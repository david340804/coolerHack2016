from time import sleep
import serial
import pymysql
import datetime

ser = serial.Serial('/dev/ttyACM0',9600)


class calibrateCan():
    def __init__(self,db,cursor,productName,redScan,blueScan,greenScan):
        self.rbScan = 0
        self.rgScan = 0
        self.bgScan = 0
        self.wScan = 0

        self.productName = productName
        self.redScan = redScan
        self.blueScan = blueScan
        self.greenScan = greenScan
        
        self.db = db
        self.cursor = cursor
        
        self.calibrateCanA()
        
    def calibrateCanA(self):
        sql = '''SELECT productID FROM coolerhack.producttable WHERE productName = %s'''
        c = self.cursor.execute(sql,(self.productName))
        
        if c<1:
            sql = '''INSERT INTO coolerhack.producttable (productName) VALUES (%s)'''
            self.cursor.execute(sql,(self.productName))
            self.db.commit()
            self.calibrateCanA()
        else:
            line = cursor.fetchone()
            self.productID = line[0]
            self.calibrateCanB()

    def calibrateCanB(self):
        sql = '''INSERT INTO coolerhack.knownproducts (productID,productName,
        redScan,blueScan,greenScan,rbScan,bgScan,rgScan,wScan) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        #print(self.cursor.fetchone())
        self.cursor.execute(sql,(int(self.productID),self.productName,self.redScan,self.blueScan,self.greenScan,self.rbScan,self.bgScan,self.rgScan,self.wScan))
        self.db.commit()
        
def formatStream(val):
    plotStream = (float(val-plotStreamRange[0])/float(plotStreamRangeW))
    plotStream = int(plotStream * plotStreamWidth)
    
    return plotStream


plotStreamRange = [950,1024]
plotStreamRangeW = plotStreamRange[1] - plotStreamRange[0]
plotStreamWidth = 30
plotStreamChar = "|"


db = pymysql.connect(db="coolerHack",user="zzzzzzzzzz",passwd="zzzzzzzzzzzzzz",host='''zzzzzzzzzzzzzzzzzzzzz''')
cursor = db.cursor()
#empty read to let the serial synchronize
ser.readline()
ser.flushInput()
ser.flushOutput()
#wait for serial
sleep(0.5)
#say hey
print("starts runing")

dataList = []

productName = raw_input("What is this product called?\n")
print("\n")

for i in range(50):
    #serial line reading limits the rate
    ser.flushInput()
    ser.flushOutput()
    line = ser.readline()

    red = int(line[line.index("r: ")+3:line.index("g: ")])
    green = int(line[line.index("g: ")+3:line.index("b: ")])
    blue = int(line[line.index("b: ")+3:line.index("row: ")])
    rowData = int(line[line.index("row: ")+5:line.index("\r\n")])

#    print(str(rowData).ljust(5)+"* "+toPlotStream(red)+toPlotStream(green)+toPlotStream(blue))

    #exaggerate like the visualization
    red = formatStream(red)
    green = formatStream(green)
    blue = formatStream(blue)

    print(red,green,blue)
    


###############################
###THIS SHIT IS BIG
    
#    productName = raw_input("What is this product called?\n")
#    print("\n")

###############################

    redScan = red
    blueScan = blue
    greenScan = green
    #throw the janky initial data
    if i > 25:
        dataList.append([red, green, blue])
    #    calibrateCan(db,cursor,productName,redScan,blueScan,greenScan)
#    print("sample " + str(i) + " taken")
    sleep(.05)


#send the data
   
aBool = raw_input("Save Data for " + productName+ "? y/n\n")
aBool = aBool == "y"
print(aBool)
if aBool:
    print("sending fingerprint data for " + productName + "...")
    for i in dataList:
        calibrateCan(db,cursor,productName,i[0],i[2],i[1])
    print("fingerprint data sent!")
    
else:
    print("Well fuck... No data sent")


#close connection
db.commit()
cursor.close()
db.close()
