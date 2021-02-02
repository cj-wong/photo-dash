import json

from photo_dash import image

with open('resources/example.json') as f:
    e = json.load(f)

i = image.DashImage(e['module'], e['title'], e['sections'])
i.create()
