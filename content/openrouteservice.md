# Openrouteservice aufsetzen

## 1. Basisumgebung einrichten

### Anforderungen

- Docker
- curl
- Linux oder macOS

### Arbeitsumgebung einrichten

Wir bereiten nun die Umgebung für den erfolgreichen Start eines Openrouteservice-Containers vor.

Zunächst erstellen wir uns einen neuen Scratch-Ordner:

```bash
mkdir -p fossgis_workshop
cd fossgis_workshop
```

Danach erstellen wir einen weiteren Ordner für die Openrouteservice-Dateien:

```bash
mkdir -p ors-docker/files
```

### PBF-Datei herunterladen

Für diese Anleitung werden wir mit zwei PBF-Dateien arbeiten: Münster und Detmold. Es können jederzeit andere PBF-Dateien von Geofabrik heruntergeladen werden: <https://download.geofabrik.de>

```bash
# Münster PBF-Datei herunterladen
curl -C https://download.geofabrik.de/europe/germany/nordrhein-westfalen/muenster-regbez-latest.osm.pbf -o ors-docker/files/muenster-regbez-latest.osm.pbf
# Detmold PBF-Datei herunterladen
curl -C https://download.geofabrik.de/europe/germany/nordrhein-westfalen/detmold-regbez-latest.osm.pbf -o ors-docker/files/detmold-regbez-latest.osm.pbf
```

- The `-C` option allows you to resume a download, if it was interrupted.
- The `-o` option allows you to specify the output file name.

## 2. Openrouteservice-Container mit Basis-Konfiguration und Münster PBF-Datei starten

Anschließend erstellen wir eine Basis-Konfigurationsdatei für Openrouteservice.
Konfigurationsparameter können der [Dokumentation](https://giscience.github.io/openrouteservice/run-instance/configuration/) entnommen werden.

```bash
echo "ors.engine.profile_default.build.source_file=/home/ors/files/muenster-regbez-latest.osm.pbf" > ors_car_muenster.env
echo "ors.engine.profiles.driving-car.enabled=true" >> ors_car_muenster.env
```

- Das erste `echo`-Kommando erstellt eine Datei `ors_car_muenster.env` und setzt den Pfad zur PBF-Datei für das Profil `driving-car`.
- `ors.engine.profile_default.build.source_file` gibt den Pfad zur PBF-Datei an, die für die Berechnung der Routen verwendet wird.
- `ors.engine.profiles.driving-car.enabled` aktiviert das Profil für Autofahrer.

Mit dem folgenden Befehl wird ein Openrouteservice-Container gestartet, der auf Port 8080 erreichbar ist und die PBF-Datei aus dem aktuellen Verzeichnis verwendet.

```bash
# Alten Container entfernen
docker rm -f ors-app || true
# Neuen Container starten
docker run -d \
  --name ors-app \
  -u $(id -u):$(id -g) \
  -p 8080:8082 \
  -v ./ors-docker:/home/ors \
  -e CONTAINER_LOG_LEVEL=INFO \
  -e REBUILD_GRAPHS=true \
  -e XMS=1g \
  -e XMX=2g \
  --env-file ors_car_muenster.env \
  openrouteservice/openrouteservice:latest

# Logs überwachen
docker logs -ft ors-app
```

Nachdem der Container gestartet wurde, kann die API unter `http://localhost:8080/ors` erreicht werden.
Wir testen nun, ob der `health`-Endpunkt erreichbar ist und den erfolgreichen Start des Containers bestätigt.

```bash
curl http://localhost:8080/ors/v2/health
```

Eine erfolgreiche Antwort sollte wie folgt aussehen:

```json
{"status":"ready"}
```

Wir überprüfen nun ebenfalls die verfügbaren Profile:

```bash
curl http://localhost:8080/ors/v2/status
```

Eine erfolgreiche Antwort sollte diverse Informationen über die konfigurierte Instanz enthalten, darunter auch die verfügbaren Profile:

```json
"profiles": {
    "driving-car": {
      "storages": {},
      "encoder_name": "driving-car",
      "encoded_values": [],
      "graph_build_date": "2025-03-19T17:10:29Z",
      "osm_date": "2025-03-18T21:21:15Z",
      "limits": {
        "maximum_distance": 100000,
        "maximum_waypoints": 50,
        "maximum_distance_dynamic_weights": 100000,
        "maximum_distance_avoid_areas": 100000
      }
    }
  }
```

## 3. Openrouteservice-Container mit zwei Profilen und Münster PBF-Datei starten

Nun erstellen wir eine Konfigurationsdatei, die zwei Profile aktiviert: `driving-car` und `cycling-regular`.

```bash
echo "ors.engine.profile_default.build.source_file=/home/ors/files/muenster-regbez-latest.osm.pbf" > ors_car_cycling_muenster.env
echo "ors.engine.profiles.driving-car.enabled=true" >> ors_car_cycling_muenster.env
echo "ors.engine.profiles.cycling-regular.enabled=true" >> ors_car_cycling_muenster.env
```

- Das erste `echo`-Kommando erstellt eine Datei `ors_car_cycling_muenster.env` und setzt den Pfad zur PBF-Datei für die Profile `driving-car` und `cycling-regular`.
- `ors.engine.profile_default.build.source_file` gibt den Pfad zur PBF-Datei an, die für die Berechnung der Routen verwendet wird.
- `ors.engine.profiles.driving-car.enabled` aktiviert das Profil für Autofahrer.
- `ors.engine.profiles.cycling-regular.enabled` aktiviert das Profil für Radfahrer.

Mit dem folgenden Befehl wird ein Openrouteservice-Container gestartet, der auf Port 8081 erreichbar ist und die PBF-Datei aus dem aktuellen Verzeichnis verwendet.

```bash
# Alten Container entfernen
docker rm -f ors-app || true
# Neuen Container starten
docker run -d \
  --name ors-app \
  -u $(id -u):$(id -g) \
  -p 8080:8082 \
  -v ./ors-docker:/home/ors \
  -e CONTAINER_LOG_LEVEL=INFO \
  -e XMS=1g \
  -e XMX=2g \
  -e REBUILD_GRAPHS=true \
  --env-file ors_car_cycling_muenster.env \
  openrouteservice/openrouteservice:latest
# Logs überwachen
docker logs -ft ors-app
```

Nachdem der Container gestartet wurde, kann die API unter `http://localhost:8080/ors` erreicht werden.
Wir testen jetzt, ob der `health`-Endpunkt erreichbar ist und den erfolgreichen Start des Containers bestätigt.

```bash
curl http://localhost:8080/ors/v2/health
```

Eine erfolgreiche Antwort sollte wie folgt aussehen:

```json
{"status":"ready"}
```

Wir überprüfen nun ebenfalls die verfügbaren Profile:

```bash
curl http://localhost:8080/ors/v2/status
```

Eine erfolgreiche Antwort sollte diverse Informationen über die konfigurierte Instanz enthalten, darunter auch die verfügbaren Profile:

```json
"profiles": {
    "driving-car": {
      "storages": {},
      "encoder_name": "driving-car",
      "encoded_values": [],
      "graph_build_date": "2025-03-19T17:10:29Z",
      "osm_date": "2025-03-18T21:21:15Z",
      "limits": {
        "maximum_distance": 100000,
        "maximum_waypoints": 50,
        "maximum_distance_dynamic_weights": 100000,
        "maximum_distance_avoid_areas": 100000
      }
    },
    "cycling-regular": {
      "storages": { },
      "encoder_name": "cycling-regular",
      "encoded_values": [ ],
      "graph_build_date": "2025-03-19T17:11:10Z",
      "osm_date": "2025-03-18T21:21:15Z",
      "limits": {
        "maximum_distance": 100000,
        "maximum_waypoints": 50,
        "maximum_distance_dynamic_weights": 100000,
        "maximum_distance_avoid_areas": 100000
      }
    }
  }
```

## 4. Openrouteservice-Container mit zwei Profilen und unterschiedlichen PBF-Dateien starten

Nun erstellen wir eine Konfigurationsdatei, die zwei Profile aktiviert: `driving-car` und `cycling-regular` und unterschiedliche PBF-Dateien verwendet.

```bash
echo "ors.engine.profile_default.build.source_file=/home/ors/files/muenster-regbez-latest.osm.pbf" > ors_car_cycling_muenster_detmold.env
echo "ors.engine.profiles.driving-car.enabled=true" >> ors_car_cycling_muenster_detmold.env
echo "ors.engine.profiles.cycling-regular.enabled=true" >> ors_car_cycling_muenster_detmold.env
echo "ors.engine.profiles.cycling-regular.build.source_file=/home/ors/files/detmold-regbez-latest.osm.pbf" >> ors_car_cycling_muenster_detmold.env
```

- Das erste `echo`-Kommando erstellt eine Datei `ors_car_cycling_muenster.env` und setzt den Pfad zur PBF-Datei für die Profile `driving-car` und `cycling-regular`.
- `ors.engine.profile_default.build.source_file` gibt den Pfad zur PBF-Datei an, die für die Berechnung der Routen verwendet wird.
- `ors.engine.profiles.driving-car.enabled` aktiviert das Profil für Autofahrer.
- `ors.engine.profiles.cycling-regular.enabled` aktiviert das Profil für Radfahrer.
- `ors.engine.profiles.cycling-regular.build.source_file` gibt den Pfad zur PBF-Datei an, die für die Berechnung der Routen für das Profil `cycling-regular` verwendet wird.

Wichtig zu beachten ist, das erste Profil übernimmt die Standard-PBF-Datei, die für alle Profile verwendet wird und über `ors.engine.profile_default.build.source_file` definiert wird.
Das `cyclin-regular`-Profil verwendet eine eigene PBF-Datei, die über `ors.engine.profiles.cycling-regular.build.source_file` definiert wird. Diese überschreibt die `profile_default`-Konfiguration.

Mit dem folgenden Befehl wird ein Openrouteservice-Container gestartet, der auf Port 8081 erreichbar ist und die PBF-Datei aus dem aktuellen Verzeichnis verwendet.

```bash
# Alten Container entfernen
docker rm -f ors-app || true
# Neuen Container starten
docker run -d \
  --name ors-app \
  -u $(id -u):$(id -g) \
  -p 8080:8082 \
  -v ./ors-docker:/home/ors \
  -e CONTAINER_LOG_LEVEL=INFO \
  -e XMS=1g \
  -e XMX=2g \
  -e REBUILD_GRAPHS=true \
  --env-file ors_car_cycling_muenster_detmold.env \
  openrouteservice/openrouteservice:latest
# Logs überwachen
docker logs -ft ors-app
```

Die Überprüfung der Profile und des `health`-Endpunkts erfolgt analog zu den vorherigen Schritten.

## 5. Openrouteservice-Container mit historischen PBF-Dateien starten

Grober Plan:

1. ~~Set-up ors instance with different pbf files~~
2. New config capabilities :)
3. "historic" routing: use old geofabrik pbf instances

<!-- Some of this content might go into ors docs -->
