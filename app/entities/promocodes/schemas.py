from pydantic import BaseModel


class PromocodeScheme(BaseModel):
    code: str
    bonus: float
    count: int
