# Imports
import json
import os
import sys

# Configuration file path
config_path = "config.json"

# Default configuration to populate a new configuration file
default_config = {
        "csrftoken": "",
        "session_id": "",
        "book_id": "",
        "total_pages": 0
        }

class Config:
    # Initializing configuration entries
    csrftoken: str
    session_id: str
    book_id: str
    total_pages: int

    def __init__(self):
        # Creating a new config if there is none found
        if not os.path.exists(config_path):
            with open(config_path, "w") as new_config:
                # Creating a new file
                json.dump(default_config, new_config, indent=4)

                # Exiting
                print("New configuration created at {}, please fill in the fields".format(config_path))
                new_config.close()
                sys.exit(0)

        # Loading configuration
        with open(config_path, "r") as config_file:
            # Loading file
            raw_config = json.load(config_file)

            # Loading variables
            self.csrftoken = raw_config.get("csrftoken")
            self.session_id = raw_config.get("session_id")
            self.book_id = raw_config.get("book_id")
            self.total_pages = raw_config.get("total_pages")

            # Exiting
            config_file.close()

        # Config checks
        if self.csrftoken == "" or self.csrftoken == None:
            print("csrftoken is unset in your configuration, exiting")
            sys.exit(1)
        if self.session_id == "" or self.session_id == None:
            print("session_id is unset in your configuration, exiting")
            sys.exit(1)
        if self.book_id == "" or self.book_id == None:
            print("book_id is unset in your configuration, exiting")
            sys.exit(1)
        if self.total_pages == 0 or self.total_pages == None:
            print("total_pages is unset in your configuration, exiitng")
            sys.exit(1)
