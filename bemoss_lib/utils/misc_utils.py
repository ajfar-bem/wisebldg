import re
def getTableName(building_id,device_model):
    tablename = "B" + str(building_id) + "_" + device_model.replace(" ", "_").replace("-", "_")
    tablename = re.sub(r'\W', '', tablename)
    return tablename