from django.db import models

class Newsletter(models.Model):
    email = models.EmailField('Email address', unique=True, null=False, blank=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
