import sys
import os
sys.dont_write_bytecode = True

class RFSettings:
    """This class is used to set up RFCat settings needed for listening, jamming, and sending."""
    
    def __init__(
        self, 
        frequency: int, 
        baud_rate: int, 
        channel_bandwidth: int, 
        modulation_type: str, 
        upper_rssi: int, 
        lower_rssi: int, 
        channel_spacing: int, 
        deviation: int
    ):
        """Initializes the RFSettings with the specified parameters.

        Args:
            frequency (int): The frequency for RF communication.
            baud_rate (int): The baud rate for RF communication.
            channel_bandwidth (int): The channel bandwidth for RF communication.
            modulation_type (str): The modulation type (e.g., 'ASK', 'FSK').
            upper_rssi (int): The upper RSSI limit for signal strength.
            lower_rssi (int): The lower RSSI limit for signal strength.
            channel_spacing (int): The spacing between RF channels.
            deviation (int): The deviation for the RF signal.
        """
        self.frequency = frequency
        self.baud_rate = baud_rate
        self.channel_bandwidth = channel_bandwidth
        self.modulation_type = modulation_type
        self.upper_rssi = upper_rssi
        self.lower_rssi = lower_rssi
        self.channel_spacing = channel_spacing
        self.deviation = deviation

    def saveDeviceSettingsTemplate(self, device_name: str, verbose: bool = False):
        """Saves the current RF settings to a file in the device_templates folder for later use.

        Args:
            device_name (str): The name of the device for which the settings are saved.
            verbose (bool): If True, prints detailed information about the saving process.
        """
        try:
            save_path = os.path.join(".", "device_templates", f"{device_name}.config")
            with open(save_path, 'w') as file:
                for key, value in self.__dict__.items():
                    if not key.startswith("__"):
                        if verbose:
                            print(f"{key}: {value}")
                        file.write(f"{key}: {value}\n")
            if verbose:
                print(f"Saved file as: {save_path}")
        except Exception as e:
            print(f"Error saving device settings: {e}")

    def loadDeviceSettingsTemplate(self, file_data: list[str], verbose: bool = False):
        """Loads previously saved working settings for attacking a device.

        Args:
            file_data (list[str]): The contents of the file containing saved RF settings.
            verbose (bool): If True, prints detailed information about the loading process.
        """
        try:
            for data in file_data:
                if "frequency" in data:
                    self.frequency = int(self.parseSetting(data))
                elif "baud_rate" in data:
                    self.baud_rate = int(self.parseSetting(data))
                elif "channel_bandwidth" in data:
                    self.channel_bandwidth = int(self.parseSetting(data))
                elif "modulation_type" in data:
                    self.modulation_type = self.parseSetting(data)
                elif "upper_rssi" in data:
                    self.upper_rssi = int(self.parseSetting(data))
                elif "lower_rssi" in data:
                    self.lower_rssi = int(self.parseSetting(data))
                elif "channel_spacing" in data:
                    self.channel_spacing = int(self.parseSetting(data))
                elif "deviation" in data:
                    self.deviation = int(self.parseSetting(data))
            
            if verbose:
                self.printSettings()
        except Exception as e:
            print(f"Error loading device settings: {e}")

    def parseSetting(self, data: str) -> str:
        """Parses a key-value pair from the settings data.

        Args:
            data (str): The data string to be parsed.

        Returns:
            str: The value extracted from the key-value pair.
        """
        try:
            key, value = data.split(":")
            return value.strip()
        except ValueError as e:
            print(f"Error parsing data '{data}': {e}")
            return ""

    def printSettings(self):
        """Prints the current RFCat settings in use."""
        print("The following settings are in use:")
        print(f"Frequency: {self.frequency}")
        print(f"Baud rate: {self.baud_rate}")
        print(f"Channel bandwidth: {self.channel_bandwidth}")
        print(f"Modulation type: {self.modulation_type}")
        print(f"Upper RSSI: {self.upper_rssi}")
        print(f"Lower RSSI: {self.lower_rssi}")
        print(f"Channel spacing: {self.channel_spacing}")
        print(f"Deviation: {self.deviation}")
