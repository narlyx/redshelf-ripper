# Imports
import sys
import time
import os
import requests
from config import Config

# Loading configuration
config = Config()

save_dir = "pages/"+config.book_id
os.makedirs(save_dir, exist_ok=True)

# Main function
def main():
    # Downloading each page
    for i in range(config.total_pages):
        # Function to download and save a page
        def download_page(page_number: int, strikes=0):
            # Cache
            path = "{}/{}.html".format(save_dir, page_number)

            # Checking if the page already is downloaded
            if os.path.exists(path):
                print("Page {} already downloaded, skipping...".format(page_number))
                return

            # Building request
            url = "https://platform.virdocs.com/spine/{}/{}".format(config.book_id, page_number)
            cookies = {
                    "csrftoken": config.csrftoken,
                    "session_id": config.session_id
                    }

            # Fetching page
            response = requests.get(url, allow_redirects=True, cookies=cookies)

            # Status codes
            if response.status_code == 200:
                # Saving page
                with open(path, "wb") as page:
                    page.write(response.content)
                    print("Page {} downloaded sucessfully...".format(page_number))
            else:
                # Error
                if strikes >= 3:
                    print("Failed to download page after 3 attempts, skipping...")
                else:
                    print("Error: code "+str(response.status_code)+", retrying in 5 seconds...")
                    time.sleep(5)
                    download_page(page_number, strikes=strikes+1)

        # Downloading each page
        download_page(i+1)
    print("Finished downloading pages!")


# Entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught! Exiting gracefully.")
        sys.exit(0)
