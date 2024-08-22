import requests
import json
from datetime import datetime, timedelta, timezone

########################
#Add squadcast user API token
user_token="b4a2de906b0c2c69e88bcc4f56add43685f7eeccf13bab79bdc324499403137ad3c1b450044856628814fed6688da2b77fe285ec32c22fd7852f78674a5d39a3"
payload = {}

#add the ID of the team from Squadcast from which the incidents are being exported
team_id = "612cdcf97115ff9a44a10357"

#global variable to store the incident ids of all the relevant alerts.
incident_id =[]
#######################

def get_auth_token():
  url = "https://auth.squadcast.com/oauth/access-token"
  response = requests.request("GET", url, headers = {"X-Refresh-Token": str(user_token)}, data=payload)
  res = response.json()
  return res

token = get_auth_token()
bearer_token = token["data"]["access_token"]
#print(bearer_token_get)

def format_time(dt):
 # Format the time without milliseconds
    time_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
# Add milliseconds and 'Z' suffix
    time_str += f".{dt.microsecond // 1000:03d}Z"
    return time_str

#export incidents from current time to 4 weeks before.
def export_incident():
   current_time = datetime.now()
   one_week_time = current_time - timedelta(weeks=4)
   formatted_current = format_time(current_time)
   formatted_week = format_time(one_week_time)
   url = "https://api.squadcast.com/v3/incidents/export/?start_time="+formatted_week +"&end_time="+ formatted_current +"&type=json&owner_id=" + team_id
   response = requests.request("GET", url, headers = {'Authorization': "Bearer "+str(bearer_token)}, data=payload)
   res = response.json()
   return res

#bulk resolve incidents that follow the criteria
def resolve_incident():
  payload = { "incident_ids": incident_id}
  url = "https://api.squadcast.com/v3/incidents/resolve"
  response = requests.request("POST", url, headers = {'Authorization': "Bearer "+str(bearer_token)}, json=payload)
  res = response.json()
  print(res)
  return res

#assign values all the incidents to incidents variable.
incidents = export_incident()

#
for x in incidents["incidents"]:
   if x["status"] == "triggered" or x["status"] == "acknowledged":
    created_at = datetime.fromisoformat(x["created_at"].replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - created_at
    if time_diff.total_seconds() > 24 *3600: #checks if the total seconds elapsed is more than 24 *3600 (24 hours)
       incident_id.append(x["id"]) #appends the relevant incident Ids to the global variable of incident ids

resolve_incident()
