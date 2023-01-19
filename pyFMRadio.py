import board
#import badger2040
import digitalio
import terminalio
import displayio
import vectorio
from adafruit_display_text import label
import time
import supervisor
from adafruit_bus_device.i2c_device import I2CDevice
import tinkeringtech_rda5807m


""" From C documentation
    { MP_ROM_QSTR(MP_QSTR_BUTTON_A), MP_ROM_INT(12) },
    { MP_ROM_QSTR(MP_QSTR_BUTTON_B), MP_ROM_INT(13) },
    { MP_ROM_QSTR(MP_QSTR_BUTTON_C), MP_ROM_INT(14) },
    { MP_ROM_QSTR(MP_QSTR_BUTTON_D), MP_ROM_INT(15) },
    { MP_ROM_QSTR(MP_QSTR_BUTTON_E), MP_ROM_INT(11) },
    { MP_ROM_QSTR(MP_QSTR_BUTTON_UP), MP_ROM_INT(15) },    // alias for D
    { MP_ROM_QSTR(MP_QSTR_BUTTON_DOWN), MP_ROM_INT(11) },  // alias for E
    { MP_ROM_QSTR(MP_QSTR_BUTTON_USER), MP_ROM_INT(23) },
"""

# Push buttons
NUM_BUTTONS = 5
BUTTON_A = 0
BUTTON_B = 1
BUTTON_C = 2
BUTTON_UP = 3
BUTTON_DOWN = 4

# Radio Commands
VOL_UP = '+'
VOL_DOWN = '-'
PRESET_LEFT = '<'
PRESET_RIGHT = '>'
SCAN_UP = '.'


"""
An example of how to show text on the Badger 2040's
screen using the built-in DisplayIO object.
"""
buttons = [
    digitalio.DigitalInOut(board.SW_A),
    digitalio.DigitalInOut(board.SW_B),
    digitalio.DigitalInOut(board.SW_C),
    digitalio.DigitalInOut(board.SW_UP),
    digitalio.DigitalInOut(board.SW_DOWN)
]

btnOldValues = [False, False, False, False, False]



def setButtonProperties():
    global buttons
    
    for btn in buttons:
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.DOWN




"""
Returns True if button value has changed
"""
def chkButton(btn_number):
    global buttons, btnOldValues
    
    print
    
    cur_val = buttons[btn_number].value
    
    if not cur_val == btnOldValues[btn_number]:
        btnOldValues[btn_number] = cur_val
        return cur_val # only want went changes to True
    
    return False

def checkButtons():
    global buttons, NUM_BUTTONS
    
    for btn_no in range(NUM_BUTTONS):
        if chkButton(btn_no):
            handleButton(buttons[btn_no])
            return # Only handle one button at a time

def handleButton(btn):
    print("Handling butto: " + str(btn))
    
    if btn == buttons[BUTTON_A]:
        handleRadioCommand(PRESET_LEFT)
        return
    if btn == buttons[BUTTON_B]:
        handleRadioCommand(PRESET_RIGHT)
        return
    if btn == buttons[BUTTON_C]:
        handleRadioCommand(SCAN_UP)
        return
    if btn == buttons[BUTTON_UP]:
        handleRadioCommand(VOL_UP)
        return
    if btn == buttons[BUTTON_DOWN]:
        handleRadioCommand(VOL_DOWN)
        return
   # if pin == button_user:
   #     message = "Button Usr"
   #     return


def drawText():
    # Write text on display
    global display, title_label, subtitle_label, radio
   
    stn_text = radio.format_freq()
    vol_text = "Volume: " + str(radio.volume)
    # Split text into two lines
    
        
    # Check that lines are not empty
    if not stn_text.strip():
        warning = "No Station Info"
        title_label.text = warning

    else:
        # Line 1
        title_label.text = stn_text
        
        # Line 2
        subtitle_label.text = vol_text
    
    print("Waiting to update dislay...")
    time.sleep(display.time_to_refresh)
    while display.busy:
        pass
    print("Refreshing dislay...")
    display.refresh()
    print("display refreshed.")

# RDS text handle
def textHandle(rdsText):
    global rdstext
    rdstext = rdsText
    print(rdsText)
    



def handleRadioCommand(cmd, value=0):
    # Executes a command
    # Starts with a character, and optionally followed by an integer, if required
    
    print("Handling command: " + cmd)
    
    global i_sidx
    global presets
    if cmd == "?":
        print("? help")
        print("+ increase volume")
        print("- decrease volume")
        print("> next preset")
        print("< previous preset")
        print(". scan up ")
        print(", scan down ")
        print("f direct frequency input")
        print("i station status")
        print("s mono/stereo mode")
        print("b bass boost")
        print("u mute/unmute")
        print("r get rssi data")
        print("e softreset chip")
        print("q stops the program")

    # Volume and audio control
    elif cmd == "+":
        v = radio.volume
        if v < 15:
            radio.set_volume(v + 1)
    elif cmd == "-":
        v = radio.volume
        if v > 0:
            radio.set_volume(v - 1)

    # Toggle mute mode
    elif cmd == "u":
        radio.set_mute(not radio.mute)
    # Toggle stereo mode
    elif cmd == "s":
        radio.set_mono(not radio.mono)
    # Toggle bass boost
    elif cmd == "b":
        radio.set_bass_boost(not radio.bassBoost)

    # Frequency control
    elif cmd == ">":
        # Goes to the next preset station
        if i_sidx < (len(presets) - 1):
            i_sidx = i_sidx + 1
            radio.set_freq(presets[i_sidx])
    elif cmd == "<":
        # Goes to the previous preset station
        if i_sidx > 0:
            i_sidx = i_sidx - 1
            radio.set_freq(presets[i_sidx])

    # Set frequency
    elif cmd == "f":
        radio.set_freq(value)

    # Seek up/down
    elif cmd == ".":
        radio.seek_up()
    elif cmd == ",":
        radio.seek_down()

    # Display current signal strength
    elif cmd == "r":
        print("RSSI: " + str(radio.get_rssi()))

    # Soft reset chip
    elif cmd == "e":
        radio.soft_reset()

    # Not in help
    elif cmd == "!":
        radio.term()

    elif cmd == "i":
        # Display chip info
        s = radio.format_freq()
        print("Station: " + s)
        print("Radio info: ")
        print("RDS -> " + str(radio.rds))
        print("TUNED -> " + str(radio.tuned))
        print("STEREO -> " + str(not radio.mono))
        print("Audio info: ")
        print("BASS -> " + str(radio.bassBoost))
        print("MUTE -> " + str(radio.mute))
        print("SOFTMUTE -> " + str(radio.softMute))
        print("VOLUME -> " + str(radio.volume))
        
    drawText()

setButtonProperties()

#button_user.irq(trigger=machine.Pin.IRQ_RISING, handler=button)





presets = [  # Preset stations
    8870,
    9070,
    9910,
    10110,
    10250,
    10330,
    10570
]
i_sidx = 4  # Starting at station with index 3

i2c = board.I2C()

# Receiver i2c communication
address = 0x11
radio_i2c = I2CDevice(i2c, address)

vol = 2 # Default volume
band = "FM"

initial_time = time.monotonic()  # Initial time - used for timing
toggle_frequency = 5  # Frequency at which the text changes between radio frequnecy and rds in seconds

rds = tinkeringtech_rda5807m.RDSParser()
rds.attach_text_callback(textHandle)

rdstext = "No rds data"

radio = tinkeringtech_rda5807m.Radio(radio_i2c, rds, presets[i_sidx], vol)
radio.set_band(band)  # Minimum frequency - 87 Mhz, max - 108 Mhz



display = board.DISPLAY

# Set text, font, and color
title = "pyFM Radio"
subtitle = "From TommyD"
font = terminalio.FONT
color = 0x000000



# Set the palette for the background color
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF

# Add a background rectangle
rectangle = vectorio.Rectangle(pixel_shader=palette, width=display.width + 1, height=display.height, x=0, y=0)

# Create the title and subtitle labels
title_label = label.Label(font, text=title, color=color, scale=4)
subtitle_label = label.Label(font, text=subtitle, color=color, scale=2)

# Set the label locations
title_label.x = 20
title_label.y = 45

subtitle_label.x = 40
subtitle_label.y = 90

# Create the display group and append objects to it
group = displayio.Group()
group.append(rectangle)
group.append(title_label)
group.append(subtitle_label)

# Show the group and refresh the screen to see the result
display.show(group)
#display.refresh()




print_rds = False
radio.sendRDS = rds.process_data
handleRadioCommand("?", 0)


while True:
        checkButtons()
