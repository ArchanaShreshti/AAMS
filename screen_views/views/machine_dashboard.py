from django.conf import settings
from django.http import JsonResponse
from screen_views.constants import AXIS_ID_MAPPING, DEMO_MONGO_URI, PROD_MONGO_URI, TEST_MONGO_URI
from screen_views.constants import UPDATE_FMAX_NO_OF_LINE_MAP, UPDATE_FMAX_NO_OF_LINE_OFFLINE_MAP
import numpy as np
from screen_views.utils import *
import json
import base64
from django.views.decorators.http import require_http_methods

# Access settings
audio_directory = settings.AUDIO_DIRECTORY
mongo_uri = settings.MONGO_URI

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
                    # RespondData = Velocity_Convert_24_DEMO(File_Data, SR_VALUE,  MachineDatas['rpm'], bearingLocationDatas['velocity']['highpassCutoffFrequencyFft'], bearingLocationDatas['velocity']['highpassOrderFft'])
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
    
