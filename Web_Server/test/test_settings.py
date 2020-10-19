URL = "http://localhost:8082"
superusername = "admin"
superuserpassword = "ari900ari900"
testusername = "bemosstester"
testuserpassword = "ari900ari900"

BUILDING_NAME = 'Building1'


DEVICE_INFO = {"RTH8580WF":{"username": "bemcontrols.app@gmail.com", "password": "Ari900_Ari900", "device_model": "RTH8580WF"
                              , "device_type":"HVAC", "api":"API_Honeywell","built_in_schedule":True,'cloud_device':True},
                 "ICM100": {"username": "mkuzlu", "password": "DRTeam@900",
                               "device_model": "ICM100", "device_type":"HVAC","api":"API_ICM","built_in_schedule":True,'cloud_device':True},
               "Dimmer":{"device_model":"Dimmer","device_type":"Lighting","api":"API_WeMoDimmer","built_in_schedule":False,"cloud_device":False}}



lighting_schedule_data = [
{
    u'monday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 6, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}],
    u'tuesday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}],
    u'friday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}],
    u'wednesday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}],
    u'thursday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}],
    u'sunday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}],
    u'saturday': [
        {u'status': u'ON', u'brightness': 66, u'nickname': u'Period1', u'id': u'1', u'at': 0},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 30},
        {u'status': u'ON', u'brightness': 100, u'nickname': u'Period3', u'id': u'3', u'at': 60},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 90}]
},
{
    u'monday': [
        {u'status': u'ON', u'brightness': 36, u'nickname': u'Period1', u'id': u'1', u'at': 30},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 120},
        {u'status': u'ON', u'brightness': 30, u'nickname': u'Period3', u'id': u'3', u'at': 210},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 270}],
    u'tuesday': [
        {u'status': u'ON', u'brightness': 76, u'nickname': u'Period1', u'id': u'1', u'at': 30},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 90},
        {u'status': u'ON', u'brightness': 30, u'nickname': u'Period3', u'id': u'3', u'at': 120},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 150}],
    u'friday': [
        {u'status': u'ON', u'brightness': 86, u'nickname': u'Period1', u'id': u'1', u'at': 150},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 270},
        {u'status': u'ON', u'brightness': 70, u'nickname': u'Period3', u'id': u'3', u'at': 300},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 330}],
    u'wednesday': [
        {u'status': u'ON', u'brightness': 36, u'nickname': u'Period1', u'id': u'1', u'at': 360},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 390},
        {u'status': u'ON', u'brightness': 20, u'nickname': u'Period3', u'id': u'3', u'at': 420},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 450}],
    u'thursday': [
        {u'status': u'ON', u'brightness': 26, u'nickname': u'Period1', u'id': u'1', u'at': 480},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 510},
        {u'status': u'ON', u'brightness': 10, u'nickname': u'Period3', u'id': u'3', u'at': 530},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 560}],
    u'sunday': [
        {u'status': u'ON', u'brightness': 86, u'nickname': u'Period1', u'id': u'1', u'at': 30},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 120},
        {u'status': u'ON', u'brightness': 70, u'nickname': u'Period3', u'id': u'3', u'at': 210},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 270}],
    u'saturday': [
        {u'status': u'ON', u'brightness': 36, u'nickname': u'Period1', u'id': u'1', u'at': 480},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period2', u'id': u'2', u'at': 510},
        {u'status': u'ON', u'brightness': 20, u'nickname': u'Period3', u'id': u'3', u'at': 530},
        {u'status': u'OFF', u'brightness': 0, u'nickname': u'Period4', u'id': u'4', u'at': 560}]
}
]
thermostat_schedule_data = [
    {
    u'monday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                 {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                 {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                 {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}],
     u'tuesday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                  {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                  {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                  {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}],
     u'friday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                 {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                 {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                 {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}],
     u'wednesday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                    {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                    {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                    {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}],
     u'thursday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                   {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                   {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                   {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}],
     u'sunday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                 {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                 {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                 {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}],
     u'saturday': [{u'cool_setpoint': 75, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 70, u'at': 390},
                   {u'cool_setpoint': 72, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 72, u'at': 480},
                   {u'cool_setpoint': 72, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 70, u'at': 1020},
                   {u'cool_setpoint': 78, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 68, u'at': 1320}]
     },
    {
    u'monday': [{u'cool_setpoint': 76, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 80, u'at': 390},
                 {u'cool_setpoint': 73, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 83, u'at': 480},
                 {u'cool_setpoint': 74, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 87, u'at': 1020},
                 {u'cool_setpoint': 79, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}],
     u'tuesday': [{u'cool_setpoint': 76, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 89, u'at': 390},
                  {u'cool_setpoint': 77, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 82, u'at': 480},
                  {u'cool_setpoint': 73, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 80, u'at': 1020},
                  {u'cool_setpoint': 79, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}],
     u'friday': [{u'cool_setpoint': 71, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 80, u'at': 390},
                 {u'cool_setpoint': 65, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 82, u'at': 480},
                 {u'cool_setpoint': 68, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 80, u'at': 1020},
                 {u'cool_setpoint': 79, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}],
     u'wednesday': [{u'cool_setpoint': 74, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 80, u'at': 390},
                    {u'cool_setpoint': 73, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 82, u'at': 480},
                    {u'cool_setpoint': 71, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 80, u'at': 1020},
                    {u'cool_setpoint': 70, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}],
     u'thursday': [{u'cool_setpoint': 73, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 80, u'at': 390},
                   {u'cool_setpoint': 75, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 82, u'at': 480},
                   {u'cool_setpoint': 76, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 80, u'at': 1020},
                   {u'cool_setpoint': 73, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}],
     u'sunday': [{u'cool_setpoint': 72, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 80, u'at': 390},
                 {u'cool_setpoint': 71, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 82, u'at': 480},
                 {u'cool_setpoint': 73, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 80, u'at': 1020},
                 {u'cool_setpoint': 75, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}],
     u'saturday': [{u'cool_setpoint': 76, u'nickname': u'WAKE', u'id': 0, u'heat_setpoint': 80, u'at': 390},
                   {u'cool_setpoint': 77, u'nickname': u'LEAVE', u'id': 1, u'heat_setpoint': 82, u'at': 480},
                   {u'cool_setpoint': 73, u'nickname': u'RETURN', u'id': 2, u'heat_setpoint': 80, u'at': 1020},
                   {u'cool_setpoint': 75, u'nickname': u'SLEEP', u'id': 3, u'heat_setpoint': 88, u'at': 1320}]
    }
    ]


test_control_commands = {"ICM100":[
{u'fan_mode': u'ON', u'thermostat_mode': u'OFF', u'anti_tampering': u'ENABLED'},
{ u'fan_mode': u'AUTO', u'thermostat_mode': u'COOL', u'cool_setpoint': 65, u'hold': u'TEMPORARY', u'anti_tampering': u'DISABLED'},
{u'fan_mode': u'ON', u'thermostat_mode': u'HEAT',  u'heat_setpoint': 85, u'hold': u'PERMANENT', u'anti_tampering': u'ENABLED'},
],
"RTH8580WF":[
{u'fan_mode': u'ON', u'thermostat_mode': u'HEAT',  u'heat_setpoint': 85, u'hold': u'PERMANENT', u'anti_tampering': u'ENABLED'},
{u'fan_mode': u'ON', u'thermostat_mode': u'OFF',  u'anti_tampering': u'ENABLED'},
{ u'fan_mode': u'AUTO', u'thermostat_mode': u'COOL', u'cool_setpoint': 65, u'hold': u'TEMPORARY', u'anti_tampering': u'DISABLED'},
],
"Dimmer":[
{"status":"ON","brightness":50},
{"status":"OFF"},
{"status":"ON","brightness":100}
]
}

test_schedule_lists = {"ICM100":thermostat_schedule_data,
                       "RTH8580WF":thermostat_schedule_data,
                       "Dimmer":lighting_schedule_data}

models_to_test = ['Dimmer','RTH8580WF']
#models_to_test = ['RTH8580WF']