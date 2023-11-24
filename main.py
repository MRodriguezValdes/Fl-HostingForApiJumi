import requests
from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

url = ("https://services1.arcgis.com/nCKYwcSONQTkPA4K/arcgis/rest/services/AntenasWifiRivasVaciamadrid/FeatureServer/0"
       "/query?outFields=*&where=1%3D1&f=geojson")


def get_antennas_data():
    response = requests.get(url)
    return response.json()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTMLResponse(content=open("templates/home.html").read(), status_code=200)


@app.get("/antennas/get_data", response_class=HTMLResponse)
def get_antenna_data_form(request: Request):
    return templates.TemplateResponse("get_antenna_data.html", {"request": request})


@app.post("/antennas/query", response_class=HTMLResponse)
def query_antenna_by_id(antenna_id: int = Form(...), antennas_data: dict = Depends(get_antennas_data)):
    try:
        if 1 <= antenna_id <= len(antennas_data["features"]):
            return RedirectResponse(url=f"/antennas/{antenna_id}", status_code=303)
        else:
            raise HTTPException(status_code=404, detail="Antenna not found")
    except HTTPException as e:
        if e.status_code == 404:
            return templates.TemplateResponse(
                "antenna_query.html",
                {"request": {"url": f"/antennas/{antenna_id}", "antenna_id": antenna_id}, "antenna_data": None}
            )
        else:
            raise e


@app.get("/antennas", response_class=HTMLResponse)
def read_antennas_list(request: Request, antennas_data: dict = Depends(get_antennas_data)):
    return templates.TemplateResponse("antennas_list.html", {"request": request, "antennas_data": antennas_data})


@app.get("/antennas/total", response_class=HTMLResponse)
def how_many_antennas(request: Request, antennas_data: dict = Depends(get_antennas_data)):
    total_antennas = len(antennas_data["features"])
    return templates.TemplateResponse("antennas.html", {"request": request, "total_antennas": total_antennas})


@app.get("/antennas/{antenna_id}", response_class=HTMLResponse)
def query_antenna(request: Request, antenna_id: int, antennas_data: dict = Depends(get_antennas_data)):
    antenna_list = antennas_data.get("features", [])

    try:
        if 1 <= antenna_id <= len(antenna_list):
            antenna_data = antenna_list[antenna_id - 1]
            return templates.TemplateResponse(
                "antenna_query.html",
                {"request": {"url": str(request.url), "antenna_id": antenna_id}, "antenna_data": antenna_data}
            )
        else:
            raise HTTPException(status_code=404, detail="Antenna not found")
    except HTTPException as e:
        if e.status_code == 404:
            # Captura la excepción HTTPException con el código de estado 404 y devuelve una respuesta HTML personalizada
            return templates.TemplateResponse(
                "antenna_query.html",
                {"request": {"url": str(request.url), "antenna_id": antenna_id}, "antenna_data": None}
            )
        else:
            # Si es una excepción diferente, permite que FastAPI maneje la respuesta automáticamente
            raise e
