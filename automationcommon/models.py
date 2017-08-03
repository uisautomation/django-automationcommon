from django.contrib.auth.models import User
from django.db import models


class Creatable(models.Model):
    """
    An abstract Model encapsulating an entity that can be created
    """

    # creator of the entity
    creator = models.ForeignKey(User, related_name="+")
    # when the entity was created
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
