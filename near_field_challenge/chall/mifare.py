#!/usr/bin/env python

import smartcard.System
import smartcard.util
import smartcard.CardConnection
import sys

DEFAULT_KEYA = 'FFFFFFFFFFFF'

class CardNotFoundError(Exception):
    pass


class MIFARE:
    def __init__(self):
        self.smartCardReader = self.GetSmartCardReader()
        if str(self.smartCardReader) == '':
            print 'No ACS ACR122 reader found'
            exit()
        self.KeyBlockNumber = None

    def GetSmartCardReader(self):
        """
           If only one reader connected, return that reader.
           If more than one reader is connected, return the first reader with the string ACR122"""
           
        readers = smartcard.System.readers()
        if len(readers) == 1:
            return readers[0]
        elif len(readers) == 0:
            return ''
        else:
            for r in readers:
                if str(r).upper().find('ACR122') > -1:
                    return r
            print 'Error selecting reader, readers: %s' % readers
            return ''

    def TransmitCommand(self, command):
        data, sw1, sw2 = self.connection.transmit(command, protocol=smartcard.CardConnection.CardConnection.T1_protocol)
        if sw1 != 0x90 or sw2 != 0x00:
            print 'sw1, sw2 = %02x %02x' % (sw1, sw2)
            print 'data     = ' + smartcard.util.toHexString(data)
            return None
        else:
            return data

    def Connect(self):
        self.connection = self.smartCardReader.createConnection()
        self.connection.connect()

    def Disconnect(self):
        self.connection.disconnect()

    def _WaitForTag(self):
        self.connection = self.smartCardReader.createConnection()
        loop = True
        while loop:
            try:
                self.connection.connect()
                loop = False
            except:
                pass
        self.connection.disconnect()

    def Poll(self, try_=0):
        if try_ > 3:
            print "Error, retry"
            exit()
        data = self.TransmitCommand(smartcard.util.toBytes('FF00000004D44A0100'))
        if data != None:
            try:
                self.tag_number = data[2]
                self.target_number = data[3]
                self.sens_res = data[4:6]
                self.sel_res = data[6]
                self.uid_length = data[7]
                self.uid_value = data[8:]
            except:
                self.Poll(try_ + 1)

    def KeyA(self, block, key=DEFAULT_KEYA):
        APDU = smartcard.util.toBytes('FF000000')
        APDU.append(11 + self.uid_length)
        APDU += smartcard.util.toBytes('D440')
        APDU.append(self.target_number)
        APDU.append(0x60) # 0x61 for key B
        APDU.append(block)
        APDU += smartcard.util.toBytes(key)
        APDU += self.uid_value
        data = self.TransmitCommand(APDU)
        if data != None:
            return data[2]
        else:
            print 'Error keyA:'
            return -1
            
    def PrepareKeyA(self, block, key):
        if self.KeyBlockNumber == None:
            self.KeyA(block, key)
            self.KeyBlockNumber = block
        elif self.KeyBlockNumber / 4 != block / 4:
            self.KeyA(block, key)
            self.KeyBlockNumber = block

    def ReadBlock(self, block, key=DEFAULT_KEYA):
        self.PrepareKeyA(block, key)
        APDU = smartcard.util.toBytes('FF00000005D440')
        APDU.append(self.target_number)
        APDU.append(0x30)
        APDU.append(block)
        data = self.TransmitCommand(APDU)
        if data != None:
            return data[3:]
        else:
            return []
    
    def WriteBlock(self, block, values, key=DEFAULT_KEYA):
        self.PrepareKeyA(block, key)
        APDU = smartcard.util.toBytes('FF00000015D440')
        APDU.append(self.target_number)
        APDU.append(0xA0)
        APDU.append(block)
        APDU += values
        data = self.TransmitCommand(APDU)
        if data != None:
            return data[2]
        else:
            print 'Error write:'
            return -1
    
    def ID(self):
        self.Connect()
        self.Poll()
        self.Disconnect()

    def _Dump(self):
        self.Connect()

        data = []
        
        self.Poll()
        for block in range(1024 / 16): # MIFARE 1K
            data += self.ReadBlock(block)
        
        self.Disconnect()

        return data

    def _DumpWritable(self):
        self.Connect()

        data = []
        
        self.Poll()
        for block in range(1, 1024 / 16): # MIFARE 1K
            if (block+1) % 4 != 0:
                data += self.ReadBlock(block)
        
        self.Disconnect()
        
        return data

    def _WriteSequence(self, sequence, key=DEFAULT_KEYA):
        self.Connect()

        self.Poll()
        rest = sequence
        for block in range(1, 1024 / 16): # MIFARE 1K
            if (block+1) % 4 != 0:
                if len(rest) >= 16:
                    values = rest[0:16]
                    rest = rest[16:]
                else:
                    values = rest
                    rest = []
                    if len(values) > 0:
                        values += [0] * (16 - len(values))
                if len(values) > 0:
                    self.WriteBlock(block, values, key)

        self.Disconnect()
        
    def _Wipe(self):
        self._WriteSequence([0] * (16 * (16 * 3 - 1)))

    def wipe(self):
        self._WaitForTag()
        self._Dump()
        self._Wipe()
        self._DumpWritable()

    def read(self):
        self._WaitForTag()
        data = self._DumpWritable()
        return ''.join([chr(i) for i in data])

    def write(self, data):
        self._WriteSequence([0] * (16 * (16 * 3 - 1)))
        self._WaitForTag()
        self._WriteSequence([ord(c) for c in data])

if __name__ == '__main__':
    mifare = MIFARE()
    
    print "Read card : %s" % mifare.read()
    # Write card

    payload = "FOOBAR"
    print "Write : %s" % payload
    mifare.write(payload)

    # Read card content
    print "Read card : %s" % mifare.read()
