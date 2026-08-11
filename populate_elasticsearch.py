import requests
import time
import sys
import os
import json
import uuid
import psycopg
from psycopg import OperationalError, DatabaseError
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import random
from dotenv import load_dotenv
import socket



DB_TIMEZONE = datetime.now().astimezone().tzinfo
print(f"Using timezone: {DB_TIMEZONE}")

load_dotenv()
PG_VERSION = os.getenv("POSTGRES_VERSION")
PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD")

########################################################
####### Functions for checking services
########################################################

def is_elasticsearch_ready():
    try:
        socket.getaddrinfo("elasticsearch", None)
        host = "elasticsearch"
    except socket.gaierror:
        # Fallback to local machine if Docker network host isn't found
        host = "localhost"

    try:
        url = f'http://{host}:9200'
        print(url)

        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Elasticsearch service: {e}")
        return False

def is_grafana_ready():
    try:
        socket.getaddrinfo("grafana", None)
        host = "grafana"
    except socket.gaierror:
        # Fallback to local machine if Docker network host isn't found
        host = "localhost"
    try:
        url = f'http://{host}:3000'
        print(url)

        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Grafana service: {e}")
        return False

def is_mage_ready():
    try:
        socket.getaddrinfo("grafana", None)
        host = "grafana"
    except socket.gaierror:
        # Fallback to local machine if Docker network host isn't found
        host = "localhost"

    try:
        url = f'http://{host}:6789'
        print(url)
        
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Mage service: {e}")
        return False

def wait_for_services(max_retries=12):  # 12 * 50 seconds = 10 minute total wait time
    retries = 0
    while retries < max_retries:
        if is_elasticsearch_ready() and is_mage_ready() and is_grafana_ready():
            print("All  Elasticsearch and Mage and Grafana are ready!")
            return True
        else:
            print(f"Attempt {retries + 1}/{max_retries}: Services not ready. Waiting 5 seconds...")
            time.sleep(50)
            retries += 1
    print("Max retries reached. Services are not ready.")
    return False

################################################################
####### Functions for Mage: run_pipeline_populate_elasticsearch
################################################################

def run_pipeline_populate_elasticsearch():
    """
    chunking, lammetizing, embedding and indexing data into elastic search via mage pipeline
    """
    url = "http://127.0.0.1:6789/api/pipeline_schedules/1/pipeline_runs/60ac297fd34a457991914d00c79c6a42"
    
    headers = {
        "Content-Type": "application/json"
    }

    print('!----> populate_elasticsearch for magic started', flush=True)
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        print(f'!----> populate_elasticsearch magic finished with code: {response.status_code}', flush=True)
    except Exception as err:
        print(f"An unexpected error occurred magic: {err}", flush=True)
        print("Error details magic:", sys.exc_info(), flush=True)
    finally:
        print("!----> Script execution completed magic.", flush=True)

###############################################################################################
####### Functions for Grafana: create_api_key, create_or_update_datasource, create_dashboard
##############################################################################################

auth = (GRAFANA_USER, GRAFANA_PASSWORD)
headers = {"Content-Type": "application/json"}

def get_or_create_service_account_token():
    
    #auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    
    account_payload = {
        "name": "ProgrammaticServiceAccount",
        "role": "Admin",  # Options: Viewer, Editor, Admin
        "isDisabled": False
    }

    # Step 1: Attempt to create the Service Account
    sa_url = f"{GRAFANA_URL}/api/serviceaccounts"
    response = requests.post(sa_url, auth=auth, headers=headers, json=account_payload)

    # 201 Created (Success)
    if response.status_code == 201:
        print("Service account created successfully.")
        sa_id = response.json()["id"]
        return create_token(sa_id)

    # 400 Bad Request or 409 Conflict (Account already exists)
    elif response.status_code in [400, 409]:
        print("Service account name already exists. Fetching existing account to recreate...")
        
        # Step 2: Query existing service accounts to find the matching ID
        search_response = requests.get(f"{sa_url}/search", auth=auth)
        if search_response.status_code == 200:
            service_accounts = search_response.json().get("serviceAccounts", [])
            for sa in service_accounts:
                if sa["name"] == account_payload["name"]:
                    sa_id = sa["id"]
                    
                    # Step 3: Delete the outdated service account
                    del_response = requests.delete(f"{sa_url}/{sa_id}", auth=auth)
                    if del_response.status_code == 200:
                        print("Old service account deleted successfully.")
                        # Recurse once to cleanly spin up the fresh account
                        return get_or_create_service_account_token()
                        
        print("Failed to resolve conflicting service account.")
        return None
    else:
        print(f"Failed to communicate with Grafana API: {response.status_code} - {response.text}")
        return None

def create_token(sa_id):
    """Generates a usable bearer token linked to the specific Service Account ID."""
    token_url = f"{GRAFANA_URL}/api/serviceaccounts/{sa_id}/tokens"
    token_payload = {"name": "ProgrammaticToken"}
    
    token_response = requests.post(token_url, auth=auth, headers=headers, json=token_payload)
    if token_response.status_code == 200:
        print("Service account token created successfully.")
        return token_response.json()["key"]  # This string is your valid bearer token
    else:
        print(f"Failed to generate token: {token_response.text}")
        return None

def create_or_update_datasource(access_token):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    datasource_payload = {
        "name": "PostgreSQL",
        "type": "postgres",
        "url": f"{PG_HOST}:{PG_PORT}",
        "access": "proxy",
        "user": PG_USER,
        "database": PG_DB,
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {"sslmode": "disable", "postgresVersion": PG_VERSION},
        "secureJsonData": {"password": PG_PASSWORD},
    }

    print("Datasource payload:")
    print(json.dumps(datasource_payload, indent=2))

    # First, try to get the existing datasource
    response = requests.get(
        f"{GRAFANA_URL}/api/datasources/name/{datasource_payload['name']}",
        headers=headers,
    )

    if response.status_code == 200:
        # Datasource exists, let's update it
        existing_datasource = response.json()
        datasource_uid = existing_datasource["uid"]

        print(f"Updating existing datasource with uid: {datasource_uid}")

        response = requests.put(
            f"{GRAFANA_URL}/api/datasources/uid/{datasource_uid}",
            headers=headers,
            json=datasource_payload,
        )
    else:
        # Datasource doesn't exist, create a new one
        print("Creating new datasource")
        response = requests.post(
            f"{GRAFANA_URL}/api/datasources", headers=headers, json=datasource_payload
        )

    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")

    if response.status_code in [200, 201]:
        print("Datasource created or updated Successfully!!")
        return response.json().get("datasource", {}).get("uid") or response.json().get(
            "uid"
        )
    else:
        print(f"Failed to create or update datasource: {response.text}")
        return None

def create_dashboard(access_token, datasource_uid, dashboard_file):
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    try:
        with open(dashboard_file, "r") as f:
            dashboard_json = json.load(f)
            
    except FileNotFoundError:
        print(f"Error: {dashboard_file} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding {dashboard_file}: {str(e)}")
        return

    print("Dashboard JSON loaded successfully.")

    # Update datasource UID in the dashboard JSON
    panels_updated = 0
    import copy



    NEW_DATASOURCE_NAME = "PostgreSQL"
    NEW_DATASOURCE_UID = datasource_uid

    updated_dashboard = copy.deepcopy(dashboard_json)

    if "elements" in updated_dashboard["spec"]:
        for element_id, element_data in updated_dashboard["spec"]["elements"].items():
            # Drill down into spec -> data -> spec -> queries
            try:
                queries = element_data["spec"]["data"]["spec"]["queries"]
                for query in queries:
                    # Update the target datasource properties
                    if "datasource" in query["spec"]["query"]:
                        # Change the targeting reference name
                        query["spec"]["query"]["datasource"]["name"] = NEW_DATASOURCE_UID
                        query["spec"]["query"]["group"] = NEW_DATASOURCE_NAME

                        panels_updated+=1
                        print(f"{panels_updated}] Updated data source reference for {element_id}")
                        
            except KeyError:
                # Handles any panels/elements that do not have queries (text fields, rows, etc.)
                continue

    print(f"Updated datasource UID for {panels_updated} panels/targets.")
 
    # Prepare the payload
    dashboard_payload = {
        "dashboard": updated_dashboard,
        "overwrite": True
    }

    print("Sending dashboard creation request...")
    print(json.dumps(dashboard_payload, indent=2))

    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db", headers=headers, json=dashboard_payload
    )

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        print("Dashboard created successfully")
        print(f"New Version: {response.json().get('version')}")
        return response.json().get("uid")
    else:
        print(f"Failed to create dashboard: {response.text}")
        return None


if __name__ == "__main__":

    load_dotenv()

    #Check services

    if not wait_for_services():
        print("Exiting script as services are not ready.")
        sys.exit(1)

    # Trigger pipeline in mage.ai

    run_pipeline_populate_elasticsearch()

    # Create Graphana Dashboard
    
    access_token = get_or_create_service_account_token()
    if not access_token:
        print("access_token creation failed")

    datasource_uid = create_or_update_datasource(access_token)
    if not datasource_uid:
        print("Datasource creation failed")

    dashboard_file = "grafana-dashboard.json"
    
    try:
        socket.getaddrinfo("elasticsearch", None)
        #Running in outside of docker container
        dashboard_file = "app/graphana-dashboard.json"
    except socket.gaierror:
        # Fallback to local machine if Docker network host isn't found
        host = "localhost"
        is_localhost = True
        #Running inside of docker container
        dashboard_file = "app/graphana-dashboard.json"

    print(dashboard_file)
    create_dashboard(access_token, datasource_uid, dashboard_file)