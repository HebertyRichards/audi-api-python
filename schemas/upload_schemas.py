from pydantic import BaseModel, HttpUrl, Field


class FileUploadResponse(BaseModel):
    public_url: HttpUrl = Field(
        ..., description="A URL pública do arquivo que foi enviado."
    )


class Config:
    from_attributes = True
