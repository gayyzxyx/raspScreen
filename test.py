#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
if __name__=="__main__":
    container = strContainer(0,14,6)
    container.handelLines('''192.168.2.5\n192.168.1.105''')
    container.addLine("xxxxxxxxxxxxxxx")
    container.addLine("vvvvvvvv")
    print container.outStr()