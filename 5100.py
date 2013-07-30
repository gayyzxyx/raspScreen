#!/user/bin/python
import threading
import time
import nokiaSPI
import commands
import psutil
import string

class timer(threading.Thread):
    def __init__(self,num,interval):
        threading.Thread.__init__(self)
        self.thread_num = num  
        self.interval = interval  
        self.thread_stop = False  

    def run(self):
        while not self.thread_stop:
            nokia.cls()
            nokia.led(0)
            ipAdd = getIp()
            tempurature = getTempurature()
            cpu = getCpuUseage()
            mem = getMem()
            strList = strContainer(0,14,6)
            strList.handelLines(ipAdd)
            strList.addLine("thermal:"+tempurature)
            strList.addLine(cpu)
            strList.addLine(mem)
            strList.addLine(getUpTime())
            #nokia.text(ipAdd+" thermal:"+tempurature+" "+cpu+"     "+mem)
            nokia.text(strList.outStr())
            time.sleep(self.interval)

    def stop(self):
        self.thread_stop = True

class strContainer():
    def __init__(self,start,eachLineCharCount,screenLineCount):
        self.lineCount = 0
        self.str = ''
        self.strList = []
        self.lineStart = start
        self.eachLineCharCount = eachLineCharCount
        self.screenLineCount = screenLineCount

    def addLine(self,str):
        lineLength = len(str)
        blanks = ""
        if lineLength%self.eachLineCharCount != 0:
            for i in range(self.eachLineCharCount-(lineLength%self.eachLineCharCount)):
                blanks += " "
        self.lineCount += (len(str)/(self.eachLineCharCount+1) + 1)
        self.strList.append(str + blanks)

    def addStr(self,str):
        self.strList[len(self.strList)-1] = self.strList[len(self.strList)-1] + str
        self.lineCount = (len(str)+len(self.strList[len(self.strList)-1]))/(self.eachLineCharCount + 1) + 1

    def outStr(self,start = 0):
        for list in self.strList:
            self.str += list
        if self.lineCount <= self.screenLineCount:
            return self.str
        else:
            endindex = start+self.screenLineCount*self.eachLineCharCount if start+self.screenLineCount*self.eachLineCharCount <= len(self.str) else len(self.str)
            return self.str[start*self.eachLineCharCount:endindex]

    def handelLines(self,str):
        if str.find('\n'):
            for s in str.split('\n'):
                self.addLine(s)
        else:
            self.addLine(str)
def getIp():
    ipAdd = commands.getstatusoutput("ifconfig|grep 'inet addr:'|grep -v '127.0.0.1'|awk '{print $2}'|awk -F':' '{print $2}'")[1]
    return ipAdd

def getTempurature():
    tempurature = str(string.atoi(commands.getstatusoutput("cat /sys/class/thermal/thermal_zone0/temp")[1])/1000.0)
    return tempurature

def getCpuUseage():    
    cpu = "cpu:"+str(psutil.cpu_percent(0.1))+"%"
    return cpu

def getMem():
    phymem = psutil.phymem_usage()
    buffers = getattr(psutil, 'phymem_buffers', lambda: 0)()  
    cached = getattr(psutil, 'cached_phymem', lambda: 0)()  
    used = phymem.total - (phymem.free + buffers + cached)  
    line = "Mem:%s/%s" % (  
        str(int(used / 1024 / 1024)) + "M",  
        str(int(phymem.total / 1024 / 1024)) + "M"  
    )
    return line

def getUpTime():
    time = commands.getstatusoutput("uptime|awk -F',' '{print $1}'|awk '{print $3}'")[1]
    return time

if __name__=="__main__":
    nokia = nokiaSPI.NokiaSPI(contrast=0xb6)
    thread1 = timer(1,5)
    thread1.start()

        
