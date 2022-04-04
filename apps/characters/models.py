from django.db import models

from core.models import BaseModel

class CharactersCsvFile(BaseModel):
    file = models.FileField(upload_to="characters")
    class Meta:
        ordering = ['-ctime']

