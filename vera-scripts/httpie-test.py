import sys
import os
import requests
import json
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC

# below is for Veracode US Commercial region. For logins in other region uncomment one of the other lines
api_base = "https://api.veracode.com/was/configservice/v1" # for logins in the Veracode US Commercial Region
#api_base = "https://api.veracode.eu" # for logins in the Veracode European Region
#api_base = "https://api.veracode.us" # for logins in the Veracode US Federal Region


#Setup variables according to environment
base_url = "http://verademoapi.aszaryk.vuln.sa.veracode.io:8000"
spec_name = "Verademo API Specification " + os.getenv("JOB_ID")

#GitLab:
#analysis_name = os.getenv("CI_PROJECT_NAME") #Dynamic Job name will be same as GitLab project name

#GitHub:
analysis_name = "Project: " + os.environ.get("REPO_NAME") + " - Workflow Number: " + os.environ.get("JOB_ID") #Dynamic Job name will inherit name from GitHub repository values

headers = {"User-Agent": "Python HMAC Example"}
query_params = "custom_base_url=" + base_url + "&spec_name=" + spec_name
spec_file = {'file': open('public/postman_collection.json','rb')}
dynamic_analysis_config = "vera-scripts/dynamic-scan.json"
api_spec_token = os.getenv("API_SPEC_TOKEN")

if __name__ == "__main__":

    try:
        response = requests.post(api_base + "/api_specifications", auth=RequestsAuthPluginVeracodeHMAC(), headers=headers, files=spec_file, params=query_params)
    except requests.RequestException as e:
        print("Whoops!")
        print(e)
        sys.exit(1)

    if response.ok:
        data = response.json()
        print (data["spec_id"])
        spec_id = data["spec_id"]

        try:
            with open(dynamic_analysis_config, 'r') as f:
                json_data = json.load(f)
                print (json_data)
                json_data['name'] = analysis_name
                json_data['scans'][0]['scan_config_request']['target_url']['url'] = base_url
                json_data['scans'][0]['scan_config_request']['api_scan_setting']['spec_id'] = spec_id
                json_data['scans'][0]['scan_config_request']['auth_configuration']['authentications']['HEADER']['headers'][0]['value'] = 'Token ' + api_spec_token

            with open(dynamic_analysis_config, 'w') as f:
                json.dump(json_data, f, indent=2)
                print (json_data)
        except requests.RequestException as e:
            print("Whoops!")
            print(e)
            sys.exit(1)




        #for app in data["_embedded"]["applications"]:
        #    print(app["profile"]["name"])
    else:
        print(response.status_code)
        print(response.text)