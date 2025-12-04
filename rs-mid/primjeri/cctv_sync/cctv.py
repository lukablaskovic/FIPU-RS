from aiohttp import web
import uuid
app = web.Application()

class CCTV_frame:
  def __init__(self, frame_id, location_x, location_y, frame_rate, camera_status, zoom_level, ip_address):
    self.frame_id = frame_id
    self.location_x = location_x
    self.location_y = location_y
    self.frame_rate = frame_rate
    self.camera_status = camera_status
    self.zoom_level = zoom_level
    self.ip_address = ip_address
    
  def update_location(self, x, y):
    self.location_x = x
    self.location_y = y
  
  def info(self):
    return(f"Frame_ID: {self.frame_id} "
          f"Location: {self.location_x, self.location_y} "
          f"Frame rate: {self.frame_rate} "
          f"Camera status: {self.camera_status} "
          f"Zoom level: {self.zoom_level} "
          f"IP Address: {self.ip_address} "
          )

async def post_handler(request):
  # request
  request_body = await request.json() # deserijalizacija
  
  podaci = request_body.get("cctv_details")
  
  instance = CCTV_frame(
    uuid.uuid4(),
    podaci["location_x"],
    podaci["location_y"],
    podaci["frame_rate"],
    podaci["camera_status"],
    podaci["zoom_level"],
    podaci["ip_address"]
    )
  message = instance.info()
  
  return web.json_response(message, status= 201)

app.router.add_post("/cctv", post_handler)

web.run_app(app, port=8090)