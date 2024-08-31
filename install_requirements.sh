#!/bin/bash

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found. Please install pip and run this script again."
    exit
fi

# Install or update required Python libraries
echo "Installing or updating required Python libraries..."
pip install --upgrade -r requirements.txt

# Check if RfCat is installed
if ! python3 -c "import rflib" &> /dev/null
then
    echo "RfCat is not installed. Installing RfCat..."
    # Install RfCat and its dependencies
    sudo apt-get update
    sudo apt-get install python3-pip python3-usb python3-serial python3-dev libusb-1.0-0-dev
    git clone https://github.com/atlas0fd00m/rfcat.git
    cd rfcat
    sudo python3 setup.py install
    cd ..
    echo "RfCat installation complete."
else
    echo "RfCat is already installed."
fi

echo "All required libraries are installed and up to date."
