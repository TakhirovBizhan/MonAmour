import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, blank=True)
    ROLE_CHOICES = [
        ('buyer', 'Покупатель'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    # дата регистрации уже включена в AbstractUser (date_joined)

    def __str__(self):
        return self.username