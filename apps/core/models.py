from django.db import models

class BaseCsvFileModel(models.Model):
    def get_storage_folder():
        raise NotImplementedError

    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to=get_storage_folder())
    class Meta:
        abstract= True
