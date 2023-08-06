from __future__ import print_function

import sys
import afl
import os
import struct
import random

# Appending current working directory to sys.path
# So that user can run randomtester from the directory where sut.py is located
current_working_dir = os.getcwd()
sys.path.append(current_working_dir)

import sut as SUT

def makeInt(s):
    try:
        return int(s)
    except:
        return None


def main():

    sut = SUT.sut()
    saveFile = "aflfail." + str(os.getpid()) + ".test"
    
    try:
        sut.stopCoverage()
    except:
        pass

    sut.restart()

    if "--swarm" in sys.argv:
        swarm = True
        R = random.Random()
    else:
        swarm = False
    showActions = "--showActions" in sys.argv
    if "--verbose" in sys.argv:
        sut.verbose(True)
    noSave = "--noSave" in sys.argv
    noCheck = "--noCheck" in sys.argv
    bytes = 2
    fmt = "<H"
    if "--32" in sys.argv:
        bytes = 4
        fmt = "<L"
    if "--64" in sys.argv:
        bytes = 8
        fmt = "<Q"

    afl.init()

    bytesin = sys.stdin.read()

    if len(bytesin) < 4:
        os._exit(0)        

    if swarm:
        R.seed(struct.unpack(">L",bytesin[0:4]))
        sut.standardSwarm(R)
        bytesin = bytesin[4:]

    alen = len(sut.actions())

    test = []
    for i in range(0,len(bytesin)/bytes):
        test.append(struct.unpack(fmt,bytesin[i:i+bytes])[0] % alen)
    
    for s in test:
        a = sut.actions()[s]
        if a[1]():
            if showActions:
                print (a[0])
            ok = sut.safely(a)
            if (not noSave) and not ok:
                sut.saveTest(sut.test(),saveFile)
            assert(ok)
            if not noCheck:
                checkResult = sut.check()
                if (not noSave) and not checkResult:
                    sut.saveTest(sut.test(),saveFile)            
                assert(checkResult)
            
    os._exit(0)
