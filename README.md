# OSM Transform Workshop für FOSSGIS 2025
jupyter book accompanying the osm-transform workshop held at FOSSGIS 2025

## Installation 

1. Create a new python environment. 

   ```
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install required packages 
   
   ```
   pip install jupyter-book ghp-import
   ```
g
## How to build and deploy

#### 1. Build html files

After making changes to the files, the jupyter book needs to be rebuild. From the repo's root directory, execute 

`jupyter-book build . --all`

#### 2. Deploy to GitHub Pages 

To deploy the current build, execute this from the repo's root directory 

`ghp-import -n -p -f -o _build/html`
