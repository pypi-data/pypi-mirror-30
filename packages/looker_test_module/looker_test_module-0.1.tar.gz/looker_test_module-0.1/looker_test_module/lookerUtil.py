import json
from configparser import ConfigParser
import requests
import snowflake.connector


# Properties File
config = ConfigParser()
config.read("./resources/properties.ini")
config.read("../resources/properties.ini")

# Read Looker Base_URL from Prop File
base_url=config.get("LOOKER","base_url")
client_id = config.get("LOOKER","client_id")
client_secret = config.get("LOOKER","client_secret")

# Snowflake Connection Properties
account=config.get("SNOWFLAKE","account")
user=config.get("SNOWFLAKE","user")
password=config.get("SNOWFLAKE","password")

############### This method will return the authentication token for further Looker API Calls #################
def login():
    login_url = base_url + "/api/3.0/login"
    querystring = {"client_id":client_id,"client_secret":client_secret}
    headers = {
        "content-type" : "application/json"
        }

    response = requests.request("POST", login_url, headers=headers, params=querystring)

    print ("Login url: " + login_url)
    print("Login response code: " + str(response.status_code))
    print("-------------")
    assert response.status_code == 200

    response_json = json.loads(response.text)

    # Get the auth token from this api response
    token = response_json['access_token']
    #print("token : " + token)
    print("Auth Token from Login API : " + token)
    print("-------------")

    # # write this token to config file for further use
    # config.set("LOOKER","token",token)
    # with open('../properties.ini', 'w') as configfile:
    #     config.write(configfile)

    return token
#=====================================================================================================#

########################### Looker API for getting Query Id By Slug Id ##############################
def getQueryIdForQuerySlug(slug_id,token,base_url):
    # https://looker.gcodatalab.net:19999/api/3.0/queries/slug/2dQaW5G2OgPVIzppgKgZ5H
    # API Endpoint - /api/3.0/queries/slug/{slug_id}
    apiUrl = base_url + "/api/3.0/queries/slug/" + slug_id
    headers = {
        "cache-control": "no-cache",
        "content-type" : "application/json",
        "Authorization": "token " + token
    }
    print("Looker Url for getting Query Id from Slug Id: " + apiUrl)
    response = requests.request("GET", apiUrl, headers=headers)

    response_json = stringToJson(response.text)
    query_id = str(response_json['id'])
    print ("Looker Query Id : " + query_id)
    return query_id
#=====================================================================================================#

########################### Looker API hit for getting Results for a Query ############################
def getQueryResultsForQueryId(query_id,token,base_url):
    # https://looker.gcodatalab.net/explore/action/action_summary?qid=2dQaW5G2OgPVIzppgKgZ5H   #query_id = '5707'
    # API - /api/3.0/queries/{query_id}/run/{result_format}

    apiUrl = base_url + "/api/3.0/queries/" + query_id + "/run/json"
    headers = {
        "cache-control": "no-cache",
        "content-type": "application/json",
        "Authorization": "token " + token
    }

    response = requests.request("GET", apiUrl, headers=headers)

    print("Looker Url for fetching Query Results: " + apiUrl)
    response_json = stringToJson(response.text)
    print("Looker Query Result : " + response.text)
    print("-------------")

    return response_json
#=====================================================================================================#

########################### Converts String to Json ##################################################
def stringToJson(text):
    return json.loads(text)
#=====================================================================================================#

########################### Order Json items for comparing to another similar json ####################
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
#=====================================================================================================#

########################### Snowflake Connect ####################
def snowflake_connect():
    conn = snowflake.connector.connect(
    account=account,
    user=user,
    password=password
    )
    cur = conn.cursor()
    print("Successfully connected to Snowflake")
    print("-------------")
    return cur
#=====================================================================================================#

########################### Convert Snowflake DB results to Json ####################
def dbToJson(cur, columns):
    rs_snowflake = []
    for row in cur.fetchall():
        rs_snowflake.append(dict(zip(columns, row)))
    rs_snowflake = (json.dumps(rs_snowflake))

    # Converting the DB Query Results to Json Format
    rs_snowflake_json = stringToJson(rs_snowflake)

    return rs_snowflake_json
#=====================================================================================================#

########################### Get Query Results from Slug ####################
def getQueryResults(url_id, token):
    result_looker = getQueryResultsForQueryId(getQueryIdForQuerySlug(url_id,token,base_url), token,base_url)
    return result_looker
#=====================================================================================================#

########################### Convert Dataframe to Json String ####################
def dfToJson(dataframe):
    result = dataframe.toJSON().map(lambda j: json.loads(j)).collect()
    return result
#=====================================================================================================#


if __name__ == "__main__":
    getQueryResultsForQueryId(getQueryIdForQuerySlug("h0MHjHIiFGnbDEGXUVcfs4"))
