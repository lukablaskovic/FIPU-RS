# models.py

from pydantic import BaseModel

class Vrijeme(BaseModel):
  mjesto : str
  temperatura_min : int
  temperatura_max : int
  vjetar: int