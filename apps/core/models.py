from django.db import models

class BaseModel(models.Model):


    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    class Meta:
        abstract= True
