from django import template

register = template.Library()


@register.filter
def username_list(users):
    """
    :param users: list of django User entities
    :return: a comma seperated list of crsid's
    """
    return ",".join([user.username for user in users])


@register.filter
def display_user(user):
    """
    :param user: django User
    :return: a rendering of the user's name sand crsid
    """
    return "%s (%s)" % (user.get_full_name(), user.username)


@register.filter
def unique_entity_id(entity):
    """
    :param entity: django model
    :return: unique token combining the model type and id for use in HTML
    """
    return "%s-%s" % (type(entity).__name__, entity.id)
