from rflib import *
import time, re, sys
sys.dont_write_bytecode = True

# Global variables
capture = ""
mytime = time.strftime('%Y_%m_%d_%H%M%S')

def bruteForceFreq(d, rf_settings, interval, clicker=False):
    """Brute forces frequencies looking for one with data being sent.
       Requires an RFCat Class, a starting frequency and the incrementing interval.
       EX: 315000000, 50000
    """
    d.setFreq(rf_settings.frequency)
    current_freq = rf_settings.frequency
    filename = "./scanning_logs/" + mytime + ".log"

    while not keystop():
        print("Currently Scanning: " + str(current_freq) + " To cancel hit enter and wait a few seconds")
        sniffFrequency(d, current_freq, filename, clicker)

        current_freq += interval
        d.setFreq(current_freq)
    
    print("Saved logfile as: ./scanning_logs/" + mytime + ".log")

def searchKnownFreqs(d, known_frequencies, clicker=False):
    """Sniffs on a rotating list of known frequencies from the default list
       or optionally uses a list provided to the function. Requires an RFCat class.
    """
    filename = "./scanning_logs/" + mytime + ".log"
    
    while not keystop():
        for current_freq in known_frequencies:
            d.setFreq(current_freq)
            print("Currently Scanning: " + str(current_freq) + " To cancel hit enter and wait a few seconds")
            if clicker:
                sniffFrequency(d, current_freq, "./captures/capturedClicks.log", clicker)
            else:
                sniffFrequency(d, current_freq, filename, clicker)
    
    print("Saved logfile as: " + filename)

def sniffFrequency(d, current_freq, filename, clicker):
    """Sniffs on a frequency, requires an RFCat Class with proper info set for listening."""
    
    if clicker:
        while True:
            try:
                y, z = d.RFrecv()
                capture = y.encode('hex')
                print(capture)
                saveLogs(current_freq, capture, filename)
            except ChipconUsbTimeoutException:
                pass
            except KeyboardInterrupt:
                print("User stopped the clicker sniffing.")
                break  
    else:
        try:
            y, z = d.RFrecv(timeout=3000)
            capture = y.encode('hex')
            print(capture)
            saveLogs(current_freq, capture, filename)
        except ChipconUsbTimeoutException:
            pass

def saveLogs(current_freq, capture, filename=" "):
    """Used to create logs for scanning known and bruteforcing frequencies."""
    with open(filename, 'a+') as file:
        file.write("A signal was found on: " + str(current_freq) + "\n" + capture + "\n")
