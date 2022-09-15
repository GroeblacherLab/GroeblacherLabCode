# -*- coding: utf-8 -*-
"""

@author: B. Platzer, N. Fiaschi

This work is licensed under the GNU Affero General Public License v3.0

Copyright (c) 2021, GroeblacherLab
All rights reserved.


___________________________________________________________________________________________________


This driver controls the mechonics stage MX35 via the USB controller CU30.

___________________________________________________________________________________________________

HOW TO USE THE CODE:

    1. Connect the controller CU30 via USB to the computer
    2. Get the absolute path of CU30_Wrapper_DLL_x64_C++/bin/CU30Wrap.dll


----------- example of usage, open connection and move in x and y direction: ----------

    mechonics = Mechonics()
    mechonics.open_connection()
    mechonics.sweep(Timeout = 100)
    time.sleep(2)
    mechonics.sweep(Axis=2)
    time.sleep(2)
    mechonics.close_connection()
    
---------------------------------------------------------------------------------------

TDB:
    - get_EEprom_info, does not return the info
    - get the connection result (success or not) from open_connection
    
tested with Spyder 4, Python 3.7, Windows 10 and ctypes 0.2.0
"""

import ctypes 
import time


class Mechonics:
    
    def __init__(self, path = "XXX\CU30Wrap.dll", USBInstance=0, USBVersion=1, DevID=1, EEID=0):
        """Initialisation. Loads the CU30Wrap.dll file containing the methods to control the device.
        The values for USBInstance etc. are given in the documentation pdf as an example, and we achieved a connection using these values.
        If no connection can be made, it may be helpful to try out different numbers.
        
        -CU30WrapperInit()
        The function performs initialization of the wrapper dll. It is either called automatically during the loading of the DLL into
        the memory or manually.
        """
        self.path = path
        self.CU30 = ctypes.windll.LoadLibrary(path)
        self.USBInstance = USBInstance
        self.USBVersion = USBVersion
        self.DevID = DevID
        self.EEID = EEID
        
        self.initialisation()
        
    def __enter__(self):
        """Method to allow the use of the with-as statement
        """
        return self
    
    def __exit__(self, type, value, traceback):
        """Method to allow the use of the with-as statement
        """
        self.close_connection()
        
    def initialisation(self):
        """
        """
        self.open_connection()
        
    def open_connection(self):
        """Opens the connection to the device, using the CU30WOpen() function saved in the .dll file. This function takes four pointers to DWORD-type objects as input.
        info from pdf:
        The function opens a connection to the hardware through the selected USB port. All the settings for the connection
        are collected in DeviceRec structure.
        """
        
        # initialise of which type the arguments and output of the function will be
        self.CU30.CU30WOpen.argtypes = [ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong)]
        self.CU30.CU30WOpen.restype = ctypes.c_char  # not sure about this one
        
        # call the function with 4 input arguments (ctypes.pointer creates a pointer to an object, c_ulong makes a DWORD)
        self.CU30.CU30WOpen(
            ctypes.pointer(ctypes.c_ulong(self.USBInstance)),
            ctypes.pointer(ctypes.c_ulong(self.USBVersion)), 
            ctypes.pointer(ctypes.c_ulong(self.DevID)), 
            ctypes.pointer(ctypes.c_ulong(self.EEID)) )
        
        print('Connected to the Mechonics stage')

        
    def sweep(self, Vel=-100, Axis=1, Timeout=20):
        """Move the stage. Info from documentation pdf:
        The function performs continuous movement along one of the axes. The movement could be stopped using
        CU30WStop() or adjusting the Timeout parameter. All the settings for the connection are collected in DeviceRec
        structure members, initialized during CU30WOpen() call.
        USBInstance, USBVersion, DevID, EEID – represent the corresponding fields of a DeviceRec structure,
        which contains the settings of the opened connection.
        Vel – Velocity of the movement; Vel = [-1000...-1, 1…+1000] , Vel = 0 => Vel = 1;
        Axis – Determines the axis of the movement (1 = X-Axis, 2 = Y-Axis, 3 = Z-Axis)
        Timeout – Determines the movement duration. Timeout = [2..255]
        If Timeout < 0, - the duration of the movement will be: Duration = 2 * 0.016 sec.
        If Timeout = 0, - the timeout will be disabled.
        If Timeout = 1, - the duration of the movement will be: Duration = 2 * 0.016 sec.
        If Timeout = [2…254], - the duration of the movement will be: Duration = Timeout * 0.016 sec.
        If Timeout > 254, - the timeout will be disabled.
        """
        
        # initialise types of input parameters (DWORD for usb info, int for movement commands)
        self.CU30.CU30WSweep.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.CU30.CU30WSweep.restype = None  # this function creates no output
        
        # call function
        self.CU30.CU30WSweep(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID),
            ctypes.c_int(Vel),
            ctypes.c_int(Axis),
            ctypes.c_int(Timeout) )
        
    def step(self, Axis=1, n=100, Vel=100):
        """Also to move the stage. Info from pdf:
        The function performs movement along one of the axes with a defined number of steps. The movement could be
        stopped using the subsequent call of CU30WStop(). All the settings for the connection are collected in DeviceRec 
        structure members, initialized during CU30WOpen() call.
        Parameters:
        USBInstance, USBVersion, DevID, EEID – represent the corresponding fields of a DeviceRec structure,
        which contains the settings of the opened connection.
        Axis – Determines the axis of the movement (1 = X-Axis, 2 = Y-Axis, 3 = Z-Axis)
        n – Determines the number of steps for the movement, n = [1… 1.000.000]
        If n < 1, - the number of steps for the movement will be: 1
        If n > 1.000.000 - the number of steps for the movement will be: 1.000.000
        Vel – Velocity of the movement; Vel = [-1000…-1, +1...+1000], Vel = 0 => Vel = 1;
        """
        
        # initialise types of input parameters (DWORD for usb info, int for movement commands)
        self.CU30.CU30WStep.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.CU30.CU30WStep.restype = None  # this function creates no output
        
        # call function
        self.CU30.CU30WStep(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID),
            ctypes.c_int(Axis),
            ctypes.c_int(n),
            ctypes.c_int(Vel) )
        
    def close_connection(self):
        """info from pdf:
        The function closes a connection to the hardware through the selected USB port, opened with previous call of
        CU30Open() function. All the settings for the connection are collected in DeviceRec structure members, initialized
        during CU30WOpen() call.
        
        -CU30WrapperDispose()
        The function releases all the memory and resources, allocated during work of the wrapper dll. It is called automatically
        when the dll is being removed from memory or it can be accessed manually.
        """
        
        # initialise types of input parameters (DWORD for usb info)
        self.CU30.CU30WClose.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
        self.CU30.CU30WClose.restype = None  # this function creates no output
        
        # call function
        self.CU30.CU30WClose(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID) )
        
    def stop_moving(self):
        """info from pdf:
        The function instantly terminates any movement of the selected hardware. All the settings for the connection are
        collected in DeviceRec structure members, initialized during CU30WOpen() call.
        """
        
        # initialise types of input parameters (DWORD for usb info)
        self.CU30.CU30WStop.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
        self.CU30.CU30WStop.restype = None  # this function creates no output
        
        # call function
        self.CU30.CU30WStop(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID) )
        
    def dcdc_on(self):
        """info from pdf:
        The function switches DCDC-converter on for the selected hardware. All the settings for the connection are collected
        in DeviceRec structure members, initialized during CU30WOpen() call.
        """
        
        # initialise types of input parameters (DWORD for usb info)
        self.CU30.CU30WDCDCon.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
        self.CU30.CU30WDCDCon.restype = None  # this function creates no output
        
        # call function
        self.CU30.CU30WDCDCon(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID) )
        
    def dcdc_off(self):
        """info from pdf:
        The function switches DCDC-converter on for the selected hardware. All the settings for the connection are collected
        in DeviceRec structure members, initialized during CU30WOpen() call.
        """
        
        # initialise types of input parameters (DWORD for usb info)
        self.CU30.CU30WDCDCoff.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
        self.CU30.CU30WDCDCoff.restype = None  # this function creates no output
        
        # call function
        self.CU30.CU30WDCDCoff(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID) )
        
    def get_EEprom_info(self): #still to be implemented
        """info from pdf:
        The function collects information about EEPROM and returns it in the output parameters. All the settings for the
        connection are collected in DeviceRec structuremembers, initialized during CU30WOpen() call.
        Parameters:
        USBInstance, USBVersion, DevID, EEID – represent the corresponding fields of a DeviceRec structure,
        which contains the settings of the opened connection.
        pUSBVendorID - pointer to a DWORD variable, where the vendor ID will be returned.
        pUSBProductID - pointer to a DWORD variable, where the product ID will be returned.
        pUSBDeviceID - pointer to a DWORD variable, where the USB device ID will be returned.
        pDeviceID - pointer to a DWORD variable, where the device ID will be returned.
        pEEPromID - pointer to a DWORD variable, where the EEPROM id will be returned.
        pVersion - pointer to a DWORD variable, where the version will be returned.
        pSerialNumber - pointer to a DWORD variable, where the serial number will be returned.
        pCustomerID - pointer to a DWORD variable, where the customer ID will be returned.
        pCompany - pointer to a string variable, where the company name will be returned. The size of the
        buffer must be at least 32 characters.
        pDate - pointer to a string variable, where the date will be returned. The size of the buffer must be
        at least 32 characters.
        pProductStr - pointer to a string variable, where the product name will be returned. The size of the
        buffer must be at least 32 characters.
        pCustomer - pointer to a string variable, where the customer name will be returned. The size of the
        buffer must be at least 32 characters.
        pCustomerStr - pointer to a string variable, where the customer string will be returned. The size of the
        buffer must be at least 32 characters.
        """
        
        self.CU30.CU30WGetEEpromInfo.argtypes = [
            ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, 
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_wchar),
            ctypes.POINTER(ctypes.c_wchar),
            ctypes.POINTER(ctypes.c_wchar),
            ctypes.POINTER(ctypes.c_wchar),
            ctypes.POINTER(ctypes.c_wchar)]
            
        
        class Output(ctypes.Structure):
            _fields_ = [
            ("pUSBVendorID", ctypes.POINTER(ctypes.c_ulong)),
            ("pUSBProductID", ctypes.POINTER(ctypes.c_ulong)),
            ("pUSBDeviceID", ctypes.POINTER(ctypes.c_ulong)),
            ("pDeviceID", ctypes.POINTER(ctypes.c_ulong)),
            ("pEEPromID", ctypes.POINTER(ctypes.c_ulong)),
            ("pVersion", ctypes.POINTER(ctypes.c_ulong)),
            ("pSerialNumber", ctypes.POINTER(ctypes.c_ulong)),
            ("pCustomerID", ctypes.POINTER(ctypes.c_ulong)),
            ("pCompany", ctypes.POINTER(ctypes.c_wchar)),
            ("pDate", ctypes.POINTER(ctypes.c_wchar)),
            ("pProductStr", ctypes.POINTER(ctypes.c_wchar)),
            ("pCustomer", ctypes.POINTER(ctypes.c_wchar)),
            ("pCustomerStr", ctypes.POINTER(ctypes.c_wchar))]
        
        self.CU30.CU30WGetEEpromInfo.restype = None
        
        # initialize saving spots for function output:
        pUSBVendorID = ctypes.c_ulong()
        pUSBProductID = ctypes.c_ulong()
        pUSBDeviceID = ctypes.c_ulong()
        pDeviceID = ctypes.c_ulong()
        pEEPromID = ctypes.c_ulong()
        pVersion = ctypes.c_ulong()
        pSerialNumber = ctypes.c_ulong()
        pCustomerID = ctypes.c_ulong()
        pCompany = ctypes.c_wchar()
        pDate = ctypes.c_wchar()
        pProductStr = ctypes.c_wchar()
        pCustomer = ctypes.c_wchar()
        pCustomerStr = ctypes.c_wchar()
        
        print("bla")
        print(pUSBVendorID.value)
        print(pUSBProductID.value)
        print(pUSBDeviceID.value)
        print(pDeviceID.value)
        print(pEEPromID.value)
        print(pVersion.value)
        print(pSerialNumber.value)
        print(pCustomerID.value)
        print(pCompany.value)
        print(pDate.value)
        print(pProductStr.value)
        print(pCustomer.value)
        print(pCustomerStr.value)
        
        self.CU30.CU30WGetEEpromInfo(
            ctypes.c_ulong(self.USBInstance),
            ctypes.c_ulong(self.USBVersion),
            ctypes.c_ulong(self.DevID),
            ctypes.c_ulong(self.EEID),
            ctypes.byref(pUSBVendorID),
            ctypes.byref(pUSBProductID),
            ctypes.byref(pUSBDeviceID),
            ctypes.byref(pDeviceID),
            ctypes.byref(pEEPromID),
            ctypes.byref(pVersion),
            ctypes.byref(pSerialNumber),
            ctypes.byref(pCustomerID),
            ctypes.byref(pCompany),
            ctypes.byref(pDate),
            ctypes.byref(pProductStr),
            ctypes.byref(pCustomer),
            ctypes.byref(pCustomerStr) )
        
        # print(out)
        # for att in dir(out):
        #     print (att, getattr(out,att))
            
        # print(out.pUSBVendorID)
        
        print("blub")
        print(pUSBVendorID.value)
        print(pUSBProductID.value)
        print(pUSBDeviceID.value)
        print(pDeviceID.value)
        print(pEEPromID.value)
        print(pVersion.value)
        print(pSerialNumber.value)
        print(pCustomerID.value)
        print(pCompany.value)
        print(pDate.value)
        print(pProductStr.value)
        print(pCustomer.value)
        print(pCustomerStr.value)
        
        

if __name__ == '__main__':   

    #example of usage, open connection and move in x and y direction:
    mechonics = Mechonics()
    mechonics.open_connection()
    mechonics.sweep(Timeout = 100)
    time.sleep(2)
    mechonics.sweep(Axis=2)
    time.sleep(2)
    mechonics.close_connection()





