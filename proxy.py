from onvif import ONVIFCamera
import os

from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse

app = FastAPI()

CAMERA_VISCA_IP = os.environ["CAMERA_VISCA_IP"]
CAMERA_VISCA_PORT = int(os.environ["CAMERA_VISCA_PORT"])
CAMERA_VISCA_USER = os.environ["CAMERA_VISCA_USER"]
CAMERA_VISCA_PASS = os.environ["CAMERA_VISCA_PASS"]
CAMERA_VISCA_PROFILE_TOKEN = os.environ["CAMERA_VISCA_PROFILE_TOKEN"]
CAMERA_DISPLAY_NAME = os.getenv("CAMERA_DISPLAY_NAME", CAMERA_VISCA_IP)


mycam = ONVIFCamera(CAMERA_VISCA_IP, CAMERA_VISCA_PORT, CAMERA_VISCA_USER, CAMERA_VISCA_PASS)

ptz_service = mycam.create_ptz_service()

with open("camdata.html") as f:
    camdata_template = f.read()


@app.get("/cgi-bin/event")
async def read_event(request: Request):
    return status.HTTP_204_NO_CONTENT

# https://eww.pass.panasonic.co.jp/pro-av/support/content/guide/DEF/UE80/AW-UE80UE50UE40_InterfaceSpecification_E.pdf
@app.get("/live/camdata.html", response_class=PlainTextResponse)
async def read_camdata():
    return camdata_template.format(title=CAMERA_DISPLAY_NAME)

@app.get("/cgi-bin/man_session")
async def read_session(request: Request):
    return status.HTTP_204_NO_CONTENT

@app.get("/cgi-bin/aw_ptz")
async def read_aw_ptz(request: Request):
    cmd = request.query_params["cmd"]
    if cmd.startswith("#PTS"):
        pan, tilt = map(int, (cmd[4:6], cmd[6:8]))
        print(pan, tilt)
        # 0 to 100 -> -1 to 1
        x, y = (pan - 50) / 50, (tilt - 50) / 50
        ptz_service.ContinuousMove({'ProfileToken': CAMERA_VISCA_PROFILE_TOKEN, 'Velocity': {'PanTilt': {'x': x, 'y': y}}})
    if cmd.startswith("#Z"):
        zoom = int(cmd[2:4])
        print(zoom)
        # 0 to 100 -> -1 to 1
        z = (zoom-50) / 100
        ptz_service.ContinuousMove({'ProfileToken': CAMERA_VISCA_PROFILE_TOKEN, 'Velocity': {'Zoom': {'x': z}}})
    return status.HTTP_204_NO_CONTENT
