from django.db import models
from main_app.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    rating = models.IntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('-created',)

# Create your models here.
