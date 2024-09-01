from rflib import *
import src.tools.RFFunctions as tools
import re, time, argparse, textwrap
import src.tools.jam as jam
import src.tools.findDevices as findDevices
import src.tools.attacks as attacks
import src.tools.RFSettings as RFSettings
import src.tools.utilities as utilities
import src.tools.Clicker as Clicker
import sys

# Setup argument parser
parser = argparse.ArgumentParser(
    description="A tool for RF communication and attacks.",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument("-s", "--send", action='store_true', help="Send a saved payload from a file.")
parser.add_argument("-i", "--instant_replay", action='store_true', help="Replay a captured signal in real-time.")
parser.add_argument("-r", "--rolling_code", default=False, action='store_true', help="Perform a rolling code attack.")
parser.add_argument("-t", "--targeted_attack", help="Perform a targeted attack (not fully implemented).")
parser.add_argument("-j", "--jammer", action='store_true', help="Activate the jammer to disrupt signals.")
parser.add_argument("-b", "--brute_scanner", action='store_true', help="Brute force frequency scanning.")
parser.add_argument("-k", "--known_scanner", action='store_true', help="Scan known frequencies for devices.")
parser.add_argument("-v", "--increment_value", help="Specify increment value for brute force scanning.", type=int)
parser.add_argument('-u', "--uploaded_payload", help="Specify the file path of the payload to upload and send.")
parser.add_argument('-f', "--list", nargs='+', type=int, default=[315000000, 433000000], help="List of frequencies to scan.")
parser.add_argument('-a', "--jamming_variance", default=80000, help="Specify variance for jamming frequency.", type=int)
parser.add_argument('-d', "--save_device_settings", action='store_true', help="Save current device settings to a template.")
parser.add_argument('-l', "--load_device_settings", help="Load device settings from a template file.")
parser.add_argument('-c', "--compare", action='store_true', help="Compare a captured signal with a known signal.")
parser.add_argument('-n', "--no_instance", action='store_true', help="Run without initializing a device instance.")
parser.add_argument('-g', "--graph_signal", action='store_true', help="Graph the signal from a captured payload.")
parser.add_argument('-D', "--de_bruijn", action='store_true', help="Generate and send a de Bruijn sequence.")
parser.add_argument('-B', "--baud_rate", default=4800, help="Specify baud rate for communication.", type=int)
parser.add_argument('-U', "--upper_rssi", default=-100, help="Specify upper RSSI threshold.", type=int)
parser.add_argument('-L', "--lower_rssi", default=-20, help="Specify lower RSSI threshold.", type=int)
parser.add_argument("-F", "--frequency", default=315000000, help="Specify the frequency for communication.", type=int)
parser.add_argument('-C', "--channel_bandwidth", default=60000, help="Specify the channel bandwidth.", type=int)
parser.add_argument("-M", "--modulation_type", default="MOD_ASK_OOK", help="Specify modulation type (e.g., MOD_ASK_OOK, MOD_2FSK).")
parser.add_argument("-S", "--channel_spacing", default=24000, help="Specify the channel spacing.", type=int)
parser.add_argument("-V", "--deviation", default=0, help="Specify the deviation for the RF signal.", type=int)

args = parser.parse_args()

# Initialize RFSettings object
rf_settings = RFSettings.RFSettings(
    frequency=args.frequency,
    baud_rate=args.baud_rate,
    channel_bandwidth=args.channel_bandwidth,
    modulation_type=args.modulation_type,
    upper_rssi=args.upper_rssi,
    lower_rssi=args.lower_rssi,
    channel_spacing=args.channel_spacing,
    deviation=args.deviation
)

# Load device settings from a file if specified
if args.load_device_settings:
    try:
        with open(args.load_device_settings) as f:
            file_data = f.readlines()
            rf_settings.loadDeviceSettingsTemplate(file_data)
    except Exception as e:
        print(f"Error loading device settings: {e}")
        sys.exit(1)

# Initialize the RfCat device if necessary
if not args.jammer and not args.no_instance:
    try:
        d = RfCat(idx=0)
        d.setFreq(int(rf_settings.frequency))
        d.setMdmDRate(rf_settings.baud_rate)
        d.setMaxPower()
        d.setMdmChanSpc(rf_settings.channel_spacing)
        d.setMdmChanBW(rf_settings.channel_bandwidth)
        d.setMdmSyncMode(0)
        d.setChannel(0)
        d.lowball(1)
        if rf_settings.deviation != 0:
            d.setMdmDeviatn(rf_settings.deviation)
        if rf_settings.modulation_type == "MOD_ASK_OOK":
            d.setMdmModulation(MOD_ASK_OOK)
        elif rf_settings.modulation_type == "MOD_2FSK":
            d.setMdmModulation(MOD_2FSK)
    except Exception as e:
        print(f"Error initializing RF device: {e}")
        sys.exit(1)

# Execute the specified operations based on command-line arguments
if args.rolling_code:
    print("Don't forget to change the default frequency and modulation type")
    attacks.rollingCode(d, rf_settings, args.rolling_code, args.jamming_variance)

if args.known_scanner and not args.compare:
    print("For a custom list, use the -f option in the format -f 433000000 314000000 390000000")
    findDevices.searchKnownFreqs(d, args.list)

if args.brute_scanner:
    if args.increment_value is None:
        print("Bruteforcing requires -v argument for an incrementing interval value (e.g., 500000)")
    else:
        findDevices.bruteForceFreq(d, rf_settings, args.increment_value)

if args.jammer:
    j = jam.setupJammer(0, rf_settings)
    jam.jamming(j, "start", rf_settings, args.rolling_code)

if args.instant_replay:
    attacks.replayLiveCapture(d, args.rolling_code, rf_settings)

if args.send:
    if args.uploaded_payload is None:
        print("Send requires -u argument for an upload file path (e.g., ./captures/payload.cap)")
    else:
        attacks.replaySavedCapture(d, args.uploaded_payload)

if args.save_device_settings:
    device_name = input("What would you like to name the device template: ")
    rf_settings.saveDeviceSettingsTemplate(device_name)

if args.known_scanner and args.compare:
    print("Uses lowercase f parameter to specify a single value frequency list")
    findDevices.searchKnownFreqs(d, args.list, args.compare)

if args.compare and args.uploaded_payload is not None:
    my_clicker = Clicker.Clicker(args.uploaded_payload)
    utilities.logTail(my_clicker)

if args.graph_signal and args.uploaded_payload is not None:
    my_clicker = Clicker.Clicker(args.uploaded_payload)
    captured_payload_binary = my_clicker.payloadsToBinary(my_clicker.captured_payload)
    my_clicker.createGraph(captured_payload_binary, 0)
    my_clicker.outputImagesComparisons(1)
    my_clicker.openImage('./imageOutput/Graph1.png')

if args.de_bruijn:
    attacks.deBruijn(d)
