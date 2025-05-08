from django.conf import settings
from django.http import JsonResponse
from screen_views.constants import *
import numpy as np
from screen_views.utils import *
import json
import base64
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, timezone

# Access settings
audio_directory = settings.AUDIO_DIRECTORY
# mongo_uri = settings.MONGO_URI

def process_data(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))
    nos = int(request.GET.get('nos', 1024))

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = velocityConvertHighResolution(file_data, sr, nos)
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_acceleration_data(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))
    nos = int(request.GET.get('nos', 1024))

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = accelerationConvertHighResolution(file_data, sr, nos)
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_velocity_data(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = velocityConvertDemo1(file_data, sr)
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_acceleration_data(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = accelerationConvertDemo(file_data, sr)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'No data found'})

def process_acceleration_envelope_data(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = accelerationEnvelopeConvertDemo(file_data, sr)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_velocity_data_24(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))
    rpm = float(request.GET.get('rpm', 0))
    cutoff = float(request.GET.get('cutoff', 0))
    order = int(request.GET.get('order', 2))
    fmax = request.GET.get('fmax')
    if fmax:
        fmax = float(fmax)
    floor_noise_threshold_percentage = request.GET.get('floor_noise_threshold_percentage')
    if floor_noise_threshold_percentage:
        floor_noise_threshold_percentage = float(floor_noise_threshold_percentage)
    floor_noise_attenuation_factor = request.GET.get('floor_noise_attenuation_factor')
    if floor_noise_attenuation_factor:
        floor_noise_attenuation_factor = float(floor_noise_attenuation_factor)
    high_resolution = int(request.GET.get('high_resolution', 1))

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = velocityConvert24Demo(file_data, sr, rpm, cutoff, order, fmax, floor_noise_threshold_percentage, floor_noise_attenuation_factor, high_resolution)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_velocity_data_32(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))
    fmax = request.GET.get('fmax')
    if fmax:
        fmax = float(fmax)

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = velocityConvert32Demo(file_data, sr, fmax)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_acceleration_data_32(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))
    fmax = request.GET.get('fmax')
    if fmax:
        fmax = float(fmax)

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = accelerationConvert32Demo(file_data, sr, fmax)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_acceleration_envelope_data_32(request):
    file_name = request.GET.get('file_name')
    axis = request.GET.get('axis')
    select_datetime = request.GET.get('select_datetime')
    if select_datetime:
        select_datetime = int(select_datetime)
    sr = int(request.GET.get('sr', 2560))
    fmax = request.GET.get('fmax')
    if fmax:
        fmax = float(fmax)

    file_data = getOldData(file_name, axis, select_datetime)
    if file_data:
        result = accelerationEnvelopeConvert32Demo(file_data, sr, fmax)
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'No data found'})
    
def process_audio(request):
    audio_data = np.random.rand(1000)  # replace with actual audio data
    processed_audio_data = audioData(audio_data.tolist())
    sr = 44100  # sample rate
    file_name = 'audio_file'
    audio_directory = 'path_to_audio_directory/'
    Audio(sr, np.array(processed_audio_data), file_name, audio_directory)
    return JsonResponse({'message': 'Audio processed successfully'})

def get_parquet_data(request):
    file_name = request.GET.get('file_name')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    limit = request.GET.get('limit')
    axis = request.GET.get('axis')
    
    if limit is not None:
        limit = int(limit)
    
    df = read_from_parquet(file_name, start_time, end_time, limit, axis)
    data = df.to_dict(orient='records')
    return JsonResponse({'data': data})

def get_new_parquet_data(request):
    file_name = request.GET.get('file_name')
    machine_id = request.GET.get('machine_id')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    limit = request.GET.get('limit')
    axis = request.GET.get('axis')
    analytics_type = request.GET.get('analytics_type')

    if limit is not None:
        limit = int(limit)

    try:
        df = read_from_new_parquet(file_name, machine_id, start_time, end_time, limit, axis, analytics_type)
        data = df.to_dict(orient='records')
        return JsonResponse({'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
def update_parquet_field(request):
    file_name = request.GET.get('file_name')
    machine_id = request.GET.get('machine_id')
    timestamp = request.GET.get('timestamp')
    cutoff = request.GET.get('cutoff')
    floor_noise_threshold_percentage = request.GET.get('floor_noise_threshold_percentage')
    floor_noise_attenuation_factor = request.GET.get('floor_noise_attenuation_factor')

    try:
        result = update_field_in_parquet(file_name, machine_id, timestamp, cutoff, floor_noise_threshold_percentage, floor_noise_attenuation_factor)
        return JsonResponse({'success': result})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
def my_view(request):
    # Assuming df is DataFrame
    df = pd.DataFrame({'data': ['[1.0, 2.0, 3.0]', '[4.0, 5.0, 6.0]']})
    appended_data = append_parquet_data(df)
    return JsonResponse({'data': appended_data})

@csrf_exempt
@require_http_methods(['POST'])
def start_audio(request):
    try:
        data = json.loads(request.body)
        db = settings.MONGO_DB
        print("audio: ", data)
        date_Time = 0
        latest = False

        start_date_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        axis_mapping = {
            "H-Axis": "H",
            "V-Axis": "V",
            "A-Axis": "A"
        }

        if "date_Time" not in data:
            end_date_Time = int(datetime.now().timestamp())
            epoch_Data = list(db["ParameterTrend"].find({
                "BearingLoactionId": data["Sensor_Name"],
                "axis": axis_mapping[data["Axis_Id"]],
                "rawDataPresent": True,
                "epochTime": {"$gte": int(start_date_time.timestamp()), "$lte": end_date_Time}
            }).sort([("_id", -1)]).limit(1))

            if epoch_Data:
                epoch_Date_Time = epoch_Data[0]["epochTime"]
            else:
                epoch_Data = datetime.now() + timedelta(days=-2)
                epoch_Date_Time = int(epoch_Data.timestamp())
            latest = True
        else:
            epoch_Date_Time = data["date_Time"]

        data_date_time = datetime.utcfromtimestamp(int(str(epoch_Date_Time)))
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": data["Sensor_Name"]})
        File_Data = []
        axis_Name = data["Axis_Id"]

        if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
            if latest:
                start_date_Time = int((datetime.now() + timedelta(days=-int(365))).timestamp())
            if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", start_date_Time, end_date_Time, limit=1)
            elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                All_History = read_from_new_parquet(data["Sensor_Name"] + ".parquet", data['Machine_Name'], start_date_Time, end_date_Time, limit=1)

            for index, row in All_History.iterrows():
                axis_Name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"
        else:
            if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", int(epoch_Date_Time))
            elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                All_History = read_from_new_parquet(data["Sensor_Name"] + ".parquet", data['Machine_Name'], int(epoch_Date_Time))

        if All_History.empty:
            return JsonResponse({"Response": "Data not Found"}, status=404)

        for index, row in All_History.iterrows():
            File_Data = json.loads(row['data'])[axis_mapping[axis_Name]]
            date_Time = int(epoch_Date_Time)
            SR_VALUE = 10000
            File_Data = audioData(File_Data)
            audio_data = File_Data

        file = str(date_Time) + "_" + data["Sensor_Name"]
        Audio(SR_VALUE, audio_data, file)
        with open(settings.AUDIO_DIRECTORY + file + '.wav', "rb") as binary_file:
            audio_data = binary_file.read()
        base64_audio = base64.b64encode(audio_data).decode('UTF-8')
        os.remove(settings.AUDIO_DIRECTORY + file + '.wav')

        response_data = {'audio_data': base64_audio}
        return JsonResponse(response_data)
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        return JsonResponse({"Response": "Data not Found"}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def start_timeseries(request):
    try:
        data = json.loads(request.body)
        db = settings.MONGO_DB
        print("timeseries: ", data)
        latest = False

        start_date_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        axis_mapping = {
            "H-Axis": "H",
            "V-Axis": "V",
            "A-Axis": "A"
        }

        if "date_Time" not in data:
            end_date_Time = int(datetime.now().timestamp())
            epoch_Data = list(db["ParameterTrend"].find({
                "BearingLoactionId": data["Sensor_Name"],
                "axis": axis_mapping[data["Axis_Id"]],
                "rawDataPresent": True,
                "epochTime": {"$gte": int(start_date_time.timestamp()), "$lte": end_date_Time}
            }).sort([("_id", -1)]).limit(1))

            if epoch_Data:
                epoch_Date_Time = epoch_Data[0]["epochTime"]
            else:
                epoch_Data = datetime.now() + timedelta(days=-2)
                epoch_Date_Time = int(epoch_Data.timestamp())
            latest = True
        else:
            epoch_Date_Time = data["date_Time"]

        data_date_time = datetime.utcfromtimestamp(int(str(epoch_Date_Time)))
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": data["Sensor_Name"]})
        MachineDatas = db["Machine"].find_one({"_id": data["Machine_Name"]})
        RespondData = []
        File_Data = []
        axis_Name = data["Axis_Id"]
        if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
            if latest:
                start_date_Time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-int(365))).timestamp())
                if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                    All_History = read_from_parquet(data["Sensor_Name"]+".parquet", start_date_Time, end_date_Time, limit = 1)
                elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                    All_History = read_from_new_parquet(data["Sensor_Name"]+".parquet", data['Machine_Name'], start_date_Time, end_date_Time, limit = 1)

                for index, row in All_History.iterrows():
                    axis_Name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"

            else:
                if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                    All_History = read_from_parquet(data["Sensor_Name"]+".parquet", int(epoch_Date_Time))
                elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                    All_History = read_from_new_parquet(data["Sensor_Name"]+".parquet", data['Machine_Name'], int(epoch_Date_Time))

            if All_History.empty:
                return {"Response": "Data not Found!"}, 404
            
            for index, row in All_History.iterrows():

                File_Data = json.loads(row['data'])[axis_mapping[axis_Name]]
                epoch_Date_Time = row['timestamp']
                if 'SR' in row:
                    if row['SR'] == 'null':
                        SR = 10000
                    else:
                        SR = int(row['SR'])
                    rpm = row['rpm']
                    rpm = row['rpm']
                    fMax = int(row['fMax'])
                    noOfLines = int(row['noOfLines'])
                    cutoff = int(float(row['cutoff']))
                    floorNoiseThresholdPercentage = float(row['floorNoiseThresholdPercentage'])
                    floorNoiseAttenuationFactor = float(row['floorNoiseAttenuationFactor'])


            OfflineDataStore = list(db["OfflineDataStore"].find({ "bearingLocationId": ObjectId(data["Sensor_Name"]), "epochTime": epoch_Date_Time }))
            if OfflineDataStore:
                OfflineDataStore = OfflineDataStore[0]
            else:
                OfflineDataStore = {}
            if len(File_Data) != 30000 and 'datatype' in OfflineDataStore and OfflineDataStore['datatype'] in ['24bit', '24bit-13C']:
                SR_VALUE = OfflineDataStore['sr']
                if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                    SR_VALUE = OfflineDataStore['sr']
                    rpm = MachineDatas['rpm']
                    cutoff = bearingLocationDatas['velocity']['highpassCutoffFrequencyFft']
                    fMax = None
                    floorNoiseThresholdPercentage = 5
                    floorNoiseAttenuationFactor = 1

                else:
                    SR_VALUE = SR
                    rpm = rpm
                    cutoff = cutoff
                    
                if data["Type"] == 'Velocity':
                    RespondData = velocityConvert24Demo(File_Data, SR_VALUE,  rpm, cutoff, bearingLocationDatas['velocity']['highpassOrderFft'], fmax = fMax, floorNoiseThresholdPercentage=floorNoiseThresholdPercentage, floorNoiseAttenuationFactor=floorNoiseAttenuationFactor)
                    # RespondData = velocityConvert24Demo(File_Data, SR_VALUE,  MachineDatas['rpm'], bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'])
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            elif 'datatype' in OfflineDataStore and OfflineDataStore['datatype'] == '32bit':
                SR_VALUE = OfflineDataStore['sr']
                if data["Type"] == 'Velocity':
                    RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            else:
                SR_VALUE = 20000
                if data["Type"] == 'Velocity':
                    RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
        else:
            if time_difference.total_seconds() > 0:
                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    fullFileData = list(db["RawData"].find({ "BearingLoactionId": ObjectId(data["Sensor_Name"]), "axis": axis_mapping[data["Axis_Id"]], "epochTime": epoch_Date_Time }))
                    SR_VALUE = fullFileData[0].get('SR', 3000)
                    File_Data = fullFileData[0]['data']

                    if bearingLocationDatas['velocity']['calibrationValue']['h'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['v'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['a'] != 1:
                        File_Data = np.array(File_Data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[data["Axis_Id"]].lower()] 

                    SR_VALUE = 3000
                    if data["Type"] == 'Velocity':
                        RespondData = velocityConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']))
                    elif data["Type"] == 'Acceleration':
                        RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],bearingLocationDatas['acceleration']['highpassOrderFft']))
                    elif data["Type"] == 'Acceleration Envelope':
                        RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))

            else:
                
                if check_file_exists(data["Sensor_Name"]+".parquet"):
                    if latest:
                        start_date_Time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-int(365))).timestamp())
                        All_History = read_from_parquet(data["Sensor_Name"]+".parquet", start_date_Time, end_date_Time, limit = 1)
                        
                        for index, row in All_History.iterrows():
                            axis_Name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"

                    else:
                        All_History = read_from_parquet(data["Sensor_Name"]+".parquet", int(epoch_Date_Time))
            
                    if All_History.empty:
                        return {"Response": "Data not Found"}, 404
                    
                    if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                        for index, row in All_History.iterrows():
                            File_Data = json.loads(row["data"])
                            if data["Axis_Id"] == "H-Axis" and row["axis"] == "H":
                                File_Data = json.loads(row["data"])
                            elif data["Axis_Id"] == "V-Axis" and row["axis"] == "V":
                                File_Data = json.loads(row["data"])
                            if data["Axis_Id"] == "A-Axis" and row["axis"] == "A":
                                File_Data = json.loads(row["data"])
                                
                        if bearingLocationDatas['velocity']['calibrationValue']['h'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['v'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['a'] != 1:
                            File_Data = np.array(File_Data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[data["Axis_Id"]].lower()] 

                        SR_VALUE = 3000
                        if data["Type"] == 'Velocity':
                            RespondData = velocityConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']))
                        elif data["Type"] == 'Acceleration':
                            RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],bearingLocationDatas['acceleration']['highpassOrderFft']))
                        elif data["Type"] == 'Acceleration Envelope':
                            RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))
        keys_to_remove = ['FFT', 'fft_max', 'fft_min']
        for key in keys_to_remove:
            RespondData.pop(key, None)

        if "date_Time" not in data:
            RespondData["epochTime"] = epoch_Date_Time

        return JsonResponse(RespondData, status=200)
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        return JsonResponse({"Response": "Data not Found"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_fft1(request):
    try:
        data = json.loads(request.body)
        print("fft:", data)

        latest = False
        start_date_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=timezone.utc)
        axis_mapping = {
            "H-Axis": "H",
            "V-Axis": "V",
            "A-Axis": "A"
        }

        if "date_Time" not in data:
            end_date_Time = int(datetime.now(tz=settings.GMT_TIMEZONE).timestamp())
            epoch_Data = list(db["ParameterTrend"].find({
                "BearingLoactionId": ObjectId(data["Sensor_Name"]),
                "axis": axis_mapping[data["Axis_Id"]],
                "rawDataPresent": True,
                "epochTime": {"$gte": int(start_date_time.timestamp()), "$lte": end_date_Time}
            }).sort([("_id", -1)]).limit(1))

            if epoch_Data:
                epoch_Date_Time = epoch_Data[0]["epochTime"]
            else:
                epoch_Date_Time = int((datetime.utcnow() - timedelta(days=2)).timestamp())
                latest = True
        else:
            epoch_Date_Time = data["date_Time"]

        data_date_time = datetime.fromtimestamp(int(epoch_Date_Time), tz=timezone.utc)
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["Sensor_Name"])})
        MachineDatas = db["Machine"].find_one({"_id": ObjectId(data["Machine_Name"])})

        RespondData = {}
        File_Data = []
        axis_Name = data["Axis_Id"]

        # Handle offline
        if bearingLocationDatas.get("bearingLocationType") == "OFFLINE":
            end_date_Time = int(datetime.now(tz=settings.GMT_TIMEZONE).timestamp())
            if latest:
                start_date_Time = int((datetime.now(tz=settings.GMT_TIMEZONE) - timedelta(days=365)).timestamp())
                All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", start_date_Time, end_date_Time, limit=1)
                for _, row in All_History.iterrows():
                    axis_Name = list(json.loads(row["data"]).keys())[0] + "-Axis"
            else:
                All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", int(epoch_Date_Time))

            if All_History.empty:
                return JsonResponse({"Response": "Data not Founda1"}, status=404)

            for _, row in All_History.iterrows():
                File_Data = json.loads(row["data"])[axis_mapping[axis_Name]]
                epoch_Date_Time = row["timestamp"]

            OfflineDataStore = db["OfflineDataStore"].find_one({
                "bearingLocationId": ObjectId(data["Sensor_Name"]),
                "epochTime": epoch_Date_Time
            }) or {}

            SR_VALUE = OfflineDataStore.get("sr", 20000)
            dtype = OfflineDataStore.get("datatype", "")

            if len(File_Data) != 30000 and dtype in ["24bit", "24bit-13C"]:
                if data["Type"] == "Velocity":
                    RespondData = velocityConvert24Demo(File_Data, SR_VALUE, MachineDatas["rpm"], bearingLocationDatas["velocity"]["highpassCutoffFrequencyFft"], bearingLocationDatas["velocity"]["highpassOrderFft"])
                elif data["Type"] == "Acceleration":
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == "Acceleration Envelope":
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            elif dtype == "32bit":
                if data["Type"] == "Velocity":
                    RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == "Acceleration":
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == "Acceleration Envelope":
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            else:
                # Default SR_VALUE
                if data["Type"] == "Velocity":
                    RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == "Acceleration":
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == "Acceleration Envelope":
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)

        else:
            # Handle online
            if time_difference.total_seconds() > 0:
                fullFileData = list(db["RawData"].find({
                    "BearingLoactionId": ObjectId(data["Sensor_Name"]),
                    "axis": axis_mapping[data["Axis_Id"]],
                    "epochTime": epoch_Date_Time
                }))

                if not fullFileData:
                    return JsonResponse({"Response": "No raw data found"}, status=404)

                file = fullFileData[0]
                File_Data = file["data"]
                SR_VALUE = file.get("SR", 3000)

                if len(File_Data) > 25000:
                    SR_VALUE = 10000
                    if data["Type"] == "Velocity":
                        RespondData = velocityConvert24Demo(File_Data, SR_VALUE, MachineDatas["rpm"], bearingLocationDatas["velocity"]["highpassCutoffFrequencyFft"], bearingLocationDatas["velocity"]["highpassOrderFft"])
                    elif data["Type"] == "Acceleration":
                        RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                    elif data["Type"] == "Acceleration Envelope":
                        RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
                else:
                    if data["Type"] == "Velocity":
                        RespondData = velocityConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas["velocity"]["highpassCutoffFrequencyFft"], bearingLocationDatas["velocity"]["highpassOrderFft"]))
                    elif data["Type"] == "Acceleration":
                        RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas["acceleration"]["highpassCutoffFrequencyFft"], bearingLocationDatas["acceleration"]["highpassOrderFft"]))
                    elif data["Type"] == "Acceleration Envelope":
                        RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas["accelerationEnvelope"]["highpassCutoffFrequencyFft"], bearingLocationDatas["accelerationEnvelope"]["highpassOrderFft"]))
            else:
                if check_file_exists(data["Sensor_Name"] + ".parquet"):
                    if latest:
                        start_date_Time = int((datetime.now(tz=settings.GMT_TIMEZONE) - timedelta(days=365)).timestamp())
                        All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", start_date_Time, end_date_Time, limit=1)
                        for _, row in All_History.iterrows():
                            axis_Name = list(json.loads(row["data"]).keys())[0] + "-Axis"
                    else:
                        All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", int(epoch_Date_Time))

                    if All_History.empty:
                        return JsonResponse({"Response": "Data not Found"}, status=404)

                    for _, row in All_History.iterrows():
                        File_Data = json.loads(row["data"])[axis_mapping[data["Axis_Id"]]]
                        epoch_Date_Time = row["timestamp"]

                    if len(File_Data) > 25000:
                        SR_VALUE = 10000
                        if data["Type"] == "Velocity":
                            RespondData = velocityConvert24Demo(File_Data, SR_VALUE, MachineDatas["rpm"], bearingLocationDatas["velocity"]["highpassCutoffFrequencyFft"], bearingLocationDatas["velocity"]["highpassOrderFft"])
                        elif data["Type"] == "Acceleration":
                            RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                        elif data["Type"] == "Acceleration Envelope":
                            RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
                    else:
                        SR_VALUE = 3000
                        if data["Type"] == "Velocity":
                            RespondData = velocityConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas["velocity"]["highpassCutoffFrequencyFft"], bearingLocationDatas["velocity"]["highpassOrderFft"]))
                        elif data["Type"] == "Acceleration":
                            RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas["acceleration"]["highpassCutoffFrequencyFft"], bearingLocationDatas["acceleration"]["highpassOrderFft"]))
                        elif data["Type"] == "Acceleration Envelope":
                            RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas["accelerationEnvelope"]["highpassCutoffFrequencyFft"], bearingLocationDatas["accelerationEnvelope"]["highpassOrderFft"]))

        for key in ['Timeseries', 'twf_max', 'twf_min']:
            RespondData.pop(key, None)

        if "date_Time" not in data:
            RespondData["epochTime"] = epoch_Date_Time

        return JsonResponse(RespondData, safe=False)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"Response": "Data not Found"}, status=500)

from Root.models import *
from django.utils.timezone import now

@csrf_exempt
@require_http_methods(["POST"])
def fft_view(request):
    try:
        data = json.loads(request.body)

        sensor_Name = data.get("Sensor_Name")
        signal_type = data.get("Type")
        axis = data.get("Axis")
        is_offline = data.get("isOffline", False)

        if not sensor_Name or not signal_type or not axis:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        axis_mapping = {
            "H-Axis": "H",
            "V-Axis": "V",
            "A-Axis": "A"
        }

        if axis not in axis_mapping:
            return JsonResponse({"error": "Invalid Axis"}, status=400)

        axis_value = axis_mapping[axis]

        # Simulated bearing location configuration
        bearingLocationDatas = {
            "velocity": {
                "highpassOrderFft": 3,
                "lowpassOrderFft": 3,
                "highpassCutoffFft": 10,
                "lowpassCutoffFft": 10000
            },
            "acceleration": {
                "highpassOrderFft": 3,
                "lowpassOrderFft": 3,
                "highpassCutoffFft": 10,
                "lowpassCutoffFft": 10000
            },
            "envelope": {
                "highpassOrderFft": 3,
                "lowpassOrderFft": 3,
                "highpassCutoffFft": 200,
                "lowpassCutoffFft": 10000
            }
        }

        calibration_value = 1.0
        rpm = 1500
        floor_noise_threshold = 5

        config = bearingLocationDatas.get(signal_type.lower(), {})
        high_pass = config.get("highpassCutoffFft", 10)
        low_pass = config.get("lowpassCutoffFft", 10000)
        high_order = config.get("highpassOrderFft", 3)
        low_order = config.get("lowpassOrderFft", 3)

        if is_offline:
            row = read_from_parquet(sensor_Name, axis_value, signal_type, "Offline")
        else:
            row = read_from_parquet(sensor_Name, axis_value, signal_type, "Online")

        if not row:
            return JsonResponse({"error": "No data found"}, status=404)

        file_data = row['data']
        sample_rate = row['SR']

        if len(file_data) != 30000:
            return JsonResponse({"error": "Insufficient data points"}, status=400)

        # Convert based on signal type
        if signal_type == "Velocity":
            fft_data = velocityConvert24Demo(file_data, sample_rate, rpm, calibration_value, floor_noise_threshold, high_pass, low_pass, high_order, low_order)
        elif signal_type == "Acceleration":
            fft_data = accelerationConvertHighResolution(file_data, sample_rate, rpm, calibration_value, floor_noise_threshold, high_pass, low_pass, high_order, low_order)
        elif signal_type == "Acceleration Envelope":
            fft_data = accelerationEnvelopeConvertDemo(file_data, sample_rate, rpm, calibration_value, floor_noise_threshold, high_pass, low_pass, high_order, low_order)
        else:
            return JsonResponse({"error": "Unsupported signal type"}, status=400)

        current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        return JsonResponse({
            "FFT": fft_data,
            "SR": sample_rate,
            "timestamp": current_time
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_parameter_trends(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("ParameterTrends:", data)
            
            # MongoDB connection setup (assuming you have a connection set up)
            db = client[settings.MONGODB_NAME]

            bearing_location_id = data["Sensor_Name"]
            bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(bearing_location_id)})

            end_date_time = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())

            # Start and End Date Calculation
            if data['days'] <= 1:
                if data['days'] == 0:
                    start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-365)).timestamp())
                    number_of_data = 120
                    # Check for offline bearing location and fetch data accordingly
                    if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                        if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                            All_History = read_from_parquet("RMS_" + bearing_location_id + ".parquet", start_date_time, end_date_time, number_of_data)
                        elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                            All_History = read_from_new_parquet("RMS_" + bearing_location_id + ".parquet", data['Machine_Name'], start_date_time, end_date_time, number_of_data, analyticsType=data['Analytics_Types'])
                elif data['days'] == 1:
                    start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-1)).timestamp())
                    if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                        if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                            All_History = read_from_parquet("RMS_" + bearing_location_id + ".parquet", start_date_time, end_date_time)
                        elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                            All_History = read_from_new_parquet("RMS_" + bearing_location_id + ".parquet", data['Machine_Name'], start_date_time, end_date_time, analyticsType=data['Analytics_Types'])
                else:
                    # Handle additional cases here if necessary
                    pass

            elif data['days'] > 1:
                start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-int(data['days']))).timestamp())
                All_History = read_from_parquet("RMS_" + bearing_location_id + ".parquet", start_date_time, end_date_time)

            # Process Parameter Trend Data
            if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                H, V, A = [], [], []
                for axis in ['H', 'V', 'A']:
                    rms_data = list(db["ParameterTrend"].find({
                        "BearingLoactionId": ObjectId(bearing_location_id),
                        "axis": axis,
                        "epochTime": {"$gte": start_date_time, "$lte": end_date_time}
                    }).sort([("_id", -1)]))
                    
                    # Handle the returned data
                    if rms_data:
                        for rd in rms_data:
                            DATETIME = rd['epochTime']
                            if axis == "H":
                                H.append((DATETIME, rd['data'][data["Type"]], rd['rawDataPresent']))
                            elif axis == "V":
                                V.append((DATETIME, rd['data'][data["Type"]], rd['rawDataPresent']))
                            elif axis == "A":
                                A.append((DATETIME, rd['data'][data["Type"]], rd['rawDataPresent']))
            
            elif 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                # Offline data processing here
                H, V, A = [], [], []
                for row in All_History.iterrows():
                    DATETIME = row['timestamp']
                    rms_data = json.loads(row['data'])
                    for axis in rms_data:
                        if 'AccelerationEnvelope' in rms_data[axis]:
                            rms_data[axis]['Acceleration Envelope'] = rms_data[axis].pop('AccelerationEnvelope')
                    axisKey = next(iter(rms_data.keys()))
                    if axisKey == "H":
                        H.append((DATETIME, rms_data["H"][data["Type"]], fileFind(1)))
                    elif axisKey == "V":
                        V.append((DATETIME, rms_data["V"][data["Type"]], fileFind(1)))
                    elif axisKey == "A":
                        A.append((DATETIME, rms_data["A"][data["Type"]], fileFind(1)))

            # Sort and return the response
            H = sorted(H, key=lambda x: x[0])
            A = sorted(A, key=lambda x: x[0])
            V = sorted(V, key=lambda x: x[0])

            if "all" == data['axis'].lower():
                input_dict = {"H": H, "V": V, "A": A}
                output_list = [{"name": key, "value": value} for key, value in input_dict.items()]
                return JsonResponse(output_list, safe=False)
            elif data['axis'] == "H-Axis":
                return JsonResponse([{"name": "H", "value": H}], safe=False)
            elif data['axis'] == "V-Axis":
                return JsonResponse([{"name": "V", "value": V}], safe=False)
            elif data['axis'] == "A-Axis":
                return JsonResponse([{"name": "A", "value": A}], safe=False)
            else:
                return JsonResponse({"Response": []}, status=404)

        except Exception as e:
            print(traceback.print_exc())
            return JsonResponse({"Response": "Data not Found"}, status=500)
        
@csrf_exempt
@require_http_methods(["POST"])
def start32BitRealTimefft(request):
    data = request.data
    print("RealTimefft : ", data)
    try:
        # Use settings.GMT_TIMEZONE for timezone calculation
        start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-60)).timestamp())
        end_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE)).timestamp())
        
        # Read the data from the Parquet file
        All_History = read_from_parquet(data["Sensor_Name"] + ".parquet", start_date_time, end_date_time, 1)

        # Extract data for the corresponding axis (H, V, A)
        File_Data = None
        for index, row in All_History.iterrows():
            axis_data = json.loads(row['data'])
            axis_key = next(iter(axis_data.keys()))
            if axis_key == "H":
                File_Data = axis_data["H"]
            elif axis_key == "V":
                File_Data = axis_data["V"]
            elif axis_key == "A":
                File_Data = axis_data["A"]
        
        if not File_Data:
            return JsonResponse({"Response": "No valid data found for the specified sensor"}, status=404)

        SR_VALUE = 20000
        # Perform the required conversion based on the Type field
        if data["Type"] == 'Velocity':
            RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
        elif data["Type"] == 'Acceleration':
            RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
        elif data["Type"] == 'Accelerationenvelope':
            RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)

        # Remove unnecessary keys from the result
        keys_to_remove = ['Timeseries', 'twf_max', 'twf_min']
        for key in keys_to_remove:
            RespondData.pop(key, None)

        return JsonResponse(RespondData, status=200)

    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return JsonResponse({"Response": "Data not Found"}, status=500)
        
@csrf_exempt
def start32BitRealTimeValue(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("RealTimeValue:", data)

            old = {
                "AccelerationEnvelope": "6",
                "Acceleration Envelope": "6",
                "Acceleration": "2",
                "Velocity": "0",
                "Temperature": "8"
            }

            machineId = data["Machine_Name"]

            # MongoDB setup
            client = MongoClient(settings.MONGO_URI)
            db = client[settings.MONGODB_NAME]

            bearingLocationDatas = db["BearingLocation"].find({"machineId": ObjectId(machineId)})
            final_data = {"data": {}}

            machine_name = db["Machine"].find_one({"_id": ObjectId(machineId)})
            isoDict = isoStandardGetter(ObjectId(machineId))

            for bearingLocationDatas in bearingLocationDatas:
                if bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                    start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-15)).timestamp())
                    end_date_time = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())
                    file_name = "RMS_" + str(bearingLocationDatas["_id"]) + ".parquet"

                    try:
                        latest_history = read_from_parquet(file_name, start_date_time, end_date_time, 10)
                        H, V, A = {}, {}, {}

                        for index, row in latest_history.iterrows():
                            DATETIME = row['timestamp']
                            parsed_data = json.loads(row['data'])

                            for j in range(3):
                                axis_key = next(iter(parsed_data.keys()))
                                if j == 0 and axis_key == "H":
                                    for key, val in parsed_data["H"].items():
                                        H[old[key]] = {
                                            "value": val,
                                            "status": isoAlertGetter(isoDict=isoDict, value=val)
                                        }
                                    H["file"] = fileFind(1)
                                elif j == 1 and axis_key == "A":
                                    for key, val in parsed_data["A"].items():
                                        A[old[key]] = {
                                            "value": val,
                                            "status": isoAlertGetter(isoDict=isoDict, value=val)
                                        }
                                    A["file"] = fileFind(1)
                                elif j == 2 and axis_key == "V":
                                    for key, val in parsed_data["V"].items():
                                        V[old[key]] = {
                                            "value": val,
                                            "status": isoAlertGetter(isoDict=isoDict, value=val)
                                        }
                                    V["file"] = fileFind(1)

                        DATETIME = DATETIME // 1000 if DATETIME > 10 ** 10 else DATETIME
                        final_data["data"][bearingLocationDatas["name"]] = {
                            "H": {"status": "normal", "value": 0} if not H else H,
                            "V": {"status": "normal", "value": 0} if not V else V,
                            "A": {"status": "normal", "value": 0} if not A else A,
                            "sensorName": bearingLocationDatas["name"],
                            "Date": datetime.utcfromtimestamp(int(DATETIME)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                            "bearingLocationType": "OFFLINE"
                        }
                    except FileNotFoundError:
                        continue  # Skip if file not found

            return JsonResponse(final_data["data"], safe=False)

        except Exception as e:
            print(traceback.print_exc())
            return JsonResponse({"Response": "Data not Found"}, status=500)

@csrf_exempt
def realtime_value_v3(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("RealTimeValue v3:", data)

            machine_id = data.get("Machine_Name")
            sensor_type = data.get("Type")

            if not machine_id or not sensor_type:
                return JsonResponse({"error": "Machine_Name and Type are required."}, status=400)

            client = MongoClient()
            db = client[settings.MONGODB_NAME]

            bearing_locations = db["BearingLocation"].find({"machineId": ObjectId(machine_id)})
            iso_dict = isoStandardGetter(ObjectId(machine_id))
            final_data = {"data": {}}

            for bl in bearing_locations:
                location_type = bl.get('bearingLocationType', 'ONLINE')
                file_name = f"RMS_{bl['_id']}.parquet"
                H, V, A = {}, {}, {}
                DATETIME = None

                start_ts = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=1)).timestamp())
                end_ts = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())
                rows_to_fetch = 1 if location_type == "ONLINE" else 10

                try:
                    df = read_from_parquet(file_name, start_ts, end_ts, rows_to_fetch)
                    if df.empty:
                        continue

                    for _, row in df.iterrows():
                        DATETIME = row['timestamp']

                        if location_type == "ONLINE":
                            H_val = json.loads(row['H'])[sensor_type]
                            V_val = json.loads(row['V'])[sensor_type]
                            A_val = json.loads(row['A'])[sensor_type]
                            H = {"value": H_val, "status": isoAlertGetter(iso_dict, H_val)}
                            V = {"value": V_val, "status": isoAlertGetter(iso_dict, V_val)}
                            A = {"value": A_val, "status": isoAlertGetter(iso_dict, A_val)}
                        else:  # OFFLINE
                            data_json = json.loads(row['data'])
                            if "H" in data_json:
                                val = data_json["H"][sensor_type]
                                H = {"value": val, "status": isoAlertGetter(iso_dict, val)}
                            elif "V" in data_json:
                                val = data_json["V"][sensor_type]
                                V = {"value": val, "status": isoAlertGetter(iso_dict, val)}
                            elif "A" in data_json:
                                val = data_json["A"][sensor_type]
                                A = {"value": val, "status": isoAlertGetter(iso_dict, val)}

                    if DATETIME:
                        DATETIME = DATETIME // 1000 if DATETIME > 10**10 else DATETIME
                        final_data["data"][bl["name"]] = {
                            "H": H if H else {"value": 0, "status": "normal"},
                            "V": V if V else {"value": 0, "status": "normal"},
                            "A": A if A else {"value": 0, "status": "normal"},
                            "sensorName": bl["name"],
                            "Time": datetime.utcfromtimestamp(int(DATETIME)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                            "bearingLocationType": location_type
                        }

                except FileNotFoundError:
                    continue
                except Exception:
                    print(traceback.format_exc())
                    continue

            return JsonResponse(list(final_data["data"].values()), safe=False, status=200)

        except Exception:
            print(traceback.format_exc())
            return JsonResponse({"Response": "Data not Found"}, status=500)
    
from pymongo import DESCENDING

@csrf_exempt
@require_http_methods(["POST"])
def start_real_time_value_report_v3(request):
    try:
        data = json.loads(request.body)

        old = {
            "AccelerationEnvelope": "6",
            "Acceleration Envelope": "6",
            "Acceleration": "2",
            "Velocity": "0",
            "Temperature": "8"
        }

        machine_id = data.get("Machine_Name")
        db = client[settings.MONGODB_NAME]

        defaultData = {
            "0": {"status": "normal", "value": 0},
            "2": {"status": "normal", "value": 0},
            "6": {"status": "normal", "value": 0},
            "file": True
        }

        bearingLocationDatas = db["BearingLocation"].find({"machineId": ObjectId(machine_id)})
        final_data = {"data": {}}
        iso_dict = isoStandardGetter(ObjectId(machine_id))

        start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=1)).timestamp())
        end_date_time = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())

        for bearingLocationDatas in bearingLocationDatas:
            file_name = f"RMS_{str(bearingLocationDatas['_id'])}.parquet"

            if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                try:
                    H, V, A = {}, {}, {}
                    DATETIME = 0

                    for axis in ['H', 'V', 'A']:
                        rms_data_cursor = db["LatestRmsData"].find(
                            {"BearingLoactionId": ObjectId(bearingLocationDatas["_id"]), "axis": axis}
                        ).sort([("_id", DESCENDING)]).limit(1)

                        rms_data = list(rms_data_cursor)
                        if not rms_data:
                            continue

                        rms_data = rms_data[0]
                        DATETIME = rms_data['epochTime']
                        axis_data = rms_data.get('data', {})

                        for key, value in axis_data.items():
                            formatted_key = old.get(key)
                            if formatted_key:
                                if axis == "H":
                                    H[formatted_key] = {"value": value, "status": isoAlertGetter(iso_dict, value)}
                                elif axis == "V":
                                    V[formatted_key] = {"value": value, "status": isoAlertGetter(iso_dict, value)}
                                elif axis == "A":
                                    A[formatted_key] = {"value": value, "status": isoAlertGetter(iso_dict, value)}

                    if DATETIME > 10**10:
                        DATETIME = DATETIME // 1000

                    if H or V or A:
                        final_data["data"][bearingLocationDatas["name"]] = {
                            "H": H,
                            "V": V,
                            "A": A,
                            "sensorName": bearingLocationDatas["name"],
                            "Date": datetime.utcfromtimestamp(int(DATETIME)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                            "bearingLocationType": "ONLINE"
                        }

                except FileNotFoundError:
                    pass

            elif bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                try:
                    start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=365)).timestamp())

                    if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                        latest_history = read_from_parquet(file_name, start_date_time, end_date_time, limit=100)
                    else:
                        latest_history = read_from_new_parquet(
                            file_name, data['Machine_Name'], start_date_time, end_date_time,
                            limit=100, analyticsType=data['Analytics_Types']
                        )

                    if latest_history.empty:
                        continue

                    latest_history = latest_history.sort_values(by='timestamp')
                    H, V, A = {}, {}, {}

                    for _, row in latest_history.iterrows():
                        DATETIME = row['timestamp']
                        data_row = json.loads(row['data'])
                        for axis, axis_data in data_row.items():
                            for key, value in axis_data.items():
                                formatted_key = old.get(key)
                                if formatted_key:
                                    entry = {"value": value, "status": isoAlertGetter(iso_dict, value)}
                                    if axis == "H":
                                        H[formatted_key] = entry
                                    elif axis == "V":
                                        V[formatted_key] = entry
                                    elif axis == "A":
                                        A[formatted_key] = entry

                    if DATETIME > 10**10:
                        DATETIME = DATETIME // 1000

                    final_data["data"][bearingLocationDatas["name"]] = {
                        "H": H if H else defaultData,
                        "V": V if V else defaultData,
                        "A": A if A else defaultData,
                        "sensorName": bearingLocationDatas["name"],
                        "Date": datetime.utcfromtimestamp(int(DATETIME)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        "bearingLocationType": "OFFLINE"
                    }

                except FileNotFoundError:
                    pass

        return JsonResponse(final_data["data"], safe=False)

    except Exception:
        traceback.print_exc()
        return JsonResponse({"Response": "Data not Found"}, status=500)
    
def return_internal_server_error(data):
    return JsonResponse({"code": 500, "message": data}, status=500)

def return_data_not_found():
    return JsonResponse({"code": 404, "message": "Data not Found"}, status=404)

def return_data_found(data):
    return JsonResponse({"code": 200, "message": "success", "result": data}, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def start_hopnet_audio(request):
    try:
        data = json.loads(request.body)
        print("audio: ", data)

        start_date_time = datetime.now(timezone.utc) - timedelta(days=1)
        data_date_time = datetime.utcfromtimestamp(int(data["date_time"])).replace(tzinfo=timezone.utc)
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["sensor_id"])})
        if not bearingLocationDatas:
            return return_data_not_found()

        axis_map = {"h": "H", "v": "V", "a": "A"}
        axis = axis_map.get(data["axis_name"].lower())

        File_Data = []
        audio_data = []
        SR_VALUE = 0

        if time_difference.total_seconds() > 0:
            if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                result = db["RawData"].find_one({
                    "BearingLoactionId": ObjectId(data["sensor_id"]),
                    "axis": axis,
                    "epochTime": data["date_time"]
                })
                if not result:
                    return return_data_not_found()

                File_Data = result['data']
                SR_VALUE = 3000
                audio_data = File_Data * 4

            elif bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                All_History = read_from_parquet(f"{data['sensor_id']}.parquet", int(data["date_time"]))
                if All_History.empty:
                    return return_data_not_found()

                for _, row in All_History.iterrows():
                    File_Data = json.loads(row['data'])[axis]
                SR_VALUE = 20000
                audio_data = File_Data * 8

        else:
            if not check_file_exists(f"{data['sensor_id']}.parquet"):
                return return_data_not_found()

            All_History = read_from_parquet(f"{data['sensor_id']}.parquet", int(data["date_time"]))
            if All_History.empty:
                return return_data_not_found()

            if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                for _, row in All_History.iterrows():
                    if row["axis"] == axis:
                        File_Data = json.loads(row["data"])
                SR_VALUE = 3000
                audio_data = File_Data * 4

            elif bearingLocationDatas['bearingLocationType'] == "OFFLINE":
                for _, row in All_History.iterrows():
                    File_Data = json.loads(row['data'])[axis]
                SR_VALUE = 20000
                audio_data = File_Data * 8

        file = f"{data['date_time']}_{data['sensor_id']}"
        Audio(SR_VALUE, audio_data, file)

        with open(f"{audio_directory}{file}.wav", "rb") as binary_file:
            encoded_audio = base64.b64encode(binary_file.read()).decode("UTF-8")

        os.remove(f"{audio_directory}{file}.wav")

        return return_data_found({"audio_data": encoded_audio})

    except Exception as e:
        return return_internal_server_error(str(e))
    
@csrf_exempt
def start_hopnet_timeseries(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            db = client[settings.MONGODB_NAME]
            start_date_time = datetime.now(timezone.utc) - timedelta(days=1)
            data_date_time = datetime.utcfromtimestamp(int(str(data["date_time"]))).replace(tzinfo=timezone.utc)
            time_difference = data_date_time - start_date_time

            bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["sensor_id"])})
            File_Data = []

            if time_difference.total_seconds() > 0:
                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    axis = data["axis_name"].upper()
                    raw = db["RawData"].find_one({
                        "BearingLoactionId": ObjectId(data["sensor_id"]),
                        "axis": axis,
                        "epochTime": data["date_time"]
                    })

                    File_Data = raw['data'] if raw else []
                    SR_VALUE = 3000
                    if data["unit_name"] == 'Velocity':
                        RespondData = velocityConvertDemo(File_Data, SR_VALUE, (
                            bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['velocity']['highpassOrderFft']))
                    elif data["unit_name"] == 'Acceleration':
                        RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (
                            bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['acceleration']['highpassOrderFft']))
                    elif data["unit_name"] == 'Acceleration Envelope':
                        RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (
                            bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))

                else:  # OFFLINE
                    All_History = read_from_parquet(data["sensor_id"] + ".parquet", int(data["date_time"]))
                    if All_History.empty:
                        return return_data_not_found()

                    for _, row in All_History.iterrows():
                        File_Data = json.loads(row['data'])[data["axis_name"].upper()]
                    SR_VALUE = 20000

                    if data["unit_name"] == 'Velocity':
                        RespondData = velocityConvert24Demo(File_Data, SR_VALUE)
                    elif data["unit_name"] == 'Acceleration':
                        RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                    elif data["unit_name"] == 'Acceleration Envelope':
                        RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)

            else:
                if not check_file_exists(data["sensor_id"] + ".parquet"):
                    return return_data_not_found()

                All_History = read_from_parquet(data["sensor_id"] + ".parquet", int(data["date_time"]))
                if All_History.empty:
                    return return_data_not_found()

                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    for _, row in All_History.iterrows():
                        if data["axis_name"].upper() == row["axis"]:
                            File_Data = json.loads(row["data"])
                    SR_VALUE = 3000
                    if data["unit_name"] == 'Velocity':
                        RespondData = velocityConvertDemo(File_Data, SR_VALUE, (
                            bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['velocity']['highpassOrderFft']))
                    elif data["unit_name"] == 'Acceleration':
                        RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (
                            bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['acceleration']['highpassOrderFft']))
                    elif data["unit_name"] == 'Acceleration Envelope':
                        RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (
                            bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))
                else:  # OFFLINE
                    for _, row in All_History.iterrows():
                        File_Data = json.loads(row['data'])[data["axis_name"].upper()]
                    SR_VALUE = 20000
                    if data["unit_name"] == 'Velocity':
                        RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                    elif data["unit_name"] == 'Acceleration':
                        RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                    elif data["unit_name"] == 'Acceleration Envelope':
                        RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)

            for key in ['FFT', 'fft_max', 'fft_min']:
                RespondData.pop(key, None)

            return return_data_found({"twf": RespondData})

        except Exception as e:
            print(traceback.format_exc())
            return return_internal_server_error(str(e))
    
@csrf_exempt
def start_hopnet_fft(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("fft:", data)

            start_date_time = datetime.now(timezone.utc) - timedelta(days=1)
            data_date_time = datetime.utcfromtimestamp(int(str(data["date_time"]))).replace(tzinfo=timezone.utc)
            time_difference = data_date_time - start_date_time

            bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["sensor_id"])})
            axis = data["axis_name"].upper()
            RespondData = {}

            def convert_unit(unit_name, file_data, sr, cutoff_data=None):
                if unit_name == 'Velocity':
                    return velocityConvertDemo(file_data, sr, cutoff_data) if cutoff_data else velocityConvert32Demo(file_data, sr)
                elif unit_name == 'Acceleration':
                    return accelerationConvertDemo(file_data, sr, cutoff_data) if cutoff_data else accelerationConvert32Demo(file_data, sr)
                elif unit_name == 'Acceleration Envelope':
                    return accelerationEnvelopeConvertDemo(file_data, sr, cutoff_data) if cutoff_data else accelerationEnvelopeConvert32Demo(file_data, sr)
                return {}

            if time_difference.total_seconds() > 0:
                # Fresh data
                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    doc = db["RawData"].find_one({
                        "BearingLoactionId": ObjectId(data["sensor_id"]),
                        "axis": axis,
                        "epochTime": data["date_time"]
                    })
                    if not doc:
                        return return_data_not_found()

                    File_Data = doc['data']
                    SR_VALUE = 3000
                    cutoff_data = bearingLocationDatas[data["unit_name"].lower()]['highpassCutoffFrequencyFft'], \
                                bearingLocationDatas[data["unit_name"].lower()]['highpassOrderFft']
                    RespondData = convert_unit(data["unit_name"], File_Data, SR_VALUE, cutoff_data)
                else:
                    All_History = read_from_parquet(f"{data['sensor_id']}.parquet", int(data["date_time"]))
                    if All_History.empty:
                        return return_data_not_found()

                    for _, row in All_History.iterrows():
                        File_Data = json.loads(row['data'])[axis]
                    RespondData = convert_unit(data["unit_name"], File_Data, 20000)
            else:
                # Historical data
                if not check_file_exists(f"{data['sensor_id']}.parquet"):
                    return return_data_not_found()

                All_History = read_from_parquet(f"{data['sensor_id']}.parquet", int(data["date_time"]))
                if All_History.empty:
                    return return_data_not_found()

                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    for _, row in All_History.iterrows():
                        if row["axis"] == axis:
                            File_Data = json.loads(row["data"])
                    SR_VALUE = 3000
                    cutoff_data = bearingLocationDatas[data["unit_name"].lower()]['highpassCutoffFrequencyFft'], \
                                bearingLocationDatas[data["unit_name"].lower()]['highpassOrderFft']
                    RespondData = convert_unit(data["unit_name"], File_Data, SR_VALUE, cutoff_data)
                else:
                    for _, row in All_History.iterrows():
                        File_Data = json.loads(row["data"])[axis]
                    RespondData = convert_unit(data["unit_name"], File_Data, 20000)

            for key in ['Timeseries', 'twf_max', 'twf_min']:
                RespondData.pop(key, None)

            return return_data_found({"fft": RespondData})
        except Exception as e:
            print(traceback.format_exc())
            return return_internal_server_error(e)

@csrf_exempt
@require_http_methods(["POST"])
def parameter_trends_view(request):
    try:
        data = json.loads(request.body)
        print("ParameterTrends:", data)
        db = client[settings.MONGODB_NAME]
        bearing_location_id = data["sensor_id"]
        bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(bearing_location_id)})
        end_time = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())

        H, V, A = [], [], []

        def append_online_data(axis, days, unit_name, limit=None):
            filter_ = {
                "BearingLoactionId": ObjectId(bearing_location_id),
                "axis": axis,
                "epochTime": {"$gte": start_time, "$lte": end_time}
            }
            query = db["ParameterTrend"].find(filter_).sort("_id", -1)
            if limit:
                query = query.limit(limit)
            for rd in query:
                t = rd["epochTime"]
                val = rd["data"].get(unit_name)
                raw = rd.get("rawDataPresent", False)
                if axis == "H":
                    H.append((t, val, raw))
                elif axis == "V":
                    V.append((t, val, raw))
                elif axis == "A":
                    A.append((t, val, raw))

        def append_offline_data(df, unit_name):
            for _, row in df.iterrows():
                t = row["timestamp"]
                axis_data = json.loads(row["data"])
                for axis_key in ["H", "V", "A"]:
                    if axis_key in axis_data:
                        val = axis_data[axis_key][unit_name]
                        raw = fileFind(1)
                        if axis_key == "H":
                            H.append((t, val, raw))
                        elif axis_key == "V":
                            V.append((t, val, raw))
                        elif axis_key == "A":
                            A.append((t, val, raw))

        days = data.get("days", 0)
        unit_name = data.get("unit_name")
        axis_name = data.get("axis_name", "all").lower()

        if days <= 1:
            if days == 0:
                start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=365)).timestamp())
                number_of_data = 120
            else:
                start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=days)).timestamp())
                number_of_data = None

            if bearingLocationDatas.get("bearingLocationType") == "OFFLINE":
                parquet_data = read_from_parquet(f"RMS_{bearing_location_id}.parquet", start_time, end_time, number_of_data)
                if parquet_data.empty:
                    return return_data_not_found()
                append_offline_data(parquet_data, unit_name)

            else:  # ONLINE
                for axis in ['H', 'V', 'A']:
                    append_online_data(axis, days, unit_name, number_of_data)

        elif days > 1:
            start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=days)).timestamp())
            parquet_data = read_from_parquet(f"RMS_{bearing_location_id}.parquet", start_time, end_time)
            if parquet_data.empty:
                return return_data_not_found()

            if bearingLocationDatas.get("bearingLocationType") == "OFFLINE":
                append_offline_data(parquet_data, unit_name)
            else:  # ONLINE (data read from parquet anyway?)
                for _, row in parquet_data.iterrows():
                    t = row["timestamp"]
                    axis = row["axis"]
                    val = json.loads(row["data"]).get(unit_name)
                    raw = row.get("rawDataPresent", False)
                    if axis == "H":
                        H.append((t, val, raw))
                    elif axis == "V":
                        V.append((t, val, raw))
                    elif axis == "A":
                        A.append((t, val, raw))

        # Sort by timestamp
        H.sort(key=lambda x: x[0])
        V.sort(key=lambda x: x[0])
        A.sort(key=lambda x: x[0])

        if axis_name == "all":
            output = [{"name": "H", "value": H}, {"name": "V", "value": V}, {"name": "A", "value": A}]
        elif axis_name == "h":
            output = [{"name": "H", "value": H}]
        elif axis_name == "v":
            output = [{"name": "V", "value": V}]
        elif axis_name == "a":
            output = [{"name": "A", "value": A}]
        else:
            return return_data_not_found()

        return return_data_found({"parameter_trend": output})

    except Exception as e:
        traceback.print_exc()
        return return_internal_server_error(str(e))
    
@csrf_exempt
@require_http_methods(["POST"])
def hopnet_realtime_value_report(request):
    try:
        data = json.loads(request.body)
        old = {
            "AccelerationEnvelope": "6",
            "Acceleration Envelope": "6",
            "Acceleration": "2",
            "Velocity": "0",
            "Temperature": "8"
        }
        machine_id = data["machine_id"]
        db = client[settings.MONGODB_NAME]
        final_data = {"data": {}}

        default_data = {
            "0": {"status": "normal", "value": 0},
            "2": {"status": "normal", "value": 0},
            "6": {"status": "normal", "value": 0},
            "file": True
        }

        start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=1)).timestamp())
        end_time = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())

        iso_dict = isoAlertGetter(ObjectId(machine_id), iso_dict=True)  # adapt isoStandardGetter as needed
        machine = db["Machine"].find_one({"_id": ObjectId(machine_id)})
        bearing_locations = db["BearingLocation"].find({"machineId": ObjectId(machine_id)})

        for location in bearing_locations:
            file_name = f"RMS_{str(location['_id'])}.parquet"
            H, V, A = {}, {}, {}

            if location.get("bearingLocationType") == "OFFLINE":
                try:
                    latest = read_from_parquet(file_name, start_time, end_time, 10)
                    if latest.empty:
                        continue

                    for _, row in latest.iterrows():
                        t = row['timestamp']
                        axis_data = json.loads(row['data'])

                        for axis_key in ["H", "V", "A"]:
                            if axis_key in axis_data:
                                for key, value in axis_data[axis_key].items():
                                    entry = {"value": value, "status": isoAlertGetter(iso_dict=iso_dict, value=value), "unixTimestamp": int(t)}
                                    if axis_key == "H":
                                        H[old.get(key, key)] = entry
                                    elif axis_key == "V":
                                        V[old.get(key, key)] = entry
                                    elif axis_key == "A":
                                        A[old.get(key, key)] = entry

                    t = t // 1000 if t > 10**10 else t
                    final_data["data"][location["name"]] = {
                        "H": default_data if not H else H,
                        "V": default_data if not V else V,
                        "A": default_data if not A else A,
                        "sensorName": location["name"],
                        "Date": datetime.utcfromtimestamp(int(t)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        "bearingLocationType": "OFFLINE"
                    }
                except FileNotFoundError:
                    continue

            else:  # ONLINE
                try:
                    for axis in ['H', 'V', 'A']:
                        rms_data = list(db["ParameterTrend"].find({
                            "BearingLoactionId": ObjectId(location["_id"]),
                            "axis": axis,
                            "rawDataPresent": True
                        }).sort([("_id", -1)]).limit(1))

                        if not rms_data:
                            continue

                        latest_data = rms_data[0]
                        t = latest_data['epochTime']

                        for key, value in latest_data['data'].items():
                            entry = {"value": value, "status": isoAlertGetter(iso_dict=iso_dict, value=value), "unixTimestamp": int(t)}
                            if axis == "H":
                                H[old.get(key, key)] = entry
                            elif axis == "V":
                                V[old.get(key, key)] = entry
                            elif axis == "A":
                                A[old.get(key, key)] = entry

                    t = t // 1000 if t > 10**10 else t
                    if H or V or A:
                        final_data["data"][location["name"]] = {
                            "H": H,
                            "V": V,
                            "A": A,
                            "sensorName": location["name"],
                            "Date": datetime.utcfromtimestamp(int(t)).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                            "bearingLocationType": "ONLINE"
                        }

                except Exception:
                    continue

        return JsonResponse(final_data["data"], safe=False)

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"Response": "Data not Found"}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def hopnet_machine_view(request):
    data = [
        {'id': '65967ec33fc203bd2bf2eb0e', 'name': 'Ball Mill 1'},
        {'id': '659688d43fc203bd2bf2eceb', 'name': 'Ball Mill 2'}
    ]
    return JsonResponse({'machine': data})

@csrf_exempt
@require_http_methods(["GET"])
def hopnet_bearing_location_view(request):
    sensor_list = [
        {"_id": "65967f553fc203bd2bf2eb38", "name": "MOTOR DE"},
        {"_id": "659682e33fc203bd2bf2eb5b", "name": "MOTOR NDE"},
        {"_id": "659684f93fc203bd2bf2ebb1", "name": "GB INPUT SHAFT DE"},
        {"_id": "659685013fc203bd2bf2ebb7", "name": "GB INPUT SHAFT NDE"},
        {"_id": "659685103fc203bd2bf2ebbd", "name": "GB OUTPUT SHAFT DE"},
        {"_id": "659685343fc203bd2bf2ebc6", "name": "GB OUTPUT SHAFT NDE"},
        {"_id": "6596853f3fc203bd2bf2ebcd", "name": "PINION DE"},
        {"_id": "659685483fc203bd2bf2ebd3", "name": "PINION NDE"},
        {"_id": "659685513fc203bd2bf2ebd9", "name": "TRUNION BEARING INLET"},
        {"_id": "659685583fc203bd2bf2ebdf", "name": "TRUNION BEARING OUTLET"}
    ]

    machine_list = [
        {"_id": str(ObjectId("65967ec33fc203bd2bf2eb0e")), "name": "Ball Mill 1"},
        {"_id": str(ObjectId("659688d43fc203bd2bf2eceb")), "name": "Ball Mill 2"}
    ]

    return JsonResponse({"machine": machine_list})

@csrf_exempt
@require_http_methods(["POST"])
def get_data(request):
    try:
        axis_mapping = {
            "H-Axis": "H",
            "V-Axis": "V",
            "A-Axis": "A"
        }

        db = client[settings.MONGO_DB_NAME]
        metaData = json.loads(request.body)
        start_date_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        machine = db["Machine"].find_one({"name": metaData['Machine_Name']})
        if not machine:
            return JsonResponse({"Error": "Machine Name Not Found"}, status=500)

        bearing = db["BearingLocation"].find_one({
            "machineId": ObjectId(machine['_id']),
            "name": metaData['Bearing_Location_Name']
        })
        if not bearing:
            return JsonResponse({"Error": "Bearing Location Not Found"}, status=500)

        axis = axis_mapping.get(metaData["Axis_Id"])
        if not axis:
            return JsonResponse({"Error": "Invalid Axis Id"}, status=400)

        if metaData['type'] == "ONLINE":
            epoch_time = metaData.get("TimeStamp")

            if not epoch_time:
                end_time = int(datetime.now(timezone.utc).timestamp())
                latest = list(db["ParameterTrend"].find({
                    "BearingLoactionId": ObjectId(bearing['_id']),
                    "axis": axis,
                    "rawDataPresent": True,
                    "epochTime": {"$gte": int(start_date_time.timestamp()), "$lte": end_time}
                }).sort([("_id", DESCENDING)]).limit(1))

                if latest:
                    epoch_time = latest[0]["epochTime"]
                else:
                    two_years_ago = int((datetime.now(timezone.utc) - timedelta(days=730)).timestamp())
                    df = read_from_parquet(
                        f"{bearing['_id']}.parquet", two_years_ago,
                        end_time=int(start_date_time.timestamp()), limit=1, axis=axis
                    )
                    if df.empty:
                        return JsonResponse({"Response": "Data not Found"}, status=404)
                    row = df.iloc[0]
                    return JsonResponse({
                        "timestamp": row["timestamp"],
                        "rawData": json.loads(row["data"]),
                        "SR": 3000,
                        "RPM": machine['rpm'],
                        "cutoff": (
                            bearing['velocity']['highpassCutoffFrequencyFft'],
                            bearing['velocity']['highpassOrderFft']
                        )
                    })

            dt_epoch = datetime.utcfromtimestamp(int(epoch_time)).replace(tzinfo=timezone.utc)
            if (dt_epoch - start_date_time).total_seconds() > 0:
                if 'bearingLocationType' not in bearing or bearing['bearingLocationType'] == "ONLINE":
                    raw = db["RawData"].find_one({
                        "BearingLoactionId": ObjectId(bearing['_id']),
                        "axis": axis,
                        "epochTime": int(epoch_time)
                    })
                    if raw:
                        return JsonResponse({
                            "timestamp": epoch_time,
                            "rawData": raw['data'],
                            "SR": 3000,
                            "RPM": machine['rpm'],
                            "cutoff": (
                                bearing['velocity']['highpassCutoffFrequencyFft'],
                                bearing['velocity']['highpassOrderFft']
                            )
                        })
            else:
                if check_file_exists(f"{bearing['_id']}.parquet"):
                    df = read_from_parquet(f"{bearing['_id']}.parquet", int(epoch_time), axis=axis)
                    if df.empty:
                        return JsonResponse({"Response": "Data not Found"}, status=404)
                    row = df.iloc[0]
                    return JsonResponse({
                        "timestamp": row["timestamp"],
                        "rawData": json.loads(row["data"]),
                        "SR": 3000,
                        "RPM": machine['rpm'],
                        "cutoff": (
                            bearing['velocity']['highpassCutoffFrequencyFft'],
                            bearing['velocity']['highpassOrderFft']
                        )
                    })

        elif metaData['type'] == "OFFLINE":
            end_ts = int((datetime.now(timezone.utc) - timedelta(days=365)).timestamp())
            start_ts = int(metaData.get('TimeStamp', datetime.now(timezone.utc).timestamp())) + 20

            if "Analytics_Types" in metaData:
                df = read_from_new_parquet(f"{bearing['_id']}.parquet", machine['_id'], end_ts, start_ts,
                                           analyticsType=metaData["Analytics_Types"])
            else:
                df = read_from_parquet(f"{bearing['_id']}.parquet", end_ts, start_ts)

            H, V, A = {}, {}, {}
            for _, row in df.iterrows():
                data = json.loads(row['data'])
                ts = row['timestamp']
                if "H" in data and axis == "H":
                    H = {"H": data["H"], "timestamp": ts}
                elif "V" in data and axis == "V":
                    V = {"V": data["V"], "timestamp": ts}
                elif "A" in data and axis == "A":
                    A = {"A": data["A"], "timestamp": ts}

            final = {}
            if axis == "H" and H:
                final = {"timestamp": H["timestamp"], "rawData": H["H"], "RPM": machine["rpm"]}
            elif axis == "V" and V:
                final = {"timestamp": V["timestamp"], "rawData": V["V"], "RPM": machine["rpm"]}
            elif axis == "A" and A:
                final = {"timestamp": A["timestamp"], "rawData": A["A"], "RPM": machine["rpm"]}

            return JsonResponse(final)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_old_data(request):
    db = client[settings.MONGODB_NAME]
    try:
        data = json.loads(request.body)
        print("ParameterTrends:", data)

        machine_data = db["Machine"].find_one({"name": data['Machine_Name']})
        if not machine_data:
            return JsonResponse({"Error": "Machine Name Not Found"}, status=500)

        bearing_data = db["BearingLocation"].find_one({
            "machineId": ObjectId(machine_data['_id']),
            "name": data['Bearing_Location_Name']
        })
        if not bearing_data:
            return JsonResponse({"Error": "Bearing Location Not Found"}, status=500)

        end_time = int(datetime.now().astimezone(settings.GMT_TIMEZONE).timestamp())

        H, V, A = [], [], []

        if data['days'] <= 1:
            if data['days'] == 0:
                start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=365)).timestamp())
                number_of_data = 120
                if bearing_data.get('bearingLocationType') == "OFFLINE":
                    All_History = read_from_parquet(f"RMS_{bearing_data['_id']}.parquet", start_time, end_time, number_of_data)
            else:
                start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=data['days'])).timestamp())
                if bearing_data.get('bearingLocationType') == "OFFLINE":
                    All_History = read_from_parquet(f"RMS_{bearing_data['_id']}.parquet", start_time, end_time)

            if bearing_data.get('bearingLocationType') == "OFFLINE":
                if All_History.empty:
                    return JsonResponse({"Response": "Data not Found"}, status=404)

            if bearing_data.get('bearingLocationType') != "OFFLINE":
                for axis in ['H', 'V', 'A']:
                    query = {
                        "BearingLoactionId": ObjectId(str(bearing_data['_id'])),
                        "axis": axis,
                        "epochTime": {"$gte": start_time, "$lte": end_time}
                    }
                    if data['days'] == 0:
                        trend_data = list(db["ParameterTrend"].find(query).sort("_id", DESCENDING).limit(number_of_data))
                    else:
                        trend_data = list(db["ParameterTrend"].find(query).sort("_id", DESCENDING))

                    if not trend_data:
                        trend_data = read_from_parquet(f"RMS_{bearing_data['_id']}.parquet", start_time, end_time, number_of_data)
                        for _, row in trend_data.iterrows():
                            timestamp = row['timestamp']
                            axis_key = next(iter(json.loads(row['data'])))
                            value = json.loads(row['data'])[axis_key][data["Type"]]
                            axis_list = {"H": H, "V": V, "A": A}.get(axis_key, [])
                            axis_list.append((timestamp, value, fileFind(1)))
                    else:
                        for item in trend_data:
                            timestamp = item['epochTime']
                            value = item['data'][data["Type"]]
                            axis_list = {"H": H, "V": V, "A": A}.get(axis, [])
                            axis_list.append((timestamp, value, item['rawDataPresent']))

            elif bearing_data.get('bearingLocationType') == "OFFLINE":
                for _, row in All_History.iterrows():
                    timestamp = row['timestamp']
                    axis_key = next(iter(json.loads(row['data'])))
                    value = json.loads(row['data'])[axis_key][data["Type"]]
                    axis_list = {"H": H, "V": V, "A": A}.get(axis_key, [])
                    axis_list.append((timestamp, value, fileFind(1)))

        else:  # days > 1
            start_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=int(data['days']))).timestamp())
            All_History = read_from_parquet(f"RMS_{bearing_data['_id']}.parquet", start_time, end_time)

            for axis in ['H', 'V', 'A']:
                trend_data = list(db["ParameterTrend"].find({
                    "BearingLoactionId": ObjectId(str(bearing_data['_id'])),
                    "axis": axis,
                    "epochTime": {"$gte": start_time, "$lte": end_time}
                }).sort("_id", DESCENDING))

                for item in trend_data:
                    timestamp = item['epochTime']
                    value = item['data'][data["Type"]]
                    axis_list = {"H": H, "V": V, "A": A}.get(axis, [])
                    axis_list.append((timestamp, value, item['rawDataPresent']))

            if All_History.empty:
                return JsonResponse({"Response": "Data not Found"}, status=404)

            for _, row in All_History.iterrows():
                timestamp = row['timestamp']
                axis_key = next(iter(json.loads(row['data'])))
                value = json.loads(row['data'])[axis_key][data["Type"]]
                axis_list = {"H": H, "V": V, "A": A}.get(axis_key, [])
                axis_list.append((timestamp, value, fileFind(1) if bearing_data.get('bearingLocationType') == "OFFLINE" else row.get('rawDataPresent')))

        # Sorting
        H.sort(key=lambda x: x[0])
        V.sort(key=lambda x: x[0])
        A.sort(key=lambda x: x[0])

        # Axis response
        axis_id = data['Axis_Id'].lower()
        if axis_id == "all":
            return JsonResponse([
                {"name": "H", "value": H},
                {"name": "V", "value": V},
                {"name": "A", "value": A}
            ], safe=False)
        elif axis_id == "h-axis":
            return JsonResponse([{"name": "H", "value": H}], safe=False)
        elif axis_id == "v-axis":
            return JsonResponse([{"name": "V", "value": V}], safe=False)
        elif axis_id == "a-axis":
            return JsonResponse([{"name": "A", "value": A}], safe=False)
        else:
            return JsonResponse({"Response": []}, status=404)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"Response": "Data not Found"}, status=500)

from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponse

@csrf_exempt
@require_http_methods(["POST"])
def delete_records_by_timestamp(request):
    try:
        metaData = json.loads(request.body)
        file_name = metaData["file_name"]
        timestamp_to_delete = metaData["timestamp_to_delete"]

        for name in [file_name + '.parquet', 'RMS_' + file_name + '.parquet']:
            file_path = os.path.join(settings.PARQUET_PATH, name)
            if not check_file_exists(name):
                return HttpResponseNotFound(f"{name} does not exist.")

            try:
                table = pq.read_table(file_path)
                df = table.to_pandas()
                original_count = len(df)
                df_filtered = df[df['timestamp'] != int(timestamp_to_delete)]
                if original_count == len(df_filtered):
                    return HttpResponseNotFound(f"No records with timestamp {timestamp_to_delete} found in {name}.")
                df_filtered.to_parquet(file_path, index=False)
            except Exception as e:
                return HttpResponseServerError(f"Error processing {name}: {str(e)}")

        return JsonResponse({ "message": "Value Deleted" })

    except Exception as e:
        return HttpResponseServerError(f"Error: {str(e)}")
    
# Define Mongo clients
TestMongoclient = MongoClient('mongodb://localhost:27017')
ProdMongoclient = MongoClient('mongodb://localhost:27017')
DemoMongoclient = MongoClient('mongodb://localhost:27017')

update_fmax_noOfLine_map = {
                (25, 125): (200, 1000),
                (25, 500): (200, 4000),
                (50, 250): (200, 1000),
                (50, 1000): (200, 4000),
                (100, 500): (200, 1000),
                (100, 2000): (200, 4000),
                (200, 1000): (800, 4000),
                (400, 2000): (800, 4000),
                (800, 4000): (800, 4000),
                (1200, 6000): (1200, 4800)
}

update_fmax_noOfLine_Offline_map = {
                (25, 125): (200, 4000),
                (25, 500): (200, 4000),
                (50, 250): (200, 4000),
                (50, 1000): (200, 4000),
                (100, 500): (200, 4000),
                (100, 2000): (200, 4000),
                (200, 1000): (800, 16000),
                (400, 2000): (800, 16000),
                (800, 4000): (800, 19200),
                (1200, 6000): (1200, 32000)
            }

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

@csrf_exempt
@require_http_methods(["GET"])
def sensor_calibration(request, mac):
    key = b'abcdefghijklmnop'  # AES 128-bit key
    try:
        db = TestMongoclient['aamsTest']
        collection = db['sensorLocation']
        config_item = collection.find_one({ "macAddress": mac })

        bearingLocationDatas = None
        if config_item:
            location = config_item.get('location')
            if location == 'prod':
                db = ProdMongoclient['aams']
                config_item = db['Sensor'].find_one({'address': mac})
                bearingLocationDatas = db["BearingLocation"].find_one({
                    "_id": ObjectId(config_item.get('bearingLocationId'))
                }) if config_item.get('bearingLocationId') else None
            elif location == 'demo':
                db = DemoMongoclient['aams']
                config_item = db['Sensor'].find_one({'address': mac})
            else:
                config_item = db['Sensor'].find_one({'macAddress': mac})

        if config_item:
            if bearingLocationDatas and "fmax" in bearingLocationDatas:
                fmax = bearingLocationDatas.get('fmax', 25)
                NoOflines = bearingLocationDatas.get('noOflines', 1000)
                if (fmax, NoOflines) in update_fmax_noOfLine_map:
                    fmax, NoOflines = update_fmax_noOfLine_map[(fmax, NoOflines)]

                plaintext = {
                    "SSID": config_item.get('ssid'),
                    "PWD": config_item.get("password"),
                    "RANGE": str(config_item.get('gRange')) + "G",
                    "POST_URL": config_item.get("postUrl"),
                    "T_FLAG": config_item.get("tFlag"),
                    "SF": int(1000000 / int(fmax * 2)),
                    "NOS": int(((fmax * 2) * (NoOflines / (fmax * 2))) * 2),
                    "RF": int((((NoOflines / (fmax * 2)) * 2) * 3) + 15)
                }
            else:
                plaintext = {
                    "SSID": config_item.get('ssid'),
                    "PWD": config_item.get("password"),
                    "RANGE": str(config_item.get('gRange')) + "G",
                    "RF": config_item.get("reportingFrequency"),
                    "NOS": config_item.get("numberOfSamples"),
                    "SF": int(1000000 / config_item.get("samplingFrequency")),
                    "POST_URL": config_item.get("postUrl"),
                    "T_FLAG": config_item.get("tFlag"),
                }

            cipher = AES.new(key, AES.MODE_ECB)
            ciphertext = cipher.encrypt(pad(json.dumps(plaintext).encode(), AES.block_size))
            encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
            return HttpResponse(encoded_ciphertext, content_type="text/plain")

        return JsonResponse({'error': 'Config item not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["GET"])
def SensorCalibrationSerialNumber(request, serialNumber):
    key = b'abcdefghijklmnop' 
    try:
        print("data", serialNumber)
        
        db = TestMongoclient['aamsTest']
        collection = db['sensorLocation']
        config_item = collection.find_one({"serialNumber": serialNumber})

        if config_item:
            location = config_item.get('location')
            if location == 'prod':            
                db = ProdMongoclient['aams']
                collection = db['MultiChannelSensor']
                config_item = collection.find_one({"serialNumber": serialNumber })
            elif location == 'demo':
                db = DemoMongoclient['aams']
                collection = db['MultiChannelSensor']
                config_item = collection.find_one({"serialNumber": serialNumber })
            else:
                collection = db['MultiChannelSensor']
                config_item = collection.find_one({"serialNumber": serialNumber })

            if config_item:  
                plaintext = {
                    "SSID": config_item.get('ssid'),
                    "PWD": config_item.get("password"),
                    "RANGE": str(config_item.get('gRange')) + "G",
                    "RF": config_item.get("reportingFrequency"),
                    "SF": config_item.get("samplingFrequency"),
                    "NOS": config_item.get("numberOfSamples"),
                    "postUrl": config_item.get("postUrl"),
                    "CSF": config_item.get("csf"),
                    "Treshold": config_item.get("treshold"),
                }

                cipher = AES.new(key, AES.MODE_ECB)
                ciphertext = cipher.encrypt(pad(json.dumps(plaintext).encode(), AES.block_size))
                encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
                return JsonResponse({"ciphertext": encoded_ciphertext}, status=200)

        return JsonResponse({"error": "Config item not found"}, status=404)

    except Exception as e:
        print(e)
        return JsonResponse({"error": "An error occurred"}, status=500)

@csrf_exempt
def get_sensor_config(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sensor_mac = data["macAddress"]

            db = TestMongoclient['aamsTest']
            collection = db['sensorLocation']
            sensor_data_validator = list(collection.find({"macAddress": sensor_mac}))

            if sensor_data_validator:
                sensor_data_validator = sensor_data_validator[0]
                location = sensor_data_validator.get('location')

                if location == 'prod':         
                    db = ProdMongoclient['aams']
                    collection = db['Sensor']
                    config_item = dict(collection.find_one({'address': sensor_mac}))

                elif location == 'demo':
                    db = DemoMongoclient['aams']
                    collection = db['Sensor']
                    config_item = collection.find_one({'address': sensor_mac})

                if "configuration" in config_item and config_item['configuration'] == True:
                    update_result = collection.update_one(
                        {'address': sensor_mac},
                        {'$set': {'configuration': False}}
                    )
                    return JsonResponse({"config": config_item["configuration"]})

                return JsonResponse({"config": False})
            
            return JsonResponse({"config": False})

        except Exception as e:
            print(e)
            return JsonResponse({"error": "An error occurred"}, status=500)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
@require_http_methods(["GET"])
def SensorToken(request, MAC):
    key = b'abcdefghijklmnop'
    try:
        print("data", MAC)
        
        db = TestMongoclient['aamsTest']
        collection = db['sensorLocation']
        config_item = collection.find_one({"macAddress": MAC})

        if config_item:
            location = config_item.get('location')
            if location == 'prod':
                db = ProdMongoclient['aams']
                collection = db['Sensor']
                config_item = collection.find_one({'address': MAC})
            elif location == 'demo':
                db = DemoMongoclient['aams']
                collection = db['Sensor']
                config_item = collection.find_one({'address': MAC})
            else:
                collection = db['Sensor']
                config_item = collection.find_one({'macAddress': MAC})

            if config_item:
                plaintext = {
                    "TOKEN": config_item.get('token')
                }
                cipher = AES.new(key, AES.MODE_ECB)
                ciphertext = cipher.encrypt(pad(json.dumps(plaintext).encode(), AES.block_size))
                encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
                return JsonResponse({"ciphertext": encoded_ciphertext}, status=200)

            return JsonResponse({"error": "Config item not found"}, status=404)

        return JsonResponse({"error": "Config item not found"}, status=404)

    except Exception as e:
        print(e)
        return JsonResponse({"error": "An error occurred"}, status=500)
    
from scipy.signal import find_peaks

def top10Fft(fft_array):
    fft_array = np.array(fft_array)
    frequencies = fft_array[:, 0]
    amplitudes = fft_array[:, 1]

    peaks, _ = find_peaks(amplitudes, height=0.001)

    peak_freqs = frequencies[peaks]
    peak_amps = amplitudes[peaks]

    sorted_indices = np.argsort(peak_amps)[-10:]

    top_peaks = [{"frequency": float(peak_freqs[i]), "amplitude": float(peak_amps[i])} for i in sorted_indices]

    top_peaks_sorted = sorted(top_peaks, key=lambda x: (x["frequency"], x["amplitude"]))
    return top_peaks_sorted

@csrf_exempt
@require_http_methods(["POST"])
def start_top_10_fft(request):
    db = client[settings.MONGODB_NAME]
    try:
        data = json.loads(request.body)
        latest = False
        start_date_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        axis_mapping = { "H-Axis": "H", "V-Axis": "V", "A-Axis": "A" }

        if "date_Time" not in data:
            end_date_time = int(datetime.now(timezone.utc).timestamp())
            epoch_data = list(
                db["ParameterTrend"].find({
                    "BearingLoactionId": ObjectId(data["Sensor_Name"]),
                    "axis": axis_mapping[data["Axis_Id"]],
                    "rawDataPresent": True,
                    "epochTime": {"$gte": int(start_date_time.timestamp()), "$lte": end_date_time}
                }).sort([("_id", DESCENDING)]).limit(1)
            )
            if epoch_data:
                epoch_date_time = epoch_data[0]["epochTime"]
            else:
                epoch_date_time = int((datetime.now(timezone.utc) + timedelta(days=-2)).timestamp())
                latest = True
        else:
            epoch_date_time = data["date_Time"]

        data_date_time = datetime.utcfromtimestamp(int(epoch_date_time)).replace(tzinfo=timezone.utc)
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["Sensor_Name"])})
        MachineDatas = db["Machine"].find_one({"_id": ObjectId(data["Machine_Name"])})

        axis_name = data["Axis_Id"]
        file_data = []
        response_data = []

        # === OFFLINE MODE ===
        if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
            # choose parquet function
            if latest:
                start_epoch = int((datetime.now(timezone.utc) + timedelta(days=-365)).timestamp())
                if data.get("Analytics_Types") in [None, "OM"]:
                    all_history = read_from_parquet(f"{data['Sensor_Name']}.parquet", start_epoch, end_date_time, limit=1)
                else:
                    all_history = read_from_new_parquet(f"{data['Sensor_Name']}.parquet", data['Machine_Name'], start_epoch, end_date_time, limit=1)
            else:
                if data.get("Analytics_Types") in [None, "OM"]:
                    all_history = read_from_parquet(f"{data['Sensor_Name']}.parquet", int(epoch_date_time))
                else:
                    all_history = read_from_new_parquet(f"{data['Sensor_Name']}.parquet", data['Machine_Name'], int(epoch_date_time))

            if all_history.empty:
                return JsonResponse({"Response": "Data not Found"}, status=404)

            for _, row in all_history.iterrows():
                file_data = json.loads(row['data'])[axis_mapping[axis_name]]
                epoch_date_time = row['timestamp']
                SR = int(row.get('SR', 20000))
                rpm = row.get('rpm', MachineDatas['rpm'])
                fMax = row.get('fMax')
                cutoff = int(float(row.get('cutoff', 0)))
                floorNoiseThresholdPercentage = float(row.get('floorNoiseThresholdPercentage', 5))
                floorNoiseAttenuationFactor = float(row.get('floorNoiseAttenuationFactor', 1))

            offline_meta = db["OfflineDataStore"].find_one({
                "bearingLocationId": ObjectId(data["Sensor_Name"]),
                "epochTime": epoch_date_time
            }) or {}

            if len(file_data) != 30000 and offline_meta.get("datatype") in ['24bit', '24bit-13C']:
                SR_VALUE = offline_meta.get('sr', SR)
                if data["Type"] == 'Velocity':
                    response_data = velocityConvert32Demo(file_data, SR_VALUE, rpm, cutoff,
                        bearingLocationDatas['velocity']['highpassOrderFft'], fmax=fMax,
                        floorNoiseAttenuationFactor=floorNoiseAttenuationFactor,
                        floorNoiseThresholdPercentage=floorNoiseThresholdPercentage)
                elif data["Type"] == 'Acceleration':
                    response_data = accelerationConvert32Demo(file_data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    response_data = accelerationEnvelopeConvert32Demo(file_data, SR_VALUE)

            elif offline_meta.get("datatype") == "32bit":
                SR_VALUE = offline_meta['sr']
                if data["Type"] == 'Velocity':
                    response_data = velocityConvert32Demo(file_data, SR_VALUE)
                elif data["Type"] == 'Acceleration':
                    response_data = accelerationConvert32Demo(file_data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    response_data = accelerationEnvelopeConvert32Demo(file_data, SR_VALUE)

            else:
                SR_VALUE = 20000
                if data["Type"] == 'Velocity':
                    response_data = velocityConvert32Demo(file_data, SR_VALUE)
                elif data["Type"] == 'Acceleration':
                    response_data = accelerationConvert32Demo(file_data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    response_data = accelerationEnvelopeConvert32Demo(file_data, SR_VALUE)

        # === ONLINE MODE ===
        else:
            if time_difference.total_seconds() > 0:
                number_of_data = 1 if bearingLocationDatas.get("onlineOfflineFlag", 0) == 1 else 5
                raw_entry = db["RawData"].find_one({
                    "BearingLoactionId": ObjectId(data["Sensor_Name"]),
                    "axis": axis_mapping[axis_name],
                    "epochTime": epoch_date_time
                })

                if not raw_entry:
                    return JsonResponse({"Response": "Raw data not found"}, status=404)

                file_data = raw_entry["data"]
                SR_VALUE = raw_entry.get("SR", 3000)

                if bearingLocationDatas['velocity']['calibrationValue'].get(axis_mapping[axis_name].lower()) != 1:
                    file_data = np.array(file_data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[axis_name].lower()]

                if len(file_data) > 25000:
                    SR_VALUE = 10000
                    if data["Type"] == 'Velocity':
                        response_data = velocityConvert32Demo(file_data, SR_VALUE, MachineDatas['rpm'], bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'])
                    elif data["Type"] == 'Acceleration':
                        response_data = accelerationConvert32Demo(file_data, SR_VALUE)
                    elif data["Type"] == 'Acceleration Envelope':
                        response_data = accelerationEnvelopeConvert32Demo(file_data, SR_VALUE)
                else:
                    lowpass_values = (
                        bearingLocationDatas['velocity'].get('lowpassCutoffFrequency', 1000),
                        bearingLocationDatas['velocity'].get('lowpassOrder', 2)
                    )

                    if data["Type"] == 'Velocity':
                        if SR_VALUE == 3000:
                            response_data = velocityConvertDemo1(file_data, SR_VALUE, (
                                bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                                bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values)
                        else:
                            response_data = velocityConvertHighResolution(file_data, SR_VALUE, raw_entry.get('NOS'),
                                (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                                 bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values)

                    elif data["Type"] == 'Acceleration':
                        if SR_VALUE == 3000:
                            response_data = accelerationConvertDemo(file_data, SR_VALUE, (
                                bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],
                                bearingLocationDatas['acceleration']['highpassOrderFft']))
                        else:
                            response_data = accelerationConvertHighResolution(file_data, SR_VALUE, raw_entry.get('NOS'),
                                (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                                 bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values)

                    elif data["Type"] == 'Acceleration Envelope':
                        response_data = accelerationEnvelopeConvertDemo(file_data, SR_VALUE, (
                            bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],
                            bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))
            
            if bearingLocationDatas['onlineOfflineFlag'] == 1:
                number_of_data = 1
            else:
                number_of_data = 4

            parquet_filename = f"{data['Sensor_Name']}.parquet"
            if check_file_exists(parquet_filename):
                if latest:
                    start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) - timedelta(days=365)).timestamp())
                    all_history = read_from_parquet(parquet_filename, start_date_time, end_date_time, limit=number_of_data)
                    for _, row in all_history.iterrows():
                        axis_name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"
                else:
                    start_date_time = int((datetime.fromtimestamp(int(epoch_Date_Time)) - timedelta(days=365)).timestamp())
                    all_history = read_from_parquet(parquet_filename, start_date_time, int(epoch_Date_Time), limit=number_of_data, axis=axis_mapping[data["Axis_Id"]])

                if all_history.empty:
                    return JsonResponse({"Response": "Data not Found"}, status=404)

                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    for _, row in all_history.iterrows():
                        file_data = json.loads(row["data"])
                        epoch_Date_Time = row['timestamp']
                        if data["Axis_Id"] == "H-Axis" and row["axis"] == "H":
                            file_data = json.loads(row["data"])
                        elif data["Axis_Id"] == "V-Axis" and row["axis"] == "V":
                            file_data = json.loads(row["data"])
                        elif data["Axis_Id"] == "A-Axis" and row["axis"] == "A":
                            file_data = json.loads(row["data"])

                    if len(all_history) > 1:
                        file_data = append_parquet_data(all_history)

                    if bearingLocationDatas['onlineOfflineFlag'] == 1 or len(file_data) < 15000:
                        file_data = (file_data * (15000 // len(file_data) + 1))[:15000]

                    calib = bearingLocationDatas['velocity']['calibrationValue']
                    if calib['h'] != 1 or calib['v'] != 1 or calib['a'] != 1:
                        file_data = np.array(file_data) * calib[axis_mapping[data["Axis_Id"]].lower()]

                    if len(file_data) > 25000:
                        SR_VALUE = 10000
                        if data["Type"] == 'Velocity':
                            respond_data = velocityConvert24Demo(file_data, SR_VALUE, MachineDatas['rpm'],
                                                                    bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                                                                    bearingLocationDatas['velocity']['highpassOrderFft'])
                        elif data["Type"] == 'Acceleration':
                            respond_data = accelerationConvert32Demo(file_data, SR_VALUE)
                        elif data["Type"] == 'Acceleration Envelope':
                            respond_data = accelerationEnvelopeConvert32Demo(file_data, SR_VALUE)
                    else:
                        SR_VALUE = 3000
                        if data["Type"] == 'Velocity':
                            respond_data = velocityConvertDemo1(
                                file_data, SR_VALUE,
                                (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],
                                bearingLocationDatas['velocity']['highpassOrderFft']),
                                lowpass_values
                            )
                        elif data["Type"] == 'Acceleration':
                            respond_data = accelerationConvertDemo(
                                file_data, SR_VALUE,
                                (bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],
                                bearingLocationDatas['acceleration']['highpassOrderFft'])
                            )
                        elif data["Type"] == 'Acceleration Envelope':
                            respond_data = accelerationEnvelopeConvertDemo(
                                file_data, SR_VALUE,
                                (bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],
                                bearingLocationDatas['accelerationEnvelope']['highpassOrderFft'])
                            )

                    respond_data = top10Fft(respond_data['FFT'])

                    return JsonResponse(respond_data, status=200, safe=False)

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return JsonResponse({"Response": "Data not Found"}, status=500)

def home(request):
    return HttpResponse("Django Server is running!")

# import highResolution

@csrf_exempt
@require_http_methods(["POST"])
def fft_high_resolution1_view(request):
    data = json.loads(request.body)
    print("fft:", data)

    latest = False
    axis_mapping = {
        "H-Axis": "H",
        "V-Axis": "V",
        "A-Axis": "A"
    }

    try:
        # Start of the day in UTC
        start_date_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        if "date_Time" not in data:
            end_date_time = int(datetime.now(timezone.utc).timestamp())

            epoch_data = list(
                db["ParameterTrend"]
                .find({
                    "BearingLoactionId": ObjectId(data["Sensor_Name"]),
                    "axis": axis_mapping[data["Axis_Id"]],
                    "rawDataPresent": True,
                    "epochTime": {
                        "$gte": int(start_date_time.timestamp()),
                        "$lte": end_date_time
                    }
                })
                .sort("_id", DESCENDING)
                .limit(1)
            )

            if epoch_data:
                epoch_date_time = epoch_data[0]["epochTime"]
            else:
                fallback_time = datetime.now(timezone.utc) + timedelta(days=-2)
                epoch_date_time = int(fallback_time.timestamp())
                latest = True
        else:
            epoch_date_time = data["date_Time"]

        data_date_time = datetime.utcfromtimestamp(int(str(epoch_date_time))).replace(tzinfo=timezone.utc)
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["Sensor_Name"])})
        machineDatas = db["Machine"].find_one({"_id": ObjectId(data["Machine_Name"])})

        axis_name = data["Axis_Id"]

        if data["Type"].lower() in ['velocity', 'acceleration']:
            axis_key = axis_mapping.get(data["Axis_Id"], "").lower()

            floor_noise_percentage = (
                bearingLocationDatas
                .get(data["Type"].lower(), {})
                .get('highResolutionFloorNoiseThresholdPercentage', {})
                .get(axis_key, 2)
            )

            lowpass_values = (
                bearingLocationDatas[data["Type"].lower()].get('lowpassCutoffFrequency', 1000),
                bearingLocationDatas[data["Type"].lower()].get('lowpassOrder', 2)
            )

            highpass_values = (
                bearingLocationDatas[data["Type"].lower()].get('highResolutionHighpassCutoffFrequency', 10),
                bearingLocationDatas[data["Type"].lower()].get('lowpassOrder', 4)
            )

            high_resolution_fmax = bearingLocationDatas.get('highResolutionFmax', 25)

        if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
            highResolutionNoOflines = bearingLocationDatas.get('highResolutionNoOflines', 20000)
            
            if data["Type"].lower() in ['velocity', 'acceleration']:
                fmax = bearingLocationDatas.get('highResolutionFmax', 25)
                NoOflines = bearingLocationDatas.get('highResolutionNoOflines', 1000)

                if (fmax, NoOflines) in update_fmax_noOfLine_Offline_map:
                    fmax, NoOflines = update_fmax_noOfLine_Offline_map[(fmax, NoOflines)]

            highResolutionFmax, NoOflines = 1000, 500000

            if data.get("latest"):
                start_date_Time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-365)).timestamp())
                All_History = read_from_parquet(f"{data['Sensor_Name']}.parquet", start_date_Time, epoch_Date_Time, limit=1)

                for index, row in All_History.iterrows():
                    axis_Name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"
            else:
                All_History = read_from_parquet(f"{data['Sensor_Name']}.parquet", epoch_Date_Time)

            if All_History.empty:
                return JsonResponse({"Response": "Data not Founda1"}, status=404)

            for index, row in All_History.iterrows():
                File_Data = json.loads(row['data'])[axis_mapping[axis_Name]]
                epoch_Date_Time = row['timestamp']
            
            OfflineDataStore = list(db["OfflineDataStore"].find({ "bearingLocationId": ObjectId(data["Sensor_Name"]), "epochTime": epoch_Date_Time }))
            if OfflineDataStore:
                OfflineDataStore = OfflineDataStore[0]
            else:
                OfflineDataStore = {}

            if len(File_Data) != 30000 and 'datatype' in OfflineDataStore and OfflineDataStore['datatype'] in ['24bit', '24bit-13C']:
                SR_VALUE = OfflineDataStore['sr']
                
                # Process data based on type
                if data["Type"] == 'Velocity':
                    pass
                    # RespondData = highResolution.Velocity_Convert_HighResolution_online(File_Data, SR_VALUE, NoOflines, highResolutionFmax, bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'], floorNoisePercentage)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            elif 'datatype' in OfflineDataStore and OfflineDataStore['datatype'] == '32bit':
                SR_VALUE = OfflineDataStore['sr']
                
                # Process data based on type
                if data["Type"] == 'Velocity':
                    pass
                    # RespondData = highResolution.Velocity_Convert_HighResolution_online(File_Data, SR_VALUE, NoOflines, highResolutionFmax, bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'], floorNoisePercentage)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            else:
                SR_VALUE = 20000
                if data["Type"] == 'Velocity':
                    pass
                    # RespondData = highResolution.Velocity_Convert_HighResolution_online(File_Data, SR_VALUE, NoOflines, highResolutionFmax, bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'], floorNoisePercentage)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)

        else:
            # Handle ONLINE case
            time_difference = datetime.now() - datetime.fromtimestamp(epoch_Date_Time)  # Assuming epoch_Date_Time is provided
            if time_difference.total_seconds() > 0:
                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    highResolutionNoOflines = bearingLocationDatas[data["Type"].lower()].get('highResolutionNoOflines', 6000)

                    if bearingLocationDatas['onlineOfflineFlag'] == 1:
                        numberOfData = 1
                    else:
                        numberOfData = 5

                    fullFileData = list(db["RawData"].find({ "BearingLoactionId": ObjectId(data["Sensor_Name"]), "axis": axis_mapping[data["Axis_Id"]], "epochTime": epoch_Date_Time }))
                    SR_VALUE = fullFileData[0].get('SR', 3000)
                    File_Data = fullFileData[0]['data']

                    if bearingLocationDatas['onlineOfflineFlag'] == 1 or len(File_Data) < 15000:
                        File_Data = (File_Data * (15000 // len(File_Data) + 1))[:15000]

                    if bearingLocationDatas['velocity']['calibrationValue']['h'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['v'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['a'] != 1:
                        File_Data = np.array(File_Data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[data["Axis_Id"]].lower()]

                    if len(File_Data) > 25000:
                        highResolutionNoOflines = bearingLocationDatas[data["Type"].lower()].get('highResolutionNoOflines', 20000)
                        SR_VALUE = 10000

                        # Process data based on type
                        if data["Type"] == 'Velocity':
                            pass
                            # RespondData = highResolution.Velocity_Convert_HighResolution_online(File_Data, SR_VALUE, highResolutionNoOflines, highResolutionFmax, highpass_values[0], highpass_values[1], floorNoisePercentage)
                        elif data["Type"] == 'Acceleration':
                            RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                        elif data["Type"] == 'Acceleration Envelope':
                            RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
                    else:
                        if data["Type"] == 'Velocity':
                            if SR_VALUE == 3000:
                                pass
                                # RespondData = highResolution.Velocity_Convert_HighResolution_online(File_Data, SR_VALUE, highResolutionNoOflines, highResolutionFmax, highpass_values[0], highpass_values[1], floorNoisePercentage)
                            else:
                                RespondData = velocityConvertHighResolution(File_Data, SR_VALUE, fullFileData[0]['NOS'], (highpass_values[0], highpass_values[1]), lowpass_values, floorNoisePercentage)

                        elif data["Type"] == 'Acceleration':
                            if SR_VALUE == 3000:
                                RespondData = accelerationConvertHighResolution(File_Data, SR_VALUE, (highpass_values[0], highpass_values[1]))
                            else:
                                RespondData = accelerationConvertHighResolution(File_Data, SR_VALUE, fullFileData[0]['NOS'], (highpass_values[0], highpass_values[1]), lowpass_values)

                        elif data["Type"] == 'Acceleration Envelope':
                            RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (highpass_values[0], highpass_values[1]))

                else:
                    if bearingLocationDatas.get('bearingLocationType') == "OFFLINE":
                        high_resolution_no_of_lines = bearingLocationDatas.get('highResolutionNoOflines', 20000)
                        if request.GET["Type"].lower() in ['velocity', 'acceleration']:
                            fmax = bearingLocationDatas.get('highResolutionFmax', 25)
                            no_of_lines = bearingLocationDatas.get('highResolutionNoOflines', 1000)

                            if (fmax, no_of_lines) in update_fmax_noOfLine_Offline_map:
                                fmax, no_of_lines = update_fmax_noOfLine_Offline_map[(fmax, no_of_lines)]

                        high_resolution_fmax, no_of_lines = 1000, 500000

                        if latest:
                            start_date_time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-365)).timestamp())
                            all_history = read_from_parquet((data["Sensor_Name"]) + ".parquet", start_date_time, end_date_time, limit=1)

                            for index, row in all_history.iterrows():
                                axis_name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"
                        else:
                            all_history = read_from_parquet((data["Sensor_Name"] + ".parquet", int(epoch_date_time)))

                        if all_history.empty:
                            return JsonResponse({"Response": "Data not Founda1"}, status=404)

                        for index, row in all_history.iterrows():
                            file_data = json.loads(row['data'])[axis_mapping[axis_name]]
                            epoch_date_time = row['timestamp']

                        offline_data_store = list(OfflineDataStore.objects.filter(bearingLocationId=ObjectId((data["Sensor_Name"]), epochTime=epoch_date_time)))
                        if offline_data_store:
                            offline_data_store = offline_data_store[0]
                        else:
                            offline_data_store = {}

                        if len(file_data) != 30000 and 'datatype' in offline_data_store and offline_data_store['datatype'] in ['24bit', '24bit-13C']:
                            sr_value = offline_data_store['sr']

                            if request.GET["Type"] == 'Velocity':
                                pass
                                # respond_data = highResolution.Velocity_Convert_HighResolution_online(file_data, sr_value, no_of_lines, high_resolution_fmax, bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'], floorNoisePercentage)
                            elif request.GET["Type"] == 'Acceleration':
                                respond_data = accelerationConvert32Demo(file_data, sr_value)
                            elif request.GET["Type"] == 'Acceleration Envelope':
                                respond_data = accelerationEnvelopeConvert32Demo(file_data, sr_value)
                        elif 'datatype' in offline_data_store and offline_data_store['datatype'] == '32bit':
                            sr_value = offline_data_store['sr']
                            if request.GET["Type"] == 'Velocity':
                                pass
                                # respond_data = highResolution.Velocity_Convert_HighResolution_online(file_data, sr_value, no_of_lines, high_resolution_fmax, bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'], floorNoisePercentage)
                            elif request.GET["Type"] == 'Acceleration':
                                respond_data = accelerationConvert32Demo(file_data, sr_value)
                            elif request.GET["Type"] == 'Acceleration Envelope':
                                respond_data = accelerationEnvelopeConvert32Demo(file_data, sr_value)
                        else:
                            sr_value = 20000
                            if request.GET["Type"] == 'Velocity':
                                pass
                                # respond_data = highResolution.Velocity_Convert_HighResolution_online(file_data, sr_value, no_of_lines, high_resolution_fmax, bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'], floorNoisePercentage)
                            elif request.GET["Type"] == 'Acceleration':
                                respond_data = accelerationConvert32Demo(file_data, sr_value)
                            elif request.GET["Type"] == 'Acceleration Envelope':
                                respond_data = accelerationEnvelopeConvert32Demo(file_data, sr_value)

            else:
                if time_difference.total_seconds() > 0:
                    if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                        high_resolution_no_of_lines = bearingLocationDatas[request.GET["Type"].lower()].get('highResolutionNoOflines', 6000)

                        if bearingLocationDatas['onlineOfflineFlag'] == 1:
                            number_of_data = 1
                        else:
                            number_of_data = 5

                        full_file_data = list(db["RawData"].find({"BearingLoactionId": ObjectId((data["Sensor_Name"])), "axis": axis_mapping[request.GET["Axis_Id"]], "epochTime": epoch_date_time}))
                        sr_value = full_file_data[0].get('SR', 3000)
                        file_data = full_file_data[0]['data']

                        if bearingLocationDatas['onlineOfflineFlag'] == 1 or len(file_data) < 15000:
                            file_data = (file_data * (15000 // len(file_data) + 1))[:15000]

                        if bearingLocationDatas['velocity']['calibrationValue']['h'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['v'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['a'] != 1:
                            file_data = np.array(file_data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[request.GET["Axis_Id"]].lower()]

                        if len(file_data) > 25000:
                            high_resolution_no_of_lines = bearingLocationDatas[request.GET["Type"].lower()].get('highResolutionNoOflines', 20000)
                            sr_value = 10000

                            if request.GET["Type"] == 'Velocity':
                                pass
                                # respond_data = highResolution.Velocity_Convert_HighResolution_online(file_data, sr_value, high_resolution_no_of_lines, high_resolution_fmax, highpass_values[0], highpass_values[1], floorNoisePercentage)
                            elif request.GET["Type"] == 'Acceleration':
                                respond_data = accelerationConvert32Demo(file_data, sr_value)
                            elif request.GET["Type"] == 'Acceleration Envelope':
                                respond_data = accelerationEnvelopeConvert32Demo(file_data, sr_value)
                        else:
                            high_resolution_no_of_lines = bearingLocationDatas[request.GET["Type"].lower()].get('highResolutionNoOflines', 6000)
                            sr_value = 3000
                            if request.GET["Type"] == 'Velocity':
                                if sr_value == 3000:
                                    pass
                                    # respond_data = highResolution.Velocity_Convert_HighResolution_online(file_data, sr_value, high_resolution_no_of_lines, high_resolution_fmax, highpass_values[0], highpass_values[1], floorNoisePercentage)
                                else:
                                    respond_data = velocityConvertHighResolution(file_data, sr_value, full_file_data[0]['NOS'], (highpass_values[0], highpass_values[1]), lowpass_values, floorNoisePercentage)

                            elif request.GET["Type"] == 'Acceleration':
                                if sr_value == 3000:
                                    respond_data = accelerationConvertHighResolution(file_data, sr_value, (highpass_values[0], highpass_values[1]))
                                else:
                                    respond_data = accelerationConvertHighResolution(file_data, sr_value, full_file_data[0]['NOS'], (highpass_values[0], highpass_values[1]), lowpass_values)

                            elif request.GET["Type"] == 'Acceleration Envelope':
                                respond_data = accelerationConvertDemo(file_data, sr_value, (highpass_values[0], highpass_values[1]))

            if isinstance(respond_data, dict):
                keys_to_remove = ['Timeseries', 'twf_max', 'twf_min']
                for key in keys_to_remove:
                    respond_data.pop(key, None)

            if "date_Time" not in request.GET:
                respond_data["epochTime"] = epoch_date_time

            return JsonResponse(respond_data, status=200)

    except Exception as e:
        print(traceback.print_exc())  # This will print the stack trace
        return JsonResponse({"Response": "Data not Found"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def set_calibration_value_in_file(request):
    try:
        data = json.loads(request.body)

        if "Analytics_Types" in data or data.get("Analytics_Types") == ['LF', 'MF', 'HF']:
            update_field_in_parquet(
                data['Sensor_Name'] + ".parquet",
                machineId=data['Machine_Name'],
                timestamp=data.get('date_Time'),
                cutoff=data.get('Cutoff'),
                floorNoiseThresholdPercentage=data.get('floorNoiseThresholdPercentage'),
                floorNoiseAttenuationFactor=data.get('floorNoiseAttenuationFactor')
            )
        else:
            return JsonResponse({"Response": "OM is not supported"}, status=404)

        return JsonResponse({"Response": "Values are set"}, status=200)

    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return JsonResponse({"Response": "Data not Found"}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def startFftHighResolution(request):
    data = json.loads(request.body)
    db = client[settings.MONGODB_NAME]
    print("fft: ",data)
    repeatAppend = int(data['repeat_Append'])
    latest = False
    try:
        # start_date_time = datetime.now(timezone.utc) + timedelta(days=-1)
        start_date_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        axis_mapping = {
            "H-Axis": "H",
            "V-Axis": "V",
            "A-Axis": "A"
        }
        if "date_Time" not in data:
            end_date_Time = int((datetime.now().astimezone(settings.GMT_TIMEZONE)).timestamp())
            epoch_Data = list(db["ParameterTrend"].find({ "BearingLoactionId": ObjectId(data["Sensor_Name"]), "axis": axis_mapping[data["Axis_Id"]], "rawDataPresent": True, "epochTime": {"$gte": int(start_date_time.timestamp()), "$lte": end_date_Time} }).sort([("_id", -1)]).limit(1))
            if epoch_Data != []:

                epoch_Date_Time = epoch_Data[0]["epochTime"]
            else:
                epoch_Data = datetime.now(timezone.utc) + timedelta(days=-2)
                epoch_Date_Time = int(epoch_Data.timestamp())
                latest = True

        else:
            epoch_Date_Time = data["date_Time"]
            
        data_date_time = datetime.utcfromtimestamp(int(str(epoch_Date_Time))).replace(tzinfo=timezone.utc)
        time_difference = data_date_time - start_date_time

        bearingLocationDatas = db["BearingLocation"].find_one({"_id": ObjectId(data["Sensor_Name"])})
        MachineDatas = db["Machine"].find_one({"_id": ObjectId(data["Machine_Name"])})
        
        RespondData = []
        File_Data = []
        # data_timestamp = ''
        axis_Name = data["Axis_Id"]
        
        if data["Type"].lower() in ['velocity', 'acceleration']:
            lowpass_values = (
                        bearingLocationDatas[data["Type"].lower()].get('lowpassCutoffFrequency', 1000),
                        bearingLocationDatas[data["Type"].lower()].get('lowpassOrder', 2)
                    )
            fmax = bearingLocationDatas.get('fmax', 25)
            NoOflines = bearingLocationDatas.get('noOflines', 25)

            # fmax, NoOflines = bearingLocationDatas['fmax'].get('lowpassCutoffFrequency', 25), bearingLocationDatas['noOflines'].get('lowpassCutoffFrequency', 125)
            if (fmax, NoOflines) in update_fmax_noOfLine_map:
                fmax, NoOflines = update_fmax_noOfLine_map[(fmax, NoOflines)]

        if 'bearingLocationType' in bearingLocationDatas and bearingLocationDatas['bearingLocationType'] == "OFFLINE":
            if latest:
                start_date_Time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-int(365))).timestamp())
                if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                    All_History = read_from_parquet(data["Sensor_Name"]+".parquet", start_date_Time, end_date_Time, limit = 1)
                elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                    All_History = read_from_new_parquet(data["Sensor_Name"]+".parquet", data['Machine_Name'], start_date_Time, end_date_Time, limit = 1 )

                # All_History = read_from_parquet(data["Sensor_Name"]+".parquet", start_date_Time, end_date_Time, limit = 100)


                for index, row in All_History.iterrows():
                    axis_Name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"

            else:
                if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                    All_History = read_from_parquet(data["Sensor_Name"]+".parquet", int(epoch_Date_Time))
                elif data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                    All_History = read_from_new_parquet(data["Sensor_Name"]+".parquet", data['Machine_Name'], int(epoch_Date_Time))

            if All_History.empty:
                return {"Response": "Data not Founda1"}, 404
            
            for index, row in All_History.iterrows():
                File_Data = json.loads(row['data'])[axis_mapping[axis_Name]]
                epoch_Date_Time = row['timestamp']
                if 'SR' in row:
                    if row['SR'] == 'null':
                        SR = 10000
                    else:
                        SR = int(row['SR'])
                    rpm = row['rpm']
                    fMax = int(row['fMax'])
                    noOfLines = int(row['noOfLines'])
                    cutoff = int(float(row['cutoff']))
                    floorNoiseThresholdPercentage = float(row['floorNoiseThresholdPercentage'])
                    floorNoiseAttenuationFactor = float(row['floorNoiseAttenuationFactor'])

            OfflineDataStore = list(db["OfflineDataStore"].find({ "bearingLocationId": ObjectId(data["Sensor_Name"]), "epochTime": epoch_Date_Time }))
            if OfflineDataStore:
                OfflineDataStore = OfflineDataStore[0]
            else:
                OfflineDataStore = {}

            if len(File_Data) != 30000 and 'datatype' in OfflineDataStore and OfflineDataStore['datatype'] in ['24bit', '24bit-13C']:
                if "Analytics_Types" not in data or data['Analytics_Types'] == "OM":
                    SR_VALUE = OfflineDataStore['sr']
                    rpm = MachineDatas['rpm']
                    cutoff = bearingLocationDatas['velocity']['highpassCutoffFrequencyFft']
                    fMax = None
                    floorNoiseThresholdPercentage = 5
                    floorNoiseAttenuationFactor = 1

                else:
                    SR_VALUE = SR
                    rpm = rpm
                    cutoff = cutoff

                File_Data = File_Data * repeatAppend 
                
                if data["Type"] == 'Velocity':
                    RespondData = velocityConvert24Demo(File_Data, SR_VALUE,  rpm, cutoff, bearingLocationDatas['velocity']['highpassOrderFft'], fmax = fMax, floorNoiseThresholdPercentage=floorNoiseThresholdPercentage, floorNoiseAttenuationFactor=floorNoiseAttenuationFactor, highResolution = repeatAppend)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE, fmax = fMax)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE, fmax = fMax)
            elif 'datatype' in OfflineDataStore and OfflineDataStore['datatype'] == '32bit':
                SR_VALUE = OfflineDataStore['sr']
                if data["Type"] == 'Velocity':
                    RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            else:
                SR_VALUE = 20000
                if data["Type"] == 'Velocity':
                    RespondData = velocityConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration':
                    RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                elif data["Type"] == 'Acceleration Envelope':
                    RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
            if "Analytics_Types" in data and data['Analytics_Types'] in ['LF', 'MF', 'HF']:
                RespondData['SR'] = SR
                RespondData['rpm'] = rpm
                RespondData['fMax'] = fMax
                RespondData['noOfLines'] = noOfLines
                RespondData['cutoff'] = cutoff
                RespondData['floorNoiseThresholdPercentage'] = floorNoiseThresholdPercentage
                RespondData['floorNoiseAttenuationFactor'] = floorNoiseAttenuationFactor
        else:
            if time_difference.total_seconds() > 0:
                if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                    
                    if bearingLocationDatas['onlineOfflineFlag'] == 1:
                        numberOfData = 1
                    else:
                        numberOfData = 5
                    
                    fullFileData = list(db["RawData"].find({ "BearingLoactionId": ObjectId(data["Sensor_Name"]), "axis": axis_mapping[data["Axis_Id"]], "epochTime": epoch_Date_Time }))
                    SR_VALUE = fullFileData[0].get('SR', 3000)
                    File_Data = fullFileData[0]['data']
                    # File_Data1 = get_oldData(data["Sensor_Name"], axis_mapping[data["Axis_Id"]],epoch_Date_Time, limit = numberOfData)

                    if bearingLocationDatas['onlineOfflineFlag'] == 1 or len(File_Data) < 15000:
                        File_Data = (File_Data * (15000 // len(File_Data) + 1))[:15000]
                    
                    if bearingLocationDatas['velocity']['calibrationValue']['h'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['v'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['a'] != 1:
                        File_Data = np.array(File_Data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[data["Axis_Id"]].lower()] 

                    if len(File_Data) > 25000:
                        SR_VALUE = 10000

                        File_Data = File_Data * repeatAppend

                        if data["Type"] == 'Velocity':
                            RespondData = velocityConvert24Demo(File_Data, SR_VALUE,  MachineDatas['rpm'], bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'])
                        elif data["Type"] == 'Acceleration':
                            RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                        elif data["Type"] == 'Acceleration Envelope':
                            RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
                    else:
                        
                        File_Data = File_Data * repeatAppend
                        if data["Type"] == 'Velocity':
                            if SR_VALUE == 3000:
                                RespondData = velocityConvertDemo1(File_Data, SR_VALUE, (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values, fmax = fmax)
                            else:
                                RespondData = velocityConvertHighResolution(File_Data, SR_VALUE, fullFileData[0]['NOS'], (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values, fmax = fmax)
                        elif data["Type"] == 'Acceleration':
                            if SR_VALUE == 3000:
                                RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],bearingLocationDatas['acceleration']['highpassOrderFft']), fmax = fmax)
                            else:
                                RespondData = accelerationConvertHighResolution(File_Data, SR_VALUE, fullFileData[0]['NOS'], (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values, fmax = fmax)
                        elif data["Type"] == 'Acceleration Envelope':
                            RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))

            else:
                if bearingLocationDatas['onlineOfflineFlag'] == 1:
                    numberOfData = 1
                else:
                    numberOfData = 4

                if check_file_exists(data["Sensor_Name"]+".parquet"):
                    if latest:
                        start_date_Time = int((datetime.now().astimezone(settings.GMT_TIMEZONE) + timedelta(days=-int(365))).timestamp())
                        All_History = read_from_parquet(data["Sensor_Name"]+".parquet", start_date_Time, end_date_Time, limit = numberOfData)
                        for index, row in All_History.iterrows():
                            axis_Name = str(list(json.loads(row['data']).keys())[0]) + "-Axis"

                    else:
                        start_date_Time = int((datetime.fromtimestamp(int(epoch_Date_Time)) + timedelta(days=-int(365))).timestamp())
                        All_History = read_from_parquet(data["Sensor_Name"]+".parquet", start_date_Time, int(epoch_Date_Time), limit = numberOfData, axis = axis_mapping[data["Axis_Id"]])
            
                    if All_History.empty:
                        return {"Response": "Data not Found"}, 404
                    
                    if 'bearingLocationType' not in bearingLocationDatas or bearingLocationDatas['bearingLocationType'] == "ONLINE":
                        for index, row in All_History.iterrows():
                            File_Data = json.loads(row["data"])
                            epoch_Date_Time = row['timestamp']
                            if data["Axis_Id"] == "H-Axis" and row["axis"] == "H":
                                File_Data = json.loads(row["data"])
                            elif data["Axis_Id"] == "V-Axis" and row["axis"] == "V":
                                File_Data = json.loads(row["data"])
                            if data["Axis_Id"] == "A-Axis" and row["axis"] == "A":
                                File_Data = json.loads(row["data"])
                                
                        if len(All_History) > 1:
                            File_Data = append_parquet_data(All_History)

                        if bearingLocationDatas['onlineOfflineFlag'] == 1 or len(File_Data) < 15000:
                            File_Data = (File_Data * (15000 // len(File_Data) + 1))[:15000]

                        if bearingLocationDatas['velocity']['calibrationValue']['h'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['v'] != 1 or bearingLocationDatas['velocity']['calibrationValue']['a'] != 1:
                            File_Data = np.array(File_Data) * bearingLocationDatas['velocity']['calibrationValue'][axis_mapping[data["Axis_Id"]].lower()] 

                        if len(File_Data) > 25000:
                            
                            File_Data = File_Data * repeatAppend
                            SR_VALUE = 10000
                            if data["Type"] == 'Velocity':
                                RespondData = velocityConvert24Demo(File_Data, SR_VALUE,  MachineDatas['rpm'], bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'])
                            elif data["Type"] == 'Acceleration':
                                RespondData = accelerationConvert32Demo(File_Data, SR_VALUE)
                            elif data["Type"] == 'Acceleration Envelope':
                                RespondData = accelerationEnvelopeConvert32Demo(File_Data, SR_VALUE)
                        else:
                            File_Data = File_Data * repeatAppend
                            SR_VALUE = 3000
                            if data["Type"] == 'Velocity':
                                if SR_VALUE == 3000:
                                    RespondData = velocityConvertDemo1(File_Data, SR_VALUE, (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values, fmax = fmax)
                                else:
                                    RespondData = velocityConvertHighResolution(File_Data, SR_VALUE, fullFileData[0]['NOS'], (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values, fmax = fmax)

                                    # RespondData = velocityConvertDemo1(File_Data, SR_VALUE, (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values)
                            elif data["Type"] == 'Acceleration':
                                if SR_VALUE == 3000:
                                    RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],bearingLocationDatas['acceleration']['highpassOrderFft']), fmax = fmax)
                                else:
                                    RespondData = accelerationConvertHighResolution(File_Data, SR_VALUE, fullFileData[0]['NOS'], (bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'],bearingLocationDatas['velocity']['highpassOrderFft']), lowpass_values, fmax = fmax)

                                    # RespondData = accelerationConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['acceleration']['highpassCutoffFrequencyFft'],bearingLocationDatas['acceleration']['highpassOrderFft']))
                            elif data["Type"] == 'Acceleration Envelope':
                                RespondData = accelerationEnvelopeConvertDemo(File_Data, SR_VALUE, (bearingLocationDatas['accelerationEnvelope']['highpassCutoffFrequencyFft'],bearingLocationDatas['accelerationEnvelope']['highpassOrderFft']))

        keys_to_remove = ['Timeseries', 'twf_max', 'twf_min']
        for key in keys_to_remove:
            RespondData.pop(key, None)

        if "date_Time" not in data:
            RespondData["epochTime"] = epoch_Date_Time

        return RespondData, 200
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return {"Response": "Data not Found"}, 500

@csrf_exempt
def delete_temp(request):
    if request.method == 'POST':
        try:
            meta_data = json.loads(request.body)
            bearing_location_id = meta_data.get("bearingLocationId")
            
            # Perform deletion logic here if needed

            return JsonResponse({"Response": "Deleted"}, status=200)
        except Exception as e:
            return JsonResponse({"Response": "Invalid Request"}, status=400)
    return JsonResponse({"Response": "Method Not Allowed"}, status=405)