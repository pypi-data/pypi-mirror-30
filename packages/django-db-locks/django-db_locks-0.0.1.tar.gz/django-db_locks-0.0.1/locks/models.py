from django.db import models


class Lock(models.Model):
    name = models.CharField(blank=True, max_length=100, unique=True)
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    expire = models.BooleanField()
    expiration = models.DateTimeField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at', 'expiration']
        get_latest_by = '-created_at'