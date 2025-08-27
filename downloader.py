import requests
from requests.adapters import HTTPAdapter, Retry
import os
import re
from pathlib import Path
import base64

class Downloader:
    # Internal vars
    book_id: str
    cookies: dict[str, str]
    download_path: str
    session: requests.Session

    # Constructor
    def __init__(self, book_id: str, cookies: dict[str, str], download_path: str):
        # Pulling variables
        self.book_id = book_id
        self.cookies = cookies
        self.download_path = download_path

        # Creating a session
        self.session = requests.Session()
        self.session.mount(
                "https://",
                HTTPAdapter(
                    max_retries=Retry(
                        total=5,
                        backoff_factor=1
                        )
                    )
                )

    # Sends a get request to the url and returns the response
    def __download_resource(self, url: str) -> requests.Response:
        # Downloading
        response = self.session.get(
                url,
                allow_redirects=True,
                cookies=self.cookies
                )

        # Returning
        return response

    # Returns the base url within the page's html
    def __get_base_url(self, html: str) -> str:
        return re.search('<base href="(.*?/(EPUB|OPS|OEBPS)).*"/>', html).group(1)

    # Returns all remote links within the page's html
    def __get_remote_urls(self, html: str) -> list[str]:
        css = re.finditer('<link.*?href="(.*?)"', html)
        imgs = re.finditer('<img.*?src="(.*?)"', html)

        remote = []
        for css in css:
            parsed = css.group(1).replace("..", "")
            if parsed[0] != "/":
                parsed = f"/{parsed}"
            remote.append(parsed)

        for img in imgs:
            parsed = img.group(1).replace("..", "")
            if parsed[0] != "/":
                parsed = f"/{parsed}"
            remote.append(parsed)

        return remote

    # Embed images into html as base64
    def __embed_images_as_base64(self, path: str, html: str) -> str:
        def encode_image(match: re.Match[str]) -> str:
            # Extract the relative path from the src attribute
            relative_path = match.group(1).replace("../", "")
            absolute_path = os.path.join(
                path, relative_path
            )  # Construct the absolute path

            try:
                # Read the image file and encode it as base64
                with open(absolute_path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode("utf-8")
                return f'src="data:image/png;base64,{encoded}"'
            except FileNotFoundError:
                print(f"Image not found: {absolute_path}")
                return match.group(0)  # Keep the original src if the image is not found

        # Replace all src attributes with base64-encoded images
        return re.sub(r'src="(.*?)"', encode_image, html)

    # Main function
    def download_page(self, page_number: int):
        # Status
        print("Downloading page {}... ".format(page_number), end='', flush=True)

        # Path for the page
        page_path = "{}/{}".format(self.download_path, page_number)

        # Checking if the page has already been downloaded
        if os.path.exists("{}/html/index.html".format(page_path, page_number)):
            print("already downloaded, skipping...")
            return

        # Creating directory
        os.makedirs(page_path, exist_ok=True)

        # Downloading base page
        page_response = self.__download_resource("https://platform.virdocs.com/spine/{}/{}".format(self.book_id, page_number))

        # Failed to download
        if page_response.status_code != 200:
            if page_response.status_code == 404:
                print("page does not exist: {}".format(page_response.status_code))
            else:
                print("failed to download page after 5 tries: {}, skipping...".format(page_response.status_code))
            return page_response.status_code

        # Parsing data
        raw = page_response.text
        base_url = self.__get_base_url(raw)
        remote_urls = self.__get_remote_urls(raw)

        # Downloading remote content
        for remote_url in remote_urls:
            # Getting full url
            asset_url: str
            if "/static" in remote_url:
                asset_url = "https://platform.virdocs.com{}".format(remote_url)
            else:
                asset_url = "{}{}".format(base_url, remote_url)

            # Downloading
            asset_response = self.__download_resource(asset_url)

            # Error checking
            if asset_response.status_code == 200:
                # Writing
                asset = Path("{}/{}".format(page_path, remote_url))
                asset.parent.mkdir(parents=True, exist_ok=True)
                asset.write_bytes(asset_response.content)
            else:
                # Failed
                print("failed to download {} after 5 tries: {}, skipping... ".format(remote_url, asset_response.status_code))

        # Creating html file
        page = Path("{}/html/index.html".format(page_path, page_number))
        page.parent.mkdir(parents=True, exist_ok=True)

        # Replacing links/assets
        parsed_raw = re.sub("<base .*?/>", "", raw)
        parsed_raw = re.sub("<script.*?>.*?</script>", "", parsed_raw, flags=re.DOTALL)
        parsed_raw = self.__embed_images_as_base64(page_path, parsed_raw)

        # Writing
        page.write_text(parsed_raw, encoding="UTF-8")

        # Closing session
        print("DONE!")
        self.session.close()
