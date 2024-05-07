import display
import device
import time

def show_battery(count):
    batLvl = str(device.battery_level())
    fill = display.Fill(display.BLUE)
    text = display.Text("bat: {} {}".format(batLvl, count), 5, 5, display.WHITE)
    display.show(fill, text)

count = 0
while count < 5:
    show_battery(count)
    time.sleep(1)
    count += 1

fill = display.Fill(display.CLEAR)
display.show(fill)

print("Done")