from django.apps import AppConfig

# List of tuples matching a ContentType 'app_label.model' to a callable
# which will take a user object, and return a list of ids of the matched
# ContentType of which the user object is a member.
# [('myapp.modelname', myapp.module.get_role_ids(user_obj=user_obj))]


class PerfieldpermsConfig(AppConfig):
    name = 'perfieldperms'
