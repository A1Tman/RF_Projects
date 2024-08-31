import bitstring
from time import sleep
import rflib

# That prefix string. This was determined by literally
# just looking at the waveform, and calculating it relative
# to the clock signal value.
# Your remote may not need this.
prefix = ''

# The key from our static key remote.
key = '1111111110111011111100111'

# Convert the data to a PWM key
pwm_key = ''.join(['1000' if b == '1' else '1110' for b in key])

# Join the prefix and the data for the full pwm key
full_pwm = '{}{}'.format(prefix, pwm_key)
print('Complete PWM key: {}'.format(full_pwm))

# Convert the data to hex
rf_data = bitstring.BitArray(bin=full_pwm).tobytes()
print(bitstring.BitArray(bin=full_pwm).tobytes())
print("Byte string: ",rf_data)
print("PWM Key: ",pwm_key)

# Start up RfCat
d = rflib.RfCat()

# Set Modulation. We using On-Off Keying here
d.setMdmModulation(rflib.MOD_ASK_OOK)

# Configure the radio
d.makePktFLEN(16) 	# Set the RFData packet length
d.setMdmDRate(2500)     # Set the Baud Rate
d.setMdmSyncMode(0)     # Disable preamble
d.setFreq(433916000)    # Set the frequency
d.setMaxPower()

# Send the data string a few times
d.RFxmit('\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\xee\x88\x80\x00\x00\x00'*4)
d.setModeIDLE()