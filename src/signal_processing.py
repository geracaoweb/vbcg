#!/usr/bin/env python
# signal_processing.py - Class for processing of the signals obtained from the video

import settings
import numpy as np
from scipy.optimize import curve_fit
from defines import *

def normalize(inputSignal):
    # Normalize the signal to lie between 0 and 1

    outputSignal = inputSignal

    # Prohobit dividing by zero
    if np.max(np.abs(outputSignal)) > 0:
        maxVal = np.max(np.abs(outputSignal))
        minVal = np.min(np.abs(outputSignal))
        # MinMax normalization
        outputSignal = (outputSignal-minVal)/(maxVal-minVal)

    return outputSignal


def curveFitFunc(x, a, b):
    # linear curve fit function
    return a * x + b


def curveFit(inputSignal1, inputSignal2):
    # perform curve fitting and return slope value

    m, ret = curve_fit(curveFitFunc, inputSignal1, inputSignal2)

    return m

# Todo: Complete this algorithm
def algorithm1(inputRawSignal,inputOutputSignal,inputMagicNumber):
    # This function computes the algorithm as described in our ISMRM 2016 contribution
    RawSignal = inputRawSignal
    OutputSignal = inputOutputSignal
    magic_number = inputMagicNumber

    # Normalize values
    valuesNorm = normalize(RawSignal)
    # Perform pseudo derivation
    valuesNormDiff = np.abs(np.diff(valuesNorm))
    # Apply window
    valuesNormDiffWindow = valuesNormDiff[-magic_number:]
    # Prepare fit
    valuesXdata = np.linspace(0, 1, magic_number)
    # Apply curve fit
    valueM = curveFit(valuesXdata, valuesNormDiffWindow)

    # Get output: Computed signal
    OutputSignal = np.append(OutputSignal, valueM[1])
    OutputSignal = normalize(OutputSignal)
    # Get outpout: Input signal
    valuesRawOutput = valuesNorm

    return valuesRawOutput,OutputSignal

def computeHR(inputRawSignal, estimatedFPS):
    # This algorithm computes the HR of the subject

    # Get current parameters
    curr_settings = settings.get_parameters()

    # Store signal
    signal = inputRawSignal
    # Store number of elements in signal
    N = np.size(signal)
    # Get FPS of video stream
    fps = estimatedFPS
    # Minimal and maximum HR (30..180 bpm)
    hrMin = 0.5
    hrMax = 3

    # Use Hamming window on signal
    valuesWin = signal[0:N] * np.hamming(N)
    # Compute FFT
    signalFFT = np.fft.fft(valuesWin)
    # Compute frequency axis
    x = np.linspace(0, N / fps, N + 1)
    freqAxis = np.fft.fftfreq(len(valuesWin), x[1] - x[0])

    # Get boolean values if values are between hrMin and hrMax
    limitsBool= (hrMin < freqAxis) & (hrMax > freqAxis)
    limitsIdx = np.linspace(0, N - 1, N)
    # Get indices of frequncies between hrMin and hrMax
    limits = limitsIdx[limitsBool.nonzero()]
    limits = limits.astype(int)
    # Get index of maximum frequency in FFT spectrum
    max_val = limits[np.argmax(abs(signalFFT[limits]))]

    # Return HR, spectrum with frequency axis, and found maximum
    return (np.round(freqAxis[max_val] * 60)), abs(signalFFT[limits]), freqAxis[limits], max_val-limits[0]