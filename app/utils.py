import os
import uuid
import requests
from config import settings
from log import Log

class Utils():
    @staticmethod
    def download_image(url: str, folder: str = settings.IMAGE_PATH) -> str:
        if not os.path.exists(folder):
            os.makedirs(folder)
        fileName: str = str(uuid.uuid4()) + "." + url.split('.')[-1]
        localFile: str = os.path.join(folder, fileName)
        with requests.get(url, stream=True) as response:
            if response.status_code == 200:
                with open(localFile, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                Log.L(Log.E, "Failed to download image from {}", url)
        return localFile

    @staticmethod
    def delete_file(path: str) -> None: 
        try:
            os.remove(path=path)
        except Exception as e:
            Log.L(Log.E, 'Error deleting file {}', e)