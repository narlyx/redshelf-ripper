# Imports
import sys
import time
import os
import requests
from config import Config
from downloader import Downloader

# Main function
def main():
    config = Config()

    save_dir = "pages/{}".format(config.book_id)
    os.makedirs(save_dir, exist_ok=True)

    downloader = Downloader(config.book_id, {"csrftoken": config.csrftoken, "session_id": config.session_id}, save_dir) 

    page_index = 0
    while True:
        page_index += 1
        downloader.download_page(page_index)
    
    print("Finished downloading pages!")


# Entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught! Exiting gracefully.")
        sys.exit(0)
