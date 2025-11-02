from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Super Admin'
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER
    )

    def can_manage_articles(self):
        return self.role in [self.Roles.ADMIN, self.Roles.SUPERADMIN]

    def can_assign_admins(self):
        return self.role == self.Roles.SUPERADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"
