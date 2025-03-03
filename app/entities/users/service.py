from app.service.base import BaseService
from .models import User

class UserService(BaseService):
    model = User
    