import requests

request = requests.get("http://i.imgur.com/a/Tm1s6.gif")
with open("no_image_response.jpg", 'w+') as f:
    f.write(request.content)

