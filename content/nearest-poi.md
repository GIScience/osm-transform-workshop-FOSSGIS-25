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

> Wo ist das nächste Café?
> Wo ist das nächste Klo?
> Wo ist die nächste Bahn-Haltestelle?

Aus einem geoinformatischen Blickwinkel stellt sich das ganze etwas komplizierter dar.
Zunächst wollen wir die Frage in der Sprache der Geoinformatik formulieren:

> Gegeben eine Koordinate und eine Menge an POIs einer bestimmten Kategorie, welcher ist fußläufig der nächste?

Die Koordinate ist unser Standort, also `N 51° 57' 49.068 E 007° 36' 46.512"`.  Die POIs einer bestimmten Kategorie, hier _Cafés_ kann uns der `openpoiservice` liefern.
Dieser wird allerdings einen Bereich um unseren Standort benötigen, um uns alle POIs, die in diesem Bereich liegen, geben zu können.

Angenommen dass wir maximal einen Kilometer, also ca. 15 Minuten, laufen
wollen, können wir diesen Bereich einfach mit einem Kreis mit passendem Radius approximieren.

Wir können aber auch zunächst den _tatsächlich_ erreichbaren Bereich mithilfe des `openrouteservice` bestimmen:

Wir beginnen mit ein bisschen notwendigem Setup, das für den Rest des Beispiels gebraucht wird.

```{code-cell} ipython3
:tags: [hide-input]

import folium
import requests

# The key in here is not working anymore.
headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf6248e2553546494b4efba514744ff48c2e59',
    'Content-Type': 'application/json; charset=utf-8'
}
```

Als nächstes kann der `/isochrones`-Endpunkt genutzt werden, um den Bereich zu finden, der fußläufig innerhalb von 15 Minuten (900 Sekunden) von unserem Standort aus erreichbar ist. Wir nutzen `folium`, um das Ergebnis zu visualisieren.


```{code-cell} ipython3
:tags: [mytag]

# openrouteservice uses [lon, lat]
startpoint = [7.61282,51.96363]

body = {"locations":[startpoint],"range":[900]}

# We use the foot-walking profile here.
isochrone_response = requests.post('https://api.openrouteservice.org/v2/isochrones/foot-walking', json=body, headers=headers)
isochrone_geojson = isochrone_response.json()

# folium uses [lat, lon]
startpoint.reverse()
m = folium.Map(startpoint, zoom_start=14)

folium.GeoJson(isochrone_geojson).add_to(m)

m

```

Innerhalb dieses Bereichs können nun POIs der gewünschten Kategorie gesucht werden.
Dafür wird der `/pois`-Endpunkt verwendet. Die entsprechende Kategorie findet sich [in der Backend-Dokumentation des openrouteservice](https://giscience.github.io/openrouteservice/api-reference/endpoints/poi/)

```{code-cell} ipython3

# The POI endpoint needs a "plain" polygon, not a GeoJSON "Feature".
geojson = isochrone_geojson["features"][0]["geometry"]

body = {"request":"pois","geometry":{"geojson":geojson},"filters":{"category_ids":[564]},"sortby":"category"}

poi_response = requests.post('https://api.openrouteservice.org/pois', json=body, headers=headers)
poi_geojson = poi_response.json()

m = folium.Map(startpoint, zoom_start=14)
folium.GeoJson(poi_geojson).add_to(m)

m
```

Als nächstes muss hieraus der nächste POI extrahiert werden. Dafür wird der `/matrix`-Endpunkt genutzt.
Hierbei werden die POI-Koordinaten als `destination`, der Startpunkt als `source` übergeben.
Dadurch ist das Ergebnis einfach verarbeitbar.

```{code-cell} ipython3

pois = []
pois_info = []

for feature in poi_geojson["features"]:
    pois.append(feature["geometry"]["coordinates"])
    pois_info.append(feature)

# The final list of locations will include all POI locations and have the startpoint attached to the end.
destinations = list(range(len(pois)))
sources = [len(pois)]

startpoint.reverse()
pois.append(startpoint)

# now we have the POIs and can make a neat matrix call

body = {"locations": pois, "sources": sources, "destinations": destinations }
print(body)

matrix_response = requests.post('https://api.openrouteservice.org/v2/matrix/foot-walking', json=body, headers=headers)
print(matrix_response.status_code, matrix_response.reason)
print(matrix_response.text)
matrix_json = matrix_response.json()

print(matrix_json)

durations = matrix_json["durations"][0]
nearest_duration = min(durations)
nearest_index = durations.index(nearest_duration)

nearest_poi = pois[nearest_index]
nearest_poi_info = pois_info[nearest_index]
nearest_poi.reverse()

m = folium.Map(startpoint, zoom_start=14)
folium.map.Marker(location=nearest_poi).add_to(m)

m

```

Jetzt kann als letzter Schritt eine Route zum nächsten POI berechnet werden.

```{code-cell} ipython3

body = {"coordinates":[startpoint,nearest_poi]}

directions_response = requests.post('https://api.openrouteservice.org/v2/directions/foot-walking/geojson', json=body, headers=headers)
directions_geojson = directions_response.json()

folium.GeoJson(directions_geojson).add_to(m)
m

```

<!-- This might become a blogpost -->
