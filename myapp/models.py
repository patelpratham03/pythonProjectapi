from django.db import models

# Create your models here.
class FavoriteRecipe(models.Model):
    recipe_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    image = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
