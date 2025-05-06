import numpy as np
import os
from django.conf import settings
from scipy.io.wavfile import write
from pymongo import MongoClient
from bson import ObjectId
from pymongo import MongoClient
from scipy import integrate, signal
import struct
import math
from scipy.signal import hilbert
from datetime import datetime, timedelta
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import traceback
from pathlib import Path
import json

client = MongoClient(settings.MONGO_URI)
db = client[settings.APP_DB]

def isoStandardGetter(machineId):
    try:
        machineCollection = db["machine"]
        isoTable = db["ISOStandard"]
        machineData = machineCollection.find_one({"_id": ObjectId(machineId)})
        if machineData and "isoStandardId" in machineData:
            isoData = isoTable.find_one({"_id": machineData["isoStandardId"]})
            return isoData
        return None
    except Exception as e:
        print(f"An error occurred: {e}")

def getOrderCutoff(macAddress):
    sensorCollection = db["Sensor"]
    sensorDetails = sensorCollection.find_one({"address": macAddress})
    if sensorDetails and "highpassCutoff" in sensorDetails and "highpassOrderFft" in sensorDetails:
        return sensorDetails['highpassCutoff'], sensorDetails['highpassOrderFft']
    return None

def isoAlertGetter(value, isoDict):
    try:
        alertThreshold = float(isoDict["alert"])
        satisfactoryThreshold = float(isoDict["satisfactory"])
        normalThreshold = float(isoDict["normal"])
        if value > alertThreshold:
            return "unacceptable"
        elif value > satisfactoryThreshold:
            return "alert"
        elif value > normalThreshold:
            return "satisfactory"
        else:
            return "normal"
    except Exception as e:
        print(f"An error occurred: {e}")

def fileFind(id):
    return id > 0

def sensorName(val, data):
    for i in data:
        if val == i["PointIndex"]:
            return i["Name"]
    return None

def butterHighpass(cutoff, fs, order=2):
    nyq = 0.5 * fs
    normalCutoff = cutoff / nyq
    b, a = signal.butter(order, normalCutoff, btype='highpass', analog=False)
    return b, a

def butterLowpass(cutoff, fs, order=2):
    nyq = 0.5 * fs
    normalCutoff = cutoff / nyq
    b, a = signal.butter(order, normalCutoff, btype='lowpass', analog=False)
    return b, a

def butterHighpassFilter(data, cutoff, fs, order=2):
    b, a = butterHighpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butterLowpassFilter(data, cutoff, fs, order=2):
    b, a = butterLowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def FFT(temp):
    N = len(temp)
    yf = np.fft.fft(temp)
    yf = 2.0/N * np.abs(yf[:N//2])
    yf[0] = 0
    return yf

def hannData(data):
    window = signal.windows.hann(len(data))
    twsValue = data * window
    return twsValue

def hexTWF(hexData):
    hexData = hexData[0]['ThisFile']
    SR = int(str(struct.unpack('i', (hexData[1:5]))[0]))
    cal_val = struct.unpack('d', (hexData[5:13]))[0]
    sens = struct.unpack('f', (hexData[13:17]))[0]
    data = []
    for j in range(51, len(hexData) + 1, 2):
        try:
            data += [(((struct.unpack('h', (hexData[j:j + 2]))[0]) * cal_val) / sens)]
        except:
            pass
    return SR, np.array(data, dtype=np.float64)

def velocityConvert(data, lr):
    SR, timeseries = hexTWF(data)
    timeseries = timeseries * 9806.65
    time_step = 1 / SR
    N = len(timeseries)
    lr_value = 0
    if type(lr) == list:
        if 262144 < N:
            lr_value = int(51200 * 2.56)
        else:
            lr_value = int(102400 * 2.56)
    else:
        lr_value = int(lr * 2.56)
    filterCutoff = 4
    filterOrder = 2
    time = np.linspace(0.0, N * time_step, N)
    velocity = integrate.cumtrapz(timeseries, x=time)
    velocityTimeseriesData = velocity - np.mean(velocity)
    velocityTemp = butterHighpassFilter(velocityTimeseriesData[0:lr_value], filterCutoff, SR, filterOrder)
    velocityFFTData = ((FFT(hannData(velocityTemp))) * 0.707) * 2.25
    velocityFFTXData = np.linspace(0.0, SR / 2, num=int(len(velocityFFTData)))
    velocityFFTData = np.round(velocityFFTData, 8)
    finalVelocityFFTData = [i for i in zip(velocityFFTXData, velocityFFTData)]
    v1 = (len(velocityTemp) / SR) / len(velocityTemp)
    velocityTemp = np.round(velocityTemp, 8)
    finalVelocityTempData = [[i * v1, velocityTemp[i]] for i in range(len(velocityTemp))]
    return {
        "SR": SR,
        "twf_min": finalVelocityTempData[0][0],
        "twf_max": finalVelocityTempData[-1][0],
        "Timeseries": finalVelocityTempData,
        "fft_min": finalVelocityFFTData[0][0],
        "fft_max": finalVelocityFFTData[-1][0],
        "FFT": finalVelocityFFTData
    }

def accelerationConvert(data, lr):
    filterCutoff = 4
    filterOrder = 2
    SR, accelerationTimeseriesData = hexTWF(data)
    lrValue = 0
    if type(lr) == list:
        if 262144 < len(accelerationTimeseriesData):
            lrValue = int(51200 * 2.56)
        else:
            lrValue = int(102400 * 2.56)
    else:
        lrValue = int(lr * 2.56)
    accelerationTemp = butterHighpassFilter(accelerationTimeseriesData[0:lrValue], filterCutoff, SR, filterOrder)
    accelerationFFTData = ((FFT(hannData(accelerationTemp))) * 0.707) * 2
    accelerationFFTXData = np.linspace(0.0, SR / 2, num=int(len(accelerationFFTData)))
    accelerationFFTData = np.round(accelerationFFTData, 8)
    finalAccelerationFFTData = [i for i in zip(accelerationFFTXData, accelerationFFTData)]
    v1 = (len(accelerationTimeseriesData) / SR) / len(accelerationTimeseriesData)
    tempAccelerationTemp = np.round(accelerationTemp, 8)
    finalAccelerationTimeseriesData = [[i * v1, accelerationTimeseriesData[i]] for i in range(len(tempAccelerationTemp))]
    return {
        "SR": SR,
        "twf_min": finalAccelerationTimeseriesData[0][0],
        "twf_max": finalAccelerationTimeseriesData[-1][0],
        "Timeseries": finalAccelerationTimeseriesData,
        "fft_min": finalAccelerationFFTData[0][0],
        "fft_max": finalAccelerationFFTData[-1][0],
        "FFT": finalAccelerationFFTData
    }

def accelerationEnvelopeConvert(data):
    filterCutoff = 1
    filterOrder = 5
    SR, timeseries = hexTWF(data)
    aeTimeseriesData = (timeseries - np.mean(timeseries))
    twsValue = np.arange(len(timeseries))
    coeffs = np.polyfit(twsValue, aeTimeseriesData, 1)
    trendline = np.polyval(coeffs, twsValue)
    detrended = aeTimeseriesData - trendline
    detrendedFilter = butterHighpassFilter(detrended, filterCutoff, SR, filterOrder)
    analyticSignal = hilbert(detrendedFilter)
    amplitudeEnvelope = np.abs(analyticSignal)
    x = np.arange(len(amplitudeEnvelope))
    coeffs = np.polyfit(x, amplitudeEnvelope, 1)
    trendline = np.polyval(coeffs, x)
    accelerationEnvelopeTimeseriesData = amplitudeEnvelope - trendline
    accelerationEnvelopeFFTData = FFT(accelerationEnvelopeTimeseriesData)
    accelerationEnvelopeFFTXData = np.linspace(0.0, SR / 2, num=int(len(accelerationEnvelopeFFTData)))
    accelerationEnvelopeFFTData = np.round(accelerationEnvelopeFFTData, 8)
    finalAccelerationEnvelopeFFTData = [i for i in zip(accelerationEnvelopeFFTXData, accelerationEnvelopeFFTData)]
    accelerationEnvelopeTimeseriesData = np.round(np.split(accelerationEnvelopeTimeseriesData, [int(len(accelerationEnvelopeTimeseriesData) * 0.4)])[0], 8).tolist()
    v1 = (len(accelerationEnvelopeTimeseriesData) / SR) / len(accelerationEnvelopeTimeseriesData)
    finalAccelerationEnvelopeTimeseriesData = [[i * v1, accelerationEnvelopeTimeseriesData[i]] for i in range(len(accelerationEnvelopeTimeseriesData))]
    return {
        "SR": SR,
        "twf_min": finalAccelerationEnvelopeTimeseriesData[0][0],
        "twf_max": finalAccelerationEnvelopeTimeseriesData[-1][0],
        "Timeseries": finalAccelerationEnvelopeTimeseriesData,
        "fft_min": finalAccelerationEnvelopeFFTData[0][0],
        "fft_max": finalAccelerationEnvelopeFFTData[-1][0],
        "FFT": finalAccelerationEnvelopeFFTData
    }

def velocityConvertDemo(data, sr, filterValue=(15, 4), callVal=1):
    divideTillFrequency = 5
    divideValue = 5
    timeseries = np.array(data)
    timeseries = timeseries * 9807
    timeStep = 1 / sr
    N = len(timeseries)
    if not filterValue:
        filterCutoff = 15
        filterOrder = 4
    else:
        filterCutoff = filterValue[0]
        filterOrder = filterValue[1]
    time = np.linspace(0.0, N * timeStep, N)
    velocity = integrate.cumtrapz(timeseries, x=time)
    velocityTimeseriesData = (velocity - np.mean(velocity)) * 0.75
    velocityTemp = butterHighpassFilter(velocityTimeseriesData, filterCutoff, sr, filterOrder)
    velocityFFTData = ((FFT(hannData(velocityTemp))) * 0.707) * 2.3
    index = velocityFFTData.argmax()
    velocityFFTData[index] = velocityFFTData[index] * callVal
    velocityFFTXData = np.linspace(0.0, sr / 2, num=int(len(velocityFFTData)))
    indexVal = velocityFFTXData[velocityFFTXData < divideTillFrequency]
    velocityFFTData[:len(indexVal)] /= divideValue
    velocityFFTData = np.round(velocityFFTData, 8)
    finalVelocityFFTData = [i for i in zip(velocityFFTXData, velocityFFTData)]
    velocityTemp = velocityTemp[int(sr * 0.15):]
    v1 = (len(velocityTemp) / sr) / len(velocityTemp)
    velocityTemp = np.round(velocityTemp, 8)
    finalVelocityTempData = [[(i * v1), velocityTemp[i]] for i in range(len(velocityTemp))]
    return {
        "SR": sr,
        "twf_min": finalVelocityTempData[0][0],
        "twf_max": finalVelocityTempData[-1][0],
        "Timeseries": finalVelocityTempData,
        "fft_min": finalVelocityFFTData[0][0],
        "fft_max": finalVelocityFFTData[-1][0],
        "FFT": finalVelocityFFTData
    }

def getOldData(fileName, axis, selectDatetime, dataType="data", limit=5):
    # assuming mongo is a MongoClient instance
    gmt_timezone = settings.GMT_TIMEZONE
    mongo = settings.MONGO_CLIENT
    db = mongo.db
    numberOfPacket = limit
    fileData = []
    if selectDatetime:
        endDateTime = selectDatetime
    else:
        endDateTime = int((datetime.now().astimezone(gmt_timezone)).timestamp())
    rmsData = list(db["RawData"].find({
        "BearingLoactionId": ObjectId(fileName.split('.')[0]),
        "axis": axis,
        "epochTime": {"$lte": endDateTime}
    }).sort([("_id", -1)]).limit(numberOfPacket))
    if len(rmsData) == 0:
        return False
    else:
        for i in range(len(rmsData)):
            fileData += rmsData[i]['data']
    return fileData

def velocityConvertHighResolution(data, sr, nos, filterValue=(15, 4), lowpassFilter=(1000, 2), callVal=1, fmax=None, floorNoisePercentage=1):
    try:
        velocityTimeseriesMms2 = np.array(data[0:nos]) * 9807
        N = len(velocityTimeseriesMms2)
        timeStep = 1 / sr
        time = np.linspace(0.0, N * timeStep, N)
        filterCutoff = filterValue[0]
        filterOrder = filterValue[1]
        velocityTimeseriesMms2 = velocityTimeseriesMms2 - np.mean(velocityTimeseriesMms2)
        velocityTimeseries = integrate.cumtrapz(velocityTimeseriesMms2, x=np.linspace(0.0, len(velocityTimeseriesMms2) * timeStep, len(velocityTimeseriesMms2)))
        velocityTimeseriesForRMS = butterHighpassFilter(velocityTimeseries, filterCutoff, sr, 2)
        velocityTimeseries1 = integrate.cumtrapz(velocityTimeseriesMms2, x=time)
        velocityTimeseries1 = butterHighpassFilter(velocityTimeseries1, filterCutoff, sr, 4)
        velocityFFTData1 = ((FFT(hannData(velocityTimeseries1)))) * 2.1 * 0.707
        velocityFFTData = velocityFFTData1
        velocityFFTXData = np.linspace(0.0, sr / 2, num=int(len(velocityFFTData)))
        velocityFFTData = np.where(velocityFFTData < (np.max(velocityFFTData) * (floorNoisePercentage / 100)), velocityFFTData / 4, velocityFFTData)
        velocityFFTData = np.round(velocityFFTData, 8)
        if fmax != None:
            finalVelocityFFTData = [(x, y) for x, y in zip(velocityFFTXData, velocityFFTData[:len(velocityFFTXData)]) if x <= int(fmax)]
        else:
            finalVelocityFFTData = [i for i in zip(velocityFFTXData, velocityFFTData)]
        v1 = (len(velocityTimeseriesForRMS) / sr) / len(velocityTimeseriesForRMS)
        finalTimeseriesData = np.round(velocityTimeseriesForRMS, 8)
        finalVelocityTempData = [[(i * v1), finalTimeseriesData[i]] for i in range(len(finalTimeseriesData))]
        return {
            "SR": sr,
            "twf_min": finalVelocityTempData[0][0],
            "twf_max": finalVelocityTempData[-1][0],
            "Timeseries": finalVelocityTempData,
            "fft_min": finalVelocityFFTData[0][0],
            "fft_max": finalVelocityFFTData[-1][0],
            "FFT": finalVelocityFFTData
        }
    except Exception as e:
        print(f"Error in velocityConvertHighResolution: {e}")

def accelerationConvertHighResolution(rawData, sr, nos, filterValue=(15, 4), lowpassFilter=(1000, 2), callVal=1, fmax=25):
    try:
        accelerationTimeseries = np.array(rawData)
        accelerationTimeseries = accelerationTimeseries - np.mean(accelerationTimeseries)
        accelerationFFTData = ((FFT(hannData(accelerationTimeseries)))) * 2 * 0.707
        accelerationFFTXData = np.linspace(0.0, sr / 2, num=int(len(accelerationFFTData)))
        accelerationFFTData = np.where(accelerationFFTData < (np.max(accelerationFFTData) * 0.1), accelerationFFTData / 4, accelerationFFTData)
        accelerationFFTData = np.round(accelerationFFTData, 8)
        finalAccelerationFFTData = [(x, y) for x, y in zip(accelerationFFTXData, accelerationFFTData[:len(accelerationFFTXData)]) if x <= int(fmax)]
        v1 = (len(accelerationTimeseries) / sr) / len(accelerationTimeseries)
        finalTimeseriesData = np.round(accelerationTimeseries, 8)
        finalAccelerationTempData = [[(i * v1), finalTimeseriesData[i]] for i in range(len(finalTimeseriesData))]
        return {
            "SR": sr,
            "twf_min": finalAccelerationTempData[0][0],
            "twf_max": finalAccelerationTempData[-1][0],
            "Timeseries": finalAccelerationTempData,
            "fft_min": finalAccelerationFFTData[0][0],
            "fft_max": finalAccelerationFFTData[-1][0],
            "FFT": finalAccelerationFFTData
        }
    except Exception as e:
        print(f"Error in accelerationConvertHighResolution: {e}")

def velocityConvertDemo1(data, sr, filterValue=(15, 4), lowpassFilter=(1000, 2), callVal=1, fmax=None):
    velocityTimeseriesMms2 = np.array(data) * 9807
    N = len(velocityTimeseriesMms2[0:6000])
    timeStep = 1 / sr
    time = np.linspace(0.0, N * timeStep, N)
    if not filterValue:
        filterCutoff = 15
        filterOrder = 4
    else:
        filterCutoff = filterValue[0]
        filterOrder = filterValue[1]
    lowpassFilterCutoff = lowpassFilter[0]
    lowpassFilterOrder = lowpassFilter[1]
    velocityTimeseriesMms2 = velocityTimeseriesMms2 - np.mean(velocityTimeseriesMms2)
    velocityTimeseries = integrate.cumtrapz(velocityTimeseriesMms2, x=np.linspace(0.0, len(velocityTimeseriesMms2) * timeStep, len(velocityTimeseriesMms2)))
    finalVelocityTimeseries = butterHighpassFilter(velocityTimeseries, 50, sr, 2)
    velocityTimeseries1 = integrate.cumtrapz(velocityTimeseriesMms2[0: int(sr * 2)], x=time)
    velocityTimeseries1 = butterHighpassFilter(velocityTimeseries1, filterCutoff, sr, filterOrder)
    velocityTimeseries1 = butterLowpassFilter(velocityTimeseries1, lowpassFilterCutoff, sr, lowpassFilterOrder)
    velocityFFTData1 = ((FFT(hannData(velocityTimeseries1)))) * 2
    velocityTimeseries2 = integrate.cumtrapz(velocityTimeseriesMms2[int(sr * 0.8): int(sr * 2.8)], x=time)
    velocityTimeseries2 = butterHighpassFilter(velocityTimeseries2, filterCutoff, sr, filterOrder)
    velocityTimeseries2 = butterLowpassFilter(velocityTimeseries2, lowpassFilterCutoff, sr, lowpassFilterOrder)
    velocityFFTData2 = ((FFT(hannData(velocityTimeseries2)))) * 2
    velocityTimeseries3 = integrate.cumtrapz(velocityTimeseriesMms2[int(sr * 1.6): int(sr * 3.6)], x=time)
    velocityTimeseries3 = butterHighpassFilter(velocityTimeseries3, filterCutoff, sr, filterOrder)
    velocityTimeseries3 = butterLowpassFilter(velocityTimeseries3, lowpassFilterCutoff, sr, lowpassFilterOrder)
    velocityFFTData3 = ((FFT(hannData(velocityTimeseries3)))) * 2
    velocityTimeseries4 = integrate.cumtrapz(velocityTimeseriesMms2[int(sr * 2.4): int(sr * 4.4)], x=time)
    velocityTimeseries4 = butterHighpassFilter(velocityTimeseries4, filterCutoff, sr, filterOrder)
    velocityTimeseries4 = butterLowpassFilter(velocityTimeseries4, lowpassFilterCutoff, sr, lowpassFilterOrder)
    velocityFFTData4 = ((FFT(hannData(velocityTimeseries4)))) * 2
    velocityFFTData = (velocityFFTData1 + velocityFFTData2 + velocityFFTData3 + velocityFFTData4) / 4
    velocityFFTXData = np.linspace(0.0, sr / 2, num=int(len(velocityFFTData)))
    velocityFFTData = np.where(velocityFFTData < (np.max(velocityFFTData) * 0.2), velocityFFTData / 4, velocityFFTData)
    velocityFFTData[:int(np.where(velocityFFTXData > 4)[0][0])] *= 0.7
    velocityFFTData = np.round(velocityFFTData, 8)
    if fmax is not None:
        finalVelocityFFTData = [(x, y) for x, y in zip(velocityFFTXData, velocityFFTData[:len(velocityFFTXData)]) if x <= int(fmax)]
    else:
        finalVelocityFFTData = [i for i in zip(velocityFFTXData, velocityFFTData)]
    v1 = (len(finalVelocityTimeseries) / sr) / len(finalVelocityTimeseries)
    finalTimeseriesData = np.round(finalVelocityTimeseries, 8)
    finalVelocityTempData = [[(i * v1), finalTimeseriesData[i]] for i in range(len(finalTimeseriesData))]
    return {
            "SR": sr,
            "twf_min": finalVelocityTempData[0][0],
            "twf_max": finalVelocityTempData[-1][0],
            "Timeseries": finalVelocityTempData,
            "fft_min": finalVelocityFFTData[0][0],
            "fft_max": finalVelocityFFTData[-1][0],
            "FFT": finalVelocityFFTData
        }

def accelerationConvertDemo(data, sr, filterValue=(15, 4), callVal=1, fmax=None):
    accelerationTimeseriesData = np.array(data)
    accelerationTimeseriesData = accelerationTimeseriesData - np.mean(accelerationTimeseriesData)
    accelerationFFTData = (FFT(hannData(accelerationTimeseriesData)) * 0.707) * 2.3
    accelerationFFTXData = np.linspace(0.0, sr / 2, num=int(len(accelerationFFTData)))
    if fmax is not None:
        finalAccelerationFFTData = [(x, y) for x, y in zip(accelerationFFTXData, accelerationFFTData[:len(accelerationFFTXData)]) if x <= int(fmax)]
    else:
        finalAccelerationFFTData = [i for i in zip(accelerationFFTXData, accelerationFFTData)]
    v1 = (len(accelerationTimeseriesData) / sr) / len(accelerationTimeseriesData)
    finalAccelerationTimeseriesData = [[i * v1, accelerationTimeseriesData[i]] for i in range(len(accelerationTimeseriesData))]
    return {
        "SR": sr,
        "twf_min": finalAccelerationTimeseriesData[0][0],
        "twf_max": finalAccelerationTimeseriesData[-1][0],
        "Timeseries": finalAccelerationTimeseriesData,
        "fft_min": finalAccelerationFFTData[0][0],
        "fft_max": finalAccelerationFFTData[-1][0],
        "FFT": finalAccelerationFFTData
    }

def accelerationEnvelopeConvertDemo(data, sr, filterValue=(15, 4), callVal=1):
    filterCutoff = 1
    filterOrder = 5
    timeseries = data
    aeTimeseriesData = (timeseries - np.mean(timeseries))
    twsValue = np.arange(len(timeseries))
    coeffs = np.polyfit(twsValue, aeTimeseriesData, 1)
    trendline = np.polyval(coeffs, twsValue)
    detrended = aeTimeseriesData - trendline
    detrendedFilter = butterHighpassFilter(detrended, filterCutoff, sr, filterOrder)
    analyticSignal = hilbert(detrendedFilter)
    amplitudeEnvelope = np.abs(analyticSignal)
    x = np.arange(len(amplitudeEnvelope))
    coeffs = np.polyfit(x, amplitudeEnvelope, 1)
    trendline = np.polyval(coeffs, x)
    accelerationEnvelopeTimeseriesData = amplitudeEnvelope - trendline
    accelerationEnvelopeFFTData = FFT(accelerationEnvelopeTimeseriesData)
    accelerationEnvelopeFFTXData = np.linspace(0.0, sr / 2, num=int(len(accelerationEnvelopeFFTData)))
    accelerationEnvelopeFFTData = np.round(accelerationEnvelopeFFTData, 8)
    finalAccelerationEnvelopeFFTData = [i for i in zip(accelerationEnvelopeFFTXData, accelerationEnvelopeFFTData)]
    accelerationEnvelopeTimeseriesData = np.round(np.split(accelerationEnvelopeTimeseriesData, [int(len(accelerationEnvelopeTimeseriesData) * 0.4)])[0], 8).tolist()
    v1 = (len(accelerationEnvelopeTimeseriesData) / sr) / len(accelerationEnvelopeTimeseriesData)
    finalAccelerationEnvelopeTimeseriesData = [[i * v1, accelerationEnvelopeTimeseriesData[i]] for i in range(len(accelerationEnvelopeTimeseriesData))]
    return {
        "SR": sr,
        "twf_min": finalAccelerationEnvelopeTimeseriesData[0][0],
        "twf_max": finalAccelerationEnvelopeTimeseriesData[-1][0],
        "Timeseries": finalAccelerationEnvelopeTimeseriesData,
        "fft_min": finalAccelerationEnvelopeFFTData[0][0],
        "fft_max": finalAccelerationEnvelopeFFTData[-1][0],
        "FFT": finalAccelerationEnvelopeFFTData
    }

def velocityConvert24Demo(rawData, sr, rpm, cutoff, order, fmax=None, floorNoiseThresholdPercentage=None, floorNoiseAttenuationFactor=None, highResolution=1):
    if 40000 < len(rawData) < 50000:
        overlappingPercentage = 60
    else:
        overlappingPercentage = 80
    if highResolution > 1:
        blockSize = int(20000 * (highResolution / 2))
    else:
        blockSize = 20000
    velocityTimeseriesMms2 = np.array(rawData) * 9807
    N = len(velocityTimeseriesMms2[0:blockSize])
    timeStep = 1 / sr
    time = np.linspace(0.0, N * timeStep, N)
    velocityTimeseriesMms2 = velocityTimeseriesMms2 - np.mean(velocityTimeseriesMms2)
    velocityTimeseries = integrate.cumtrapz(velocityTimeseriesMms2, x=np.linspace(0.0, len(velocityTimeseriesMms2) * timeStep, len(velocityTimeseriesMms2)))
    rmsCutoffValue = max((rpm / 60) * 0.6, 4)
    rmsCutoffValue = math.ceil(rmsCutoffValue)
    rmsCutoffValue = max(rmsCutoffValue, cutoff)
    finalVelocityTimeseries = butterHighpassFilter(velocityTimeseries, rmsCutoffValue, 10000, 2)
    velocityFFTDataList = []
    for i in range(4):
        start = int(i * (1 - (overlappingPercentage / 100)) * blockSize)
        end = start + blockSize
        velocityTimeseriesI = integrate.cumtrapz(velocityTimeseriesMms2[start:end], x=time)
        velocityTimeseriesI = butterHighpassFilter(velocityTimeseriesI, rmsCutoffValue, 10000, 2)
        velocityFFTDataI = ((FFT(hannData(velocityTimeseriesI)))) * 2
        velocityFFTDataList.append(velocityFFTDataI)
    velocityFFTData = sum(velocityFFTDataList) / len(velocityFFTDataList)
    velocityFFTXData = np.linspace(0.0, sr / 2, num=int(len(velocityFFTData)))
    if floorNoiseThresholdPercentage not in (None, 0) and floorNoiseAttenuationFactor not in (None, 0):
        velocityFFTData = np.where(velocityFFTData < (np.max(velocityFFTData) * floorNoiseThresholdPercentage), velocityFFTData / floorNoiseAttenuationFactor, velocityFFTData)
    else:
        velocityFFTData = np.where(velocityFFTData < (np.max(velocityFFTData) * 0.05), velocityFFTData / 1.1, velocityFFTData)
    velocityFFTData[:int(np.where(velocityFFTXData > rmsCutoffValue)[0][0])] *= 0.2
    velocityFFTData[:int(np.where(velocityFFTXData > (rmsCutoffValue * 0.75))[0][0])] *= 0.05
    velocityFFTData = np.round(velocityFFTData, 8)
    if fmax is not None:
        filteredIndices = velocityFFTXData < fmax
        finalVelocityFFTData = list(zip(velocityFFTXData[filteredIndices], velocityFFTData[filteredIndices]))
    else:
        finalVelocityFFTData = list(zip(velocityFFTXData, velocityFFTData))
    v1 = (len(finalVelocityTimeseries) / sr) / len(finalVelocityTimeseries)
    finalTimeseriesData = np.round(finalVelocityTimeseries, 8)
    finalVelocityTempData = [[(i * v1), finalTimeseriesData[i]] for i in range(len(finalTimeseriesData))]
    return {
        "SR": sr,
        "twf_min": finalVelocityTempData[0][0],
        "twf_max": finalVelocityTempData[-1][0],
        "Timeseries": finalVelocityTempData,
        "fft_min": finalVelocityFFTData[0][0],
        "fft_max": finalVelocityFFTData[-1][0],
        "FFT": finalVelocityFFTData
    }

def velocityConvert32Demo(data, sr, fmax=None):
    timeseries = np.array(data)
    filterCutoff = 10
    filterOrder = 4
    timeStep = 1 / sr
    N = len(timeseries)
    time = np.linspace(0.0, N * timeStep, N)
    firstFilterData = butterHighpassFilter(timeseries, filterCutoff, sr, filterOrder)
    mms2Data = firstFilterData * 9807
    integrateData = integrate.cumtrapz(mms2Data, x=time)
    integrateData = np.append(0, integrateData)
    velocityTimeseriesData = (integrateData - np.mean(integrateData)) * 0.75
    secondTimeseriesData = butterHighpassFilter(velocityTimeseriesData, filterCutoff, sr, filterOrder)
    secondTimeseriesData = secondTimeseriesData[int(sr * 0.2): int(sr - sr * 0.2)]
    finalFFT = FFT(hannData(secondTimeseriesData))
    velocityFFTData = ((np.array(finalFFT)) * 0.707) * 2.1
    velocityFFTXData = np.linspace(0.0, sr / 2, num=int(len(velocityFFTData)))
    velocityFFTData = np.round(velocityFFTData, 8)
    if fmax is not None:
        filteredIndices = velocityFFTXData < fmax
        finalVelocityFFTData = list(zip(velocityFFTXData[filteredIndices], velocityFFTData[filteredIndices]))
    else:
        finalVelocityFFTData = list(zip(velocityFFTXData, velocityFFTData))
    v1 = (len(secondTimeseriesData) / sr) / len(secondTimeseriesData)
    finalTimeseriesData = np.round(secondTimeseriesData, 8)
    finalVelocityTempData = [[(i * v1), finalTimeseriesData[i]] for i in range(len(finalTimeseriesData))]
    return {
        "SR": sr,
        "twf_min": finalVelocityTempData[0][0],
        "twf_max": finalVelocityTempData[-1][0],
        "Timeseries": finalVelocityTempData,
        "fft_min": finalVelocityFFTData[0][0],
        "fft_max": finalVelocityFFTData[-1][0],
        "FFT": finalVelocityFFTData
    }

def accelerationConvert32Demo(data, sr, fmax=None):
    accelerationTimeseriesData = np.array(data)
    filterCutoff = 10
    filterOrder = 4
    firstFilterData = butterHighpassFilter(accelerationTimeseriesData, filterCutoff, sr, filterOrder)
    accelerationFFTData = (FFT(hannData(firstFilterData)) * 0.707) * 2.1
    accelerationFFTXData = np.linspace(0.0, sr / 2, num=int(len(accelerationFFTData)))
    if fmax is not None:
        filteredIndices = accelerationFFTXData < fmax
        finalAccelerationFFTData = list(zip(accelerationFFTXData[filteredIndices], accelerationFFTData[filteredIndices]))
    else:
        finalAccelerationFFTData = list(zip(accelerationFFTXData, accelerationFFTData))
    accelerationTimeseriesData = accelerationTimeseriesData[int(len(accelerationTimeseriesData) * 0.1):]
    v1 = (len(accelerationTimeseriesData) / sr) / len(accelerationTimeseriesData)
    finalAccelerationTimeseriesData = [[i * v1, accelerationTimeseriesData[i]] for i in range(len(accelerationTimeseriesData))]
    return {
        "SR": sr,
        "twf_min": finalAccelerationTimeseriesData[0][0],
        "twf_max": finalAccelerationTimeseriesData[-1][0],
        "Timeseries": finalAccelerationTimeseriesData,
        "fft_min": finalAccelerationFFTData[0][0],
        "fft_max": finalAccelerationFFTData[-1][0],
        "FFT": finalAccelerationFFTData
    }

def accelerationEnvelopeConvert32Demo(data, sr, fmax=None):
    filterCutoff = 4
    filterOrder = 4
    timeseries = data
    aeTimeseriesData = (timeseries - np.mean(timeseries))
    twsValue = np.arange(len(timeseries))
    coeffs = np.polyfit(twsValue, aeTimeseriesData, 1)
    trendline = np.polyval(coeffs, twsValue)
    detrended = aeTimeseriesData - trendline
    detrendedFilter = butterHighpassFilter(detrended, filterCutoff, sr, filterOrder)
    analyticSignal = hilbert(detrendedFilter)
    amplitudeEnvelope = np.abs(analyticSignal)
    x = np.arange(len(amplitudeEnvelope))
    coeffs = np.polyfit(x, amplitudeEnvelope, 1)
    trendline = np.polyval(coeffs, x)
    accelerationEnvelopeTimeseriesData = amplitudeEnvelope - trendline
    accelerationEnvelopeFFTData = FFT(accelerationEnvelopeTimeseriesData)
    accelerationEnvelopeFFTXData = np.linspace(0.0, sr / 2, num=int(len(accelerationEnvelopeFFTData)))
    accelerationEnvelopeFFTData = np.round(accelerationEnvelopeFFTData, 8)
    if fmax is not None:
        filteredIndices = accelerationEnvelopeFFTXData < fmax
        finalAccelerationEnvelopeFFTData = list(zip(accelerationEnvelopeFFTXData[filteredIndices], accelerationEnvelopeFFTData[filteredIndices]))
    else:
        finalAccelerationEnvelopeFFTData = list(zip(accelerationEnvelopeFFTXData, accelerationEnvelopeFFTData))
    accelerationEnvelopeTimeseriesData = np.round(np.split(accelerationEnvelopeTimeseriesData, [int(len(accelerationEnvelopeTimeseriesData) * 0.4)])[0], 8).tolist()
    v1 = (len(accelerationEnvelopeTimeseriesData) / sr) / len(accelerationEnvelopeTimeseriesData)
    finalAccelerationEnvelopeTimeseriesData = [[i * v1, accelerationEnvelopeTimeseriesData[i]] for i in range(len(accelerationEnvelopeTimeseriesData))]
    return {
        "SR": sr,
        "twf_min": finalAccelerationEnvelopeTimeseriesData[0][0],
        "twf_max": finalAccelerationEnvelopeTimeseriesData[-1][0],
        "Timeseries": finalAccelerationEnvelopeTimeseriesData,
        "fft_min": finalAccelerationEnvelopeFFTData[0][0],
        "fft_max": finalAccelerationEnvelopeFFTData[-1][0],
        "FFT": finalAccelerationEnvelopeFFTData
    }

def check_values_near(value1, value2, threshold_value, threshold_percentage=200):
    return abs(value1 - value2) <= threshold_value

def audioData(audio_data, threshold_percentage=15):
    index_value = 0
    if audio_data[0] < 0:
        for value in audio_data:
            if value > 0:
                index_value = audio_data.index(value)
                break
    elif audio_data[0] > 0:
        for value in audio_data:
            if value < 0:
                index_value = audio_data.index(value)
                break
    if index_value is not None:
        length_of_data = len(audio_data)
        offset = int((threshold_percentage / 100) * length_of_data)
        next_index_value = index_value + offset
        max_value = max(audio_data[next_index_value:]) * 0.1
        final_index_value = 0
        if audio_data[next_index_value] < 0:
            for value in audio_data[next_index_value:]:
                if value > 0:
                    final_index_value = audio_data.index(value)
                    break
        elif audio_data[next_index_value] > 0:
            for value in audio_data[next_index_value:]:
                if value < 0:
                    final_index_value = audio_data.index(value)
                    break
        if final_index_value >= length_of_data:
            final_index_value = length_of_data - 1
        last_index = -1
        while True:
            if check_values_near(audio_data[final_index_value], audio_data[last_index], max_value):
                break
            else:
                last_index = last_index - 1
        return audio_data[final_index_value:last_index]

def Audio(sr, timeseries, file, audio_directory):
    scaled = np.int16(timeseries / np.max(np.abs(timeseries)) * 32767)
    write(audio_directory + file + '.wav', sr, scaled)

def check_file_exists(file_name):
    file_path = os.path.join(settings.PARQUET_PATH, file_name)
    return os.path.exists(file_path)

def read_from_parquet(file_name, start_time, end_time=None, limit=None, axis=None):
    filters = [('timestamp', '==', start_time)]
    if axis is not None:
        filters += [('axis', '==', axis)]
    if not check_file_exists(file_name):
        return pd.DataFrame()
    try:
        if start_time is not None and end_time is not None:
            filters = [('timestamp', '>=', start_time), ('timestamp', '<=', end_time)]
            if axis is not None:
                filters += [('axis', '==', axis)]
        filtered_chunks = pq.read_table(os.path.join(settings.PARQUET_PATH, file_name), filters=filters)
        df = filtered_chunks.to_pandas()
        if limit is not None:
            df = df.tail(limit)
        return df
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return pd.DataFrame()
    
def check_new_file_exists(new_file_name, machine_id):
    machine_data = settings.MONGO_DB["Machine"].find_one({"_id": ObjectId(machine_id)})
    folder_path = os.path.join(settings.NEW_PQ_DIR, str(machine_data["customerId"]), str(machine_data["areaId"]), str(machine_data["subAreaId"]), str(machine_id))
    file_path = os.path.join(folder_path, new_file_name)
    return os.path.exists(file_path)

def read_from_new_parquet(file_name, machine_id, start_time, end_time=None, limit=None, axis=None, analytics_type=None):
    try:
        machine_data = settings.MONGO_DB["Machine"].find_one({"_id": ObjectId(machine_id)})
        folder_path = os.path.join(settings.NEW_PQ_DIR, str(machine_data["customerId"]), str(machine_data["areaId"]), str(machine_data["subAreaId"]), str(machine_id))
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return pd.DataFrame()

    filters = [('timestamp', '==', start_time)]
    if axis is not None:
        filters += [('axis', '==', axis)]
    if analytics_type is not None:
        filters += [('analyticsType', '==', analytics_type)]

    if not check_new_file_exists(folder_path, file_name):
        return pd.DataFrame()

    try:
        if start_time is not None and end_time is not None:
            filters = [('timestamp', '>=', start_time), ('timestamp', '<=', end_time)]
            if axis is not None:
                filters += [('axis', '==', axis)]
            if analytics_type is not None:
                filters += [('analyticsType', '==', analytics_type)]
        
        file_path = os.path.join(folder_path, file_name)
        filtered_chunks = pq.read_table(file_path, filters=filters)
        df = filtered_chunks.to_pandas()
        if limit is not None:
            df = df.tail(limit)
        return df
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return pd.DataFrame()

def update_field_in_parquet(file_name, machine_id, timestamp=None, cutoff=None, floor_noise_threshold_percentage=None, floor_noise_attenuation_factor=None):
    try:
        machine_data = settings.MONGO_DB["Machine"].find_one({"_id": ObjectId(machine_id)})
        folder_path = os.path.join(settings.NEW_PQ_DIR, str(machine_data["customerId"]), str(machine_data["areaId"]), str(machine_data["subAreaId"]), str(machine_id))
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return False

    file_path = os.path.join(folder_path, file_name)
    if not os.path.exists(file_path):
        print("Parquet file not found.")
        return False

    # Load Parquet into DataFrame
    df = pq.read_table(file_path).to_pandas()

    # Determine which rows to update
    if timestamp is not None:
        match_mask = df['timestamp'] == timestamp
        matched_count = match_mask.sum()
    else:
        # Update the row with the maximum timestamp (latest entry)
        latest_idx = df['timestamp'].idxmax()
        match_mask = pd.Series([False] * len(df))
        match_mask.iloc[latest_idx] = True
        matched_count = 1
        timestamp = df.loc[latest_idx, 'timestamp']  # for logging

    if matched_count == 0:
        print(f"No records found with timestamp = {timestamp}")
        return False

    updates = {
        'cutoff': cutoff,
        'floorNoiseThresholdPercentage': floor_noise_threshold_percentage,
        'floorNoiseAttenuationFactor': floor_noise_attenuation_factor
    }

    for field, value in updates.items():
        if value is not None:
            if field in df.columns:
                df.loc[match_mask, field] = value
            else:
                print(f"Field '{field}' does not exist in the dataset. Skipping.")

    for field in ['cutoff', 'floorNoiseThresholdPercentage', 'floorNoiseAttenuationFactor']:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce')

    # Write back to Parquet
    table = pa.Table.from_pandas(df)
    pq.write_table(table, file_path, compression='GZIP')
    print(f"Updated {match_mask.sum()} record(s) in {file_path}")
    return True

def append_parquet_data(df):
    appended_data = []
    for _, row in df.iterrows():
        try:
            raw_data = row['data']
            if isinstance(raw_data, bytes):
                parsed_data = [float(x) for x in raw_data.decode('utf-8').strip('[]').split(',')]
            elif isinstance(raw_data, str):
                parsed_data = [float(x) for x in raw_data.strip('[]').split(',')]
            else:
                print(f"Unsupported data type: {type(raw_data)}")
                continue
            appended_data.extend(parsed_data)
        except Exception as e:
            print(f"Error processing row: {row}. Error: {e}")
    return appended_data

def get_latest_data(rawData, axis):
    axis_mapping = {
        "H": "H",
        "V": "V",
        "A": "A"
    }

    axis_data = {}

    for index, row in rawData.iterrows():
        axis_key = next(iter(json.loads(row['data']).keys()))
        axis_data[axis_key] = row

    return axis_data.get(axis_mapping[axis])