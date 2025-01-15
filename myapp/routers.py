class UserDataRouter:
    """
    A router to control all database operations on models in the
    user_data application.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'user_data':
            return 'user_data'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'user_data':
            return 'user_data'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'user_data' or obj2._meta.app_label == 'user_data':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'user_data':
            return db == 'user_data'
        return None





# # your_app/routers.py
# from django.db import models

# class MyDatabaseRouter:
#     def db_for_read(self, model, **hints):
#         if model._meta.app_label == 'my_label':
#             return 'USER_data'
#         return 'default'

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label == 'my_label':
#             return 'USER_data'
#         return 'default'

#     def allow_migrate(self, db, app_label, model_name=models, **hints):
#         if app_label == 'my_label':
#             return db == 'USER_data'
#         return db == 'default'
