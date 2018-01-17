import logging
import threading
from distutils.version import StrictVersion

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.forms import model_to_dict
from testfixtures import django

LOGGER = logging.getLogger('automationcommon')

LOCAL_USER_WARNING = """
    Use automationcommon.models.set_local_user() to set the user to be used in the audit trail or 
    automationcommon.middleware.RequestUserMiddleware if you are in the context of a webapp.
"""


class Creatable(models.Model):
    """
    An abstract Model encapsulating an entity that can be created
    """

    # creator of the entity
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete="CASCADE")
    # when the entity was created
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Audit(models.Model):
    """
    A model that defines an audit record for a change to any django model

    Attributes:
        when      when the change was made
        who       who made the change (if null, then the user was anomymous)
        model     the changed model name
        model_pk  the changed model primary key
        field     the changed model's field
        old       the changed field's original value
        new       the changed field's updated value
    """
    when = models.DateTimeField(auto_now=True)

    who = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete="CASCADE") \
        if StrictVersion(django.get_version()) >= StrictVersion('2.0') else \
        models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    model = models.CharField(max_length=64)

    model_pk = models.IntegerField()

    field = models.CharField(max_length=64)

    old = models.CharField(max_length=255, null=True, blank=True)

    new = models.CharField(max_length=255, null=True, blank=True)


# A thread local object used for binding the user currently updating the model to the thread.
# The user's id is stored instead of the object to avoid issues with stale user objects.
# An id of -1 is used to store an anonymous user.
_thread_local = threading.local()


def set_local_user(user):
    """
    Bind's a user to the current thread to be used for the audit trail

    :param user: user model
    """
    # workaround for is_anonymous being an attribute in Django >=1.10
    is_anon = user.is_anonymous() if callable(user.is_anonymous) else user.is_anonymous
    _thread_local.user_id = -1 if is_anon else user.id


def get_local_user():
    """
    :return: The user for the local thread's request
    """
    user_id = _thread_local.user_id if hasattr(_thread_local, 'user_id') else None

    if user_id == None:
        return None
    elif user_id == -1:
        return AnonymousUser()
    else:
        return get_user_model().objects.filter(id=user_id).first()


def clear_local_user():
    """
    Clear's the user from the current thread
    """
    _thread_local.user_id = None


class ModelChangeMixin(object):
    """
    A model mixin that tracks changes to model fields' values and saves an Audit record per changed field
    when the model is saved. Based ModelDiffMixin on here:
    https://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    """
    def __init__(self, *args, **kwargs):
        super(ModelChangeMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        """
        :return: a dict of the model's fields and their current values
        """
        # NOTE: an internal attribute has been used when introspecting the model.
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    @property
    def diffs(self):
        """
        :return: An array of any changed fields. Each item is a sequence: (field_name, (original_value, updated_value))
        """
        d1 = self.__initial
        d2 = self._dict
        return [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]

    def save(self, *args, **kwargs):
        """
        Saves model, created an Audit record per changed field, and resets the initial state.
        """
        creating = self.pk is None
        super(ModelChangeMixin, self).save(*args, **kwargs)
        # Don't audit new records
        if not creating:
            request_user = get_local_user()
            for diff in self.diffs:
                if request_user:
                    # Workaround for is_anonymous becoming an attribute in Django >=1.10.
                    is_anon = request_user.user.is_anonymous() if callable(request_user.is_anonymous) else request_user.is_anonymous
                    Audit.objects.create(
                        who=None if is_anon else request_user,
                        model=self.__class__.__name__,
                        model_pk=self.pk,
                        field=diff[0],
                        old=diff[1][0], new=diff[1][1]
                    )
                else:
                    LOGGER.warning("Don't know who made this change: (model=%s:%s, field=%s, old='%s', new='%s')" % (
                        self.__class__.__name__, self.pk, diff[0], diff[1][0], diff[1][1]
                    ))
                    LOGGER.warning(LOCAL_USER_WARNING)

        self.__initial = self._dict

    def delete(self, *args, **kwargs):
        """
        Created an Audit record per field with 'new' set to None and deletes the model.
        """
        request_user = get_local_user()
        if request_user:
            # Workaround for is_anonymous becoming an attribute in Django >=1.10.
            is_anon = request_user.user.is_anonymous() if callable(request_user.is_anonymous) else request_user.is_anonymous
            for field, value in self.__initial.items():
                if field != 'id' and value:
                    Audit.objects.create(
                        who=None if is_anon else request_user,
                        model=self.__class__.__name__,
                        model_pk=self.pk,
                        field=field, old=value,
                    )
        else:
            LOGGER.warning("Don't know deleted this: (model=%s:%s)" % (self.__class__.__name__, self.pk))
            LOGGER.warning(LOCAL_USER_WARNING)
        super(ModelChangeMixin, self).delete(*args, **kwargs)
