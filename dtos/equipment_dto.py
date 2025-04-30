from pydantic import BaseModel
from models.equipment import PurposeEnum

class EquipmentBase(BaseModel):
    name: str
    img_url: str = "undefined"
    description: str
    detailed_description: str = ""
    purpose: PurposeEnum
    quantity: int = 0

class EquipmentAIRequest(BaseModel):
    name: str
    purpose: PurposeEnum
