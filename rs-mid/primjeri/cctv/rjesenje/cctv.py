import aiohttp
from aiohttp import web
import uuid

class CCTV_frame:
  def __init__(self, frame_id, location_x, location_y, frame_rate, camera_status, zoom_level, ip_address):
      self.frame_id = frame_id
      self.location_x = location_x
      self.location_y = location_y
      self.frame_rate = frame_rate
      self.camera_status = camera_status
      self.zoom_level = zoom_level
      self.ip_address = ip_address
      
  def azuriraj(self, x_novi, y_novi):
    self.location_x = x_novi
    self.location_y = y_novi

  def info(self):
      return (
          f"Frame ID: {self.frame_id}, "
          f"Location: ({self.location_x}, {self.location_y}), "
          f"Frame rate: {self.frame_rate}, "
          f"Camera status: {self.camera_status}, "
          f"Zoom level: {self.zoom_level}x, "
          f"IP address: {self.ip_address}"
      )
  def update_location(self, new_location_x, new_location_y):
      self.location_x = new_location_x
      self.location_y = new_location_y      

app = web.Application()

async def handle_cctv_instance(request):
  print("Zahtjev zaprimljen...")
  data = await request.json()
  details = data.get("cctv_details")
  
  frame_id = uuid.uuid4()
  location_x = details.get("location_x")
  location_y = details.get("location_y")
  frame_rate = details.get("frame_rate")
  camera_status = details.get("camera_status")
  zoom_level = details.get("zoom_level")
  ip_address = details.get("ip_address")
  
  camera = CCTV_frame(frame_id, location_x, location_y, frame_rate, camera_status, zoom_level, ip_address)
  
  return web.json_response({"message": camera.info()})

app.router.add_post('/cctv', handle_cctv_instance)

if __name__ == "__main__":
  web.run_app(app, port=8090)