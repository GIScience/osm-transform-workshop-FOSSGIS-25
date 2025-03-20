---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Den nächsten POI finden

Aus Nutzer-Perspektive ist das ein ganz klassisches Problem:

> Wo ist die nächste Eisdiele?
> Wo ist das nächste Klo?
> Wo ist die nächste Bahn-Haltestelle?

Aus einem geoinformatischen Blickwinkel stellt sich das ganze etwas komplizierter dar.
Zunächst wollen wir die Frage in der Sprache der Geoinformatik formulieren:

> Gegeben eine Koordinate und eine Menge an POIs einer bestimmten Kategorie, welcher ist fußläufig der nächste?

Die Koordinate ist unser Standort, und die POIs einer bestimmten Kategorie kann uns der `openpoiservice` liefern.
Dieser wird allerdings einen Bereich um unseren Standort benötigen, um uns alle POIs, die in diesem Bereich liegen, geben zu können.

Angenommen dass wir maximal einen Kilometer, also ca. 15 Minuten, laufen
wollen, können wir diesen Bereich einfach mit einem Kreis mit passendem Radius approximieren.

Wir können aber auch zunächst den _tatsächlich_ erreichbaren Bereich mithilfe des `openrouteservice` bestimmen:


0. Get isochrone for "in X radius"

```{code-cell} ipython3
:tags: [mytag]

import folium
import requests

# openrouteservice uses [lon, lat]
startpoint = [7.612823,51.96363]

body = {"locations":[startpoint],"range":[900]}

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf6248e2553546494b4efba514744ff48c2e59',
    'Content-Type': 'application/json; charset=utf-8'
}
isochrone_request = requests.post('https://api.openrouteservice.org/v2/isochrones/foot-walking', json=body, headers=headers)

print(isochrone_request.status_code, isochrone_request.reason)
print(isochrone_request.text)

# folium uses [lat, lon]
startpoint.reverse()
m = folium.Map(startpoint, zoom_start=14)

folium.GeoJson(isochrone_request.json()).add_to(m)

m

```

Innerhalb dieses Bereichs können nun POIs der gewünschten Kategorie gesucht werden:

```{code-cell} ipython3


import requests
geojson = isochrone_request.json()

body = {"request":"pois","geometry":{"bbox":[[8.8034,53.0756],[8.7834,53.0456]],"geojson":isochrone_request.json(),"buffer":200},"filters":{"category_ids":[568]},"sortby":"category"}

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf6248e2553546494b4efba514744ff48c2e59',
    'Content-Type': 'application/json; charset=utf-8'
}
call = requests.post('https://api.openrouteservice.org/pois', json=body, headers=headers)

print(call.status_code, call.reason)
print(call.text)

folium.GeoJson(call.json()).add_to(m)

m
```

1. POI query from given position with corresponding radius
2. matrix query for found POIs
3. route generation for nearest POI(s)

## A section

And some more Markdown...
<!-- This might become a blogpost -->
