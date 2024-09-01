from rflib import *
import bitstring
import time, sys, re
sys.dont_write_bytecode = True
from difflib import SequenceMatcher

#-----------------Start RF Capture ----------------#
def capturePayload(d, rolling_code, rf_settings):
    """Starts a listener and returns an RFrecv capture and signal strength.
    If rolling code options are sent, it will check for valid packets while the jammer is running."""
    
    capture = ""        # Capture without Rolling code
    roll_captures = []  # List of captures for RollingCode

    roll_count = 0      # Used to count 2 captures
    while True:
        try:
            y, z = d.RFrecv()
            capture = y.encode('hex')
            signal_strength = -ord(str(d.getRSSI()))  # Convert RSSI to a negative integer
        except ChipconUsbTimeoutException:
            pass

        # This block is used for rolling code operations
        if rolling_code and capture:  # If there is a good capture and we are attacking rollingCode, execute this block
            print("SIGNAL STRENGTH: " + str(signal_strength))
            print("RF CAPTURE: \n" + capture + "\n")
            decision = determineRealTransmission(signal_strength, rf_settings)
            if decision:
                roll_captures.append(capture)  # Add key with good decision to the list
                if roll_count >= 1:  # Check if we have 2 keys and return
                    return roll_captures, signal_strength
                else:
                    roll_count += 1
                    continue
            else:
                continue

        # This block is for just capturing and returning, no rolling code
        elif capture and not rolling_code:
            print("SIGNAL STRENGTH: " + str(signal_strength))
            print("RF CAPTURE: \n" + capture + "\n")

            response = input("\"Do you want to return the above payload? (y/n): ")
            if response.lower() == 'y':
                break
            if response.lower() == 'n':
                capture = ""

    return capture, signal_strength


#----------------- Determine Real Transmission ----------------#
def determineRealTransmission(signal_strength, rf_settings):
    """Used to search for transmissions which are not max power and fall between
    defined RSSI power levels."""
    if rf_settings.lower_rssi < signal_strength < rf_settings.upper_rssi:
        return True
    return False


#------------Split Captures by 4 or more 0's --------------------#
def splitCaptureByZeros(capture):
    """Parses hex from the capture by reducing 0's."""
    payloads = re.split('0000*', capture)
    items = [payload for payload in payloads if len(payload) > 5]
    return items


#------------Split Device Settings Configuration --------------------#
def parseDeviceSettings(file_data):
    """Parses file device configuration and returns a list."""
    settings = [re.split(':', data) for data in file_data]
    print(settings)
    return settings


#------------ Hex conversion function --------------------#
def printFormatedHex(payload):
    """Helper function that takes RFrecv output and returns formatted hex.
    Note: Don't just use this output into your send, but you can manually paste its output in a string."""
    
    formatedPayload = ""
    if len(payload) % 2 == 0:
        print("The following payload is currently being formatted: " + payload)
        iterator = iter(payload)
        for i in iterator:
            formatedPayload += ('\\x' + i + next(iterator))

    return formatedPayload


#------------Create Payloads in Bytes--------------------#
def createBytesFromPayloads(payloads):
    """Accepts a list of payloads for formatting and returns a list formatted in byte format
    for RFXmit transmission."""
    formatedPayloads = [turnToBytes(bin(int(payload, 16))[2:]) for payload in payloads]
    return formatedPayloads

def turnToBytes(binary):
    """Converts binary payloads into sendable byte payloads."""
    payloadBytes = bitstring.BitArray(bin=(binary)).tobytes()
    return payloadBytes


#------------Send Transmission--------------------#
def sendTransmission(payload, d):
    """Expects formatted data for sending with RFXMIT."""
    print("Sending payload...")
    d.RFxmit(payload, 10)
    print("Transmission Complete")


#-------------------Parse the log file------------#
def parseSignalsFromLog(log_file):
    """Creates a multidimensional array of signals from a logfile split by 0000's."""
    payloads = []
    with open(log_file) as f:
        for line in f:
            if "found" not in line:
                payloads.append(splitCaptureByZeros(line))
    return payloads

def similar(a, b):
    """Returns the similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()


#-------------------Parse single Log Entry From live Clicker------------#
def parseSignalsLive(click):
    """Creates a multidimensional array of signals from a logfile split by 0000's."""
    payloads = [splitCaptureByZeros(click)]
    return payloads
