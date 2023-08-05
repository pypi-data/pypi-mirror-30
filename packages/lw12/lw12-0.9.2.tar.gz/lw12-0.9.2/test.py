#!/usr/bin/env python

from lw12 import *
import time


lw12 = LW12Controller('192.168.178.24', 5000)
print('[+] LW12 LIGHT OFF')
lw12.light_off()
time.sleep(.500)
print('[+] LW12 LIGHT ON')
lw12.light_on()
time.sleep(.500)
print('[+] LW12_LIGHT.BRIGHTNESS')
for brightness in range(0, 101, 5):
    print('    brightness={}'.format(brightness))
    lw12.set_light_option(LW12_LIGHT.BRIGHTNESS, brightness)
    time.sleep(.250)
print('[+] LW12_LIGHT.FLASH')
print('    speed=100')
lw12.set_light_option(LW12_LIGHT.FLASH, 100)
print('[+] LW12_EFFECT')
for effect in LW12_EFFECT:
    print('    {}'.format(effect))
    lw12.set_effect(effect)
    time.sleep(2)
lw12.set_effect(LW12_EFFECT.PURPLE)
lw12.set_light_option(LW12_LIGHT.BRIGHTNESS, 10)
print('[+] LW12 SCAN')
lw12.scan()
print('[+] LW12 SET COLOR r=255, g=75, b=216')
lw12.set_color(255, 75, 216)
