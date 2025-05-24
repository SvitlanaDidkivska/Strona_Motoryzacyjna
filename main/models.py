from django.db import models

class Car(models.Model):
    name = models.CharField(max_length=200)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50)
    drive_wheel = models.CharField(max_length=20, choices=[
        ('fwd', 'Front Wheel Drive'),
        ('rwd', 'Rear Wheel Drive'),
        ('4wd', '4 Wheel Drive'),
        ('awd', 'All Wheel Drive'),
    ])
    description = models.TextField()
    image = models.ImageField(upload_to='cars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    class Meta:
        ordering = ['-created_at']
