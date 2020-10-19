import sys
sys.path.append('/home/bemoss/BEMOSS_PLUS')

from bemoss_lib.databases.cassandraAPI.cassandraDB import customQuery, makeConnection
import csv
import os
import datetime

today  = (datetime.datetime.now()-datetime.timedelta(hours=24)).isoformat()[0:10]



downloads = {"icm1_bgqbzcguerov_1":"T-13 Springs social room",  "icm1_bgqbyppscakd_1": "T-3 46 Children, Youth, & Fam",   "icm1_bgqbzonzdfsq_1":"T-12 Potomac room",
"icm1_bgqbvednmeuj_1":"T-1 8-12 Area Agency On Aging", "icm1_bgqbzjeasozn_1":"T-7 27 Mental Health & Disabl",
"wnc_401370_1":"power_5_Agency_Aging_Power","icm1_bgqbyancdjdz_1":"T-4 47 Dept of Family SVCS EX",  
"icm1_bgqbybnamlhj_1":"T-5 39A Veterans Affairs", 
"icm1_bgqbzhruhouv_1":"T-6 43 Office of the Director",  "icm1_bgqbzlzjhmbk_1":"T-9 77 CSEP",
"icm1_bgqbzkcoyfvf_1":"T-8 25 MGMT Services",
"icm1_bgqbznkgojde_1" :"T-11 Blue Crab Dining room", "wnc_381662_1":"power_12_Agency_Aging",    
"icm1_bgqbzmfdwycr_1":"t10-multipurpose",     "icm1_bgqbynxedgjs_1": "T-2 4-5 Area Agency On Aging"}

folder = today.replace('-','')
os.makedirs('/home/bemoss/BEMOSS_DATA/PGCOUNTY/'+folder+'/')
makeConnection()

for agent_id in downloads.keys():
    table = 'b' + agent_id.lower()
    qstring = "select * from bemossspace."+table+" where agent_id='"+agent_id.upper()+"' and date_id='"+today+"';"
    result = customQuery(qstring)
    filename = downloads[agent_id]+'-'+today+'.csv'
    resultFile = open('/home/bemoss/BEMOSS_DATA/PGCOUNTY/'+folder+'/'+filename, 'wb')
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerows(result)

