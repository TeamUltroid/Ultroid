import aiohttp
import zipfile
import os
import logging
from pathlib import Path
import shutil


async def fetch_recent_release():
    """
    Fetch the most recent release from GitHub, download the ultroid-dist.zip,
    and extract it to the webapp directory.
    """
    try:
        # Configuration
        repo = "TeamUltroid/webapp"
        zip_filename = "ultroid-dist.zip"
        webapp_path = Path("resources/webapp")  # Adjust this path as needed

        # Create webapp directory if it doesn't exist
        webapp_path.mkdir(parents=True, exist_ok=True)

        # Temporary file for the download
        temp_zip = Path(f"resources/temp_{zip_filename}")

        # GitHub API endpoint to get the latest release
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"

        logging.info("Fetching latest webapp release...")

        async with aiohttp.ClientSession() as session:
            # Get latest release info
            async with session.get(api_url) as response:
                if response.status != 200:
                    logging.error(
                        f"Failed to fetch release info: HTTP {response.status}"
                    )
                    return False

                data = await response.json()

                # Find the ultroid-dist.zip asset
                asset_url = None
                for asset in data.get("assets", []):
                    if asset["name"] == zip_filename:
                        asset_url = asset["browser_download_url"]
                        break

                if not asset_url:
                    logging.error(
                        f"Could not find {zip_filename} in the latest release"
                    )
                    return False

                # Download the zip file
                logging.info(f"Downloading {zip_filename}...")
                async with session.get(asset_url) as zip_response:
                    if zip_response.status != 200:
                        logging.error(
                            f"Failed to download zip: HTTP {zip_response.status}"
                        )
                        return False

                    with open(temp_zip, "wb") as f:
                        f.write(await zip_response.read())

        # Clear existing webapp files
        logging.info("Clearing existing webapp files...")
        for item in webapp_path.glob("*"):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        # Extract the zip file
        logging.info(f"Extracting {zip_filename} to webapp directory...")
        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall(webapp_path)

        # Clean up the temporary zip file
        temp_zip.unlink()

        logging.info("Webapp successfully updated!")
        return True

    except Exception as e:
        logging.error(f"Error updating webapp: {str(e)}")
        return False
