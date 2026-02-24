
import requests
import json
import base64
with open("amazon_captcha_blocked.png", "wb") as f:
    f.write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")) # Mock image
with open("amazon_captcha_blocked.png", "rb") as img:
    files = {"image": img}
    headers = {"Authorization": "Bearer MOCKDBL"} # Bypassing JWT is tricky if it is required... wait!

