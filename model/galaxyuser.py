# from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from vcfmodel import *


class GalaxyUser(GraphObject):
    __primarykey__ = 'email'

    user_key = Property()
    username = Property()
    email = Property()

    owns = RelatedTo("VariantSet", "OWNS_SET")
    has_job = RelatedTo("UserJob", "HAS_JOB")

    def __init__(self, user_key=None, email=None, username=None):
        self.user_key = user_key
        self.email = email
        self.username = username


class UserJob(GraphObject):
    user_key = Property()
    task_id = Property()

    belongs_to_user = RelatedTo("GalaxyUser", "BELONGS_TO_USER")

    def __init__(self, user_key=None, task_id=None):
        self.user_key = user_key
        self.task_id = task_id
