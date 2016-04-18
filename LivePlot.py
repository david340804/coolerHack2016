from time import sleep
import serial

ser = serial.Serial('/dev/ttyACM0',9600)

def toPlotStream(val):
    plotStream = (float(val-plotStreamRange[0])/float(plotStreamRangeW))
    plotStream = int(plotStream * plotStreamWidth)
    plotStream = plotStreamChar * plotStream
    plotStream = plotStream.ljust(plotStreamWidth)
    
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

t = 0

while True:
    try:
        #serial line reading limits the rate
        line = ser.readline()

        red = int(line[line.index("r: ")+3:line.index("g: ")])
        green = int(line[line.index("g: ")+3:line.index("b: ")])
        blue = int(line[line.index("b: ")+3:line.index("row: ")])
        rowData = int(line[line.index("row: ")+5:line.index("\r\n")])

        #convert the resistance value to number of cans
        numCans = getNumCans(rowData);
        
        print(red,green,blue)
        print(str(numCans).ljust(5)+"* "+toPlotStream(red)+toPlotStream(green)+toPlotStream(blue))
    except ValueError:
        print("Serial went too fast, flushing buffer before continuing...")
    t += 1
    sleep(.05)

