import requests

DEFAULT_TRIES = 4

def download_image(url: str) -> bytes:
    return _download_image(url, DEFAULT_TRIES)

def _download_image(url: str, tries: int):
    try:
        with requests.get(url, stream=True, timeout=2) as res:
            return res.content
    except Exception as e:
        #print("---", tries, url, e)
        if tries:
            return _download_image(url, tries-1)
        raise e
