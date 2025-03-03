from app.service.base import BaseService
from .models import Server

class ServerService(BaseService):
    model = Server