import folium
import requests
import json
import geojson

# openrouteservice uses [lon, lat]
startpoint = [7.612823,51.96363]

body = {"locations":[startpoint],"range":[900]}

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf6248e2553546494b4efba514744ff48c2e59',
    'Content-Type': 'application/json; charset=utf-8'
}
isochrone_request = requests.post('https://api.openrouteservice.org/v2/isochrones/foot-walking', json=body, headers=headers)

#print(isochrone_request.status_code, isochrone_request.reason)
#print(isochrone_request.text)


geojson_from_request = isochrone_request.json()
area = geojson_from_request["features"][0]
##area = geojson_from_request
geojson_string = json.dumps(area)
print("--- GeoJSON string from json.dumps ---")
print(geojson_string)
#g = geojson.loads(area)
g = geojson.loads(geojson_string)
print(type(g))
print(type(dict(g)))

body = {"request":"pois","geometry":{"geojson":dict(g),"buffer":200},"filters":{"category_ids":[568]},"sortby":"category"}
print("--- Geojson from body ---")
print(body['geometry']['geojson'])

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf6248e2553546494b4efba514744ff48c2e59',
    'Content-Type': 'application/json; charset=utf-8'
}
call = requests.post('https://api.openrouteservice.org/pois', json=body, headers=headers)
print("--- Response ---")
print(call.status_code, call.reason)
print(call.text)


body = {"request":"pois","geometry":{"geojson":{"type":"Point","coordinates":[8.8034,53.0756]},"buffer":200},"filters":{"category_ids":[568]},"sortby":"category"}

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf6248e2553546494b4efba514744ff48c2e59',
    'Content-Type': 'application/json; charset=utf-8'
}
call = requests.post('https://api.openrouteservice.org/pois', json=body, headers=headers)

print("--- Response 2 ---")
print(call.status_code, call.reason)
print(call.text)
