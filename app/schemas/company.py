from pydantic import BaseModel


class CompanyRequest(BaseModel):
    url: str