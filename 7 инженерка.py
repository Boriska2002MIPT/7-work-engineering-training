#importing modules
import RPi.GPIO as GPIO
import numpy as np
import time
import matplotlib.pyplot as plt

#creating constants
leds = [21, 20, 16, 12, 7, 8, 25, 23]
dac = [26, 19, 13, 6, 5, 11, 9, 10]
comparator = 4
troykaVoltage = 17

bits = len(dac)
levels = 2 ** bits
dV = 3.3 / levels

#setting GPIO modules
GPIO.setmode(GPIO.BCM)
GPIO.setup(leds + dac, GPIO.OUT)
GPIO.setup(troykaVoltage, GPIO.OUT)
GPIO.setup(comparator, GPIO.IN)

#defining functions 
def num2pins(pins, value):
    GPIO.output(pins, [int(i) for i in bin(value)[2:].zfill(bits)])

def adc():

    value = 0
    up = True

    for i in range(bits):
        delta = 2 ** (bits - 1 - i)
        value = value + delta * (1 if up else -1)

    num2pins(dac, value)
    time.sleep(0.0011)

    up = bool(GPIO.input(comparator))

    return value

def adc3():
    array = [0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(8):
        array[i] = 1
        GPIO.output(dac, array)
        time.sleep(0.001)

        if GPIO.input(comparator) == 0:
            array[i] = 0

    return array[0] * 2 ** 7 + array[1] * 2 ** 6 + array[2] * 2 ** 5 + array[3] * 2 ** 4 + array[4] * 2 ** 3 + array[5] * 2 ** 2 + array[6] * 2 ** 1 + array[7] * 2 ** 0

try:
    #create variables
    value = 0
    measure = []

    #Fix start time

    start = time.time()

    #charging capacitor

    GPIO.output(troykaVoltage, 1)
    while value <= 235:
        value = adc3()
        num2pins(leds, value)
        measure.append(value)
        print(adc3(), "charging")

    #discharging capacitor

    GPIO.output(troykaVoltage, 0)
    while value > 1:
        value = adc3()
        num2pins(leds, value)
        measure.append(value)
        print(adc3(), "discharging")

    #fix finish time and print time values

    finish = time.time()

    TIME = finish - start
    MeasurePeriod = TIME / len(measure)
    samplingFrequency = int(1 / MeasurePeriod)
    print("Measure time : {:.2f} s, measure period: {:.3f} ms, sampling frequency: {:d} Hz".format(TIME, MeasurePeriod, samplingFrequency))

    #creating the plot

    plt.plot(measure)
    plt.show()

    #writing in files
    measured_data_str = [str(item) for item in measure]
    with open('data.txt', 'w') as f1:
        f1.write(measured_data_str)
    with open('settings.txt', 'w') as f2:
        f2.write(MeasurePeriod, dV)

    #executing after script

finally:
    GPIO.cleanup()
    print('GPIO.cleanup completed')





