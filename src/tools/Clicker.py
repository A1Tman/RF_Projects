import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import numpy as np
import sys
import subprocess
import RFFunctions as tools

# Disable bytecode generation
sys.dont_write_bytecode = True

# Setup Graphing Size
fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 8
fig_size[1] = 3
plt.rcParams["figure.figsize"] = fig_size

# Clicker Class for RF Signal Analysis and Visualization
class Clicker:
    """This class is used to help identify and analyze signals as well as create clickers
    from captures. It uses a known payload and live captures or a logfile of unknown payloads to compare."""
    
    def __init__(self, captured_payload, keyfob_payloads=[]):
        self.captured_payload = captured_payload
        self.keyfob_payloads = keyfob_payloads
        # Print statement describing the purpose of this Clicker instance
        print("Clicker instance created: ready to analyze and compare RF signals.")

    def determineDipSwitches(self, captured_payload):
        """This function will return the dip switches as up:down:down:up format based on signal analysis"""
        pass

    def liveClicks(self):
        """Compare signals and create graphs to compare a live capture with a keyfob press"""
        live = True
        graph_to_percent = {}  # Holds % match and payload for each signal in a click

        # Get binary output of the payload
        captured_payload_binary = self.payloadsToBinary(self.captured_payload)
        print("----------Start Signals On Press--------------")
        
        for presses in self.keyfob_payloads:
            for keyfob_payload in presses:
                percent = self.convertAndCompare(self.captured_payload, keyfob_payload)
                graph_to_percent[keyfob_payload] = percent
                print("Percent Chance of Match for press is: {:.2f}".format(percent))
        
        print("----------End Signals On Press------------")
        
        # Send dictionaries of percents and return the signal with the highest % comparison
        keyfob_payload = self.getHighestPercent(graph_to_percent)
        keyfob_programming_binary = self.payloadsToBinary(keyfob_payload)

        self.createGraph(captured_payload_binary, keyfob_programming_binary)
        self.outputImagesComparisons(1, live)
        plt.close()
        self.openImage('./imageOutput/LiveComparison.png')

        print("For Visual of the last signal comparison go to ./imageOutput/LiveComparison.png")

    def createImageGraph(self):
        """Create a graph to compare a list of captures with the keyfob press"""
        count = 0

        # Get binary output of the payload
        captured_payload_binary = self.payloadsToBinary(self.captured_payload)

        for presses in self.keyfob_payloads:
            for keyfob_payload in presses:
                percent = self.convertAndCompare(self.captured_payload, keyfob_payload)
                print("Percent Chance of Match for press is: {:.2f}".format(percent))

                self.createGraph(captured_payload_binary, self.payloadsToBinary(keyfob_payload))
                self.outputImagesComparisons(count)
                count += 1
                plt.close()

    def setupNumberPrinting(self, captured_payload_binary, keyfob_programming_binary):
        """Prints numbers under the graph, reduces the counts in half for readability with a counter"""
        count = 0
        for tbit, bit in enumerate(captured_payload_binary):
            if count % 2 != 1:
                plt.text(tbit + 0.5, 3.5, str(bit))
            count += 1

        count = 0
        for tbit, bit in enumerate(keyfob_programming_binary):
            if count % 2 != 1:
                plt.text(tbit + 0.5, 1.5, str(bit))
            count += 1

    def outputImagesComparisons(self, count, live=False):
        """Outputs image files to compare capture to keyfob presses"""
        if live:
            pylab.savefig("./imageOutput/LiveComparison.png")
        else:
            pylab.savefig("./imageOutput/Graph" + str(count) + ".png")

    def payloadsToBinary(self, payload):
        """Converts hex data into binary and back into lists of binary numbers"""
        binary = bin(int(payload, 16))[2:]
        results = list(map(int, list(str(binary))))
        return results

    def getHighestPercent(self, myDictionary):
        """Takes a dictionary of signals as keys and returns the signal with the highest percent value"""
        highest_percent = max(zip(myDictionary.values(), myDictionary.keys()))
        return highest_percent[1]

    def openImage(self, path):
        """Opens an image from the hard drive based on the path sent in"""
        try:
            image_viewer = {
                'linux': 'eog',
                'linux2': 'eog',
                'win32': 'explorer',
                'darwin': 'open'
            }.get(sys.platform, 'eog')  # Default to eog for unknown platforms
            subprocess.call([image_viewer, path])
        except Exception as e:
            print(f"Failed to open image: {e}")

    def createGraph(self, captured_payload_binary, keyfob_programming_binary):
        """Sets up the graphing elements for images or display, requires 2 binary payloads to plot"""
        payload_data = np.repeat(captured_payload_binary, 2)
        keyfob_data = np.repeat(keyfob_programming_binary, 2)
        t = 0.5 * np.arange(len(payload_data))
        u = 0.5 * np.arange(len(keyfob_data))

        # Used to show the waveform
        plt.step(t, payload_data + 4, 'r', linewidth=2, where='post')
        plt.step(u, keyfob_data + 2, 'r', linewidth=2, where='post')

        # Limit the height of the waveform and turns off axis lines
        plt.ylim([-1, 6])
        plt.gca().axis('off')

    def convertAndCompare(self, payload1, payload2):
        """Convert payloads to binary and compare them, returning the match percentage."""
        binary1 = self.payloadsToBinary(payload1)
        binary2 = self.payloadsToBinary(payload2)
        one = ''.join(str(x) for x in binary1)
        two = ''.join(str(x) for x in binary2)
        return tools.similar(one, two)
