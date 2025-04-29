from django.db import models

# Create your models here.
class MenuItem(models.Model):
    name: models.CharField(max_length=50)
    description: models.CharField(max_length=200)
    rating: models.FloatField(default=0)
    image: models.ImageField(upload_to="/image")
    price: models.IntegerField()

