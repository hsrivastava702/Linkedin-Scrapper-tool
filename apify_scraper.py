import requests
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def run_apify_actor(actor_id, token, input_data):
    try:
        # Correctly handle actor ID (split by '/' if it's in the format 'username/actor_name')
        if "/" in actor_id:
            username, actor_name = actor_id.split("/")
        else:
            raise ValueError("Invalid actor ID format. Expected 'username/actor_name'.")

        # Construct run URL
        run_url = f"https://api.apify.com/v2/acts/{username}~{actor_name}/runs?token={token}"
        headers = {"Content-Type": "application/json"}

        # Start actor
        logging.info(f"Starting actor: {actor_id}")
        response = requests.post(run_url, json=input_data, headers=headers)
        response.raise_for_status()
        run_id = response.json()["data"]["id"]

        # Check run status
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
        dataset_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={token}&clean=true&format=json"

        for _ in range(30):  # Retry for up to 30 attempts
            logging.info(f"Checking status for run ID {run_id}...")
            status = requests.get(status_url).json()

            if "data" not in status or "status" not in status["data"]:
                raise ValueError(f"Invalid response structure: {status}")

            if status["data"]["status"] == "SUCCEEDED":
                data = requests.get(dataset_url)
                return data.json()
            elif status["data"]["status"] == "FAILED":
                raise Exception("Apify run failed.")
            
            logging.info("Status not ready, retrying...")
            time.sleep(5)

        raise TimeoutError("Apify actor run timed out.")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        raise
    except ValueError as e:
        logging.error(f"Value error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error: {e}")
        raise

# Updated to use 'curious_coder/linkedin-post-search-scraper'
def scrape_linkedin_post(url, token, cookies):
    actor_id = "curious_coder/linkedin-post-search-scraper"
    input_data = {
        "postUrls": [url],
        "cookies": cookies
    }
    return run_apify_actor(actor_id, token, input_data)

# You can keep using this one or replace it with another actor if needed
def scrape_linkedin_profile(url, token, cookies):
    actor_id = "curious_coder/linkedin-post-search-scraper"
    input_data = {
        "startUrls": [{"url": url}],
        "cookies": cookies
    }
    return run_apify_actor(actor_id, token, input_data)
