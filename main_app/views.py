import base64
import requests
from django.shortcuts import render
from .forms import ImageUploadForm

# New (using environment variable)
from decouple import config

def image_recognition(request):
    result = None
    api_key = config("API_KEY", default="")  
    api_url = "https://api.ximilar.com/dom_colors/generic/v2/dominantcolor"

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save()

            # Encode the image in Base64
            try:
                with uploaded_image.image.open("rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode()
            except Exception as e:
                result = {"error": f"Failed to encode image: {str(e)}"}
                return render(request, "main_app/recognition.html", {"form": form, "result": result})

            # Prepare the request payload
            data = {
                "records": [
                    {"_base64": base64_image}
                ]
            }

            # Set headers
            headers = {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            }

            # Call the API
            try:
                response = requests.post(api_url, json=data, headers=headers)
                if response.status_code == 200:
                    api_result = response.json()
                    
                    # Extract and format the dominant colors
                    if "records" in api_result:
                        dominant_colors = api_result["records"][0]["_dominant_colors"]
                        result = {
                            "colors": [
                                {"name": name, "hex": hex_value, "rgb": rgb}
                                for name, hex_value, rgb in zip(
                                    dominant_colors["color_names"],
                                    dominant_colors["rgb_hex_colors"],
                                    dominant_colors["rgb_colors"],
                                )
                            ]
                        }
                    else:
                        result = {"error": "No dominant colors found"}
                else:
                    result = {
                        "error": f"API request failed with status code {response.status_code}",
                        "details": response.text,
                    }
            except Exception as e:
                result = {"error": f"Failed to connect to API: {str(e)}"}

    else:
        form = ImageUploadForm()

    return render(request, "main_app/recognition.html", {"form": form, "result": result})
