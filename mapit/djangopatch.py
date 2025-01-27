import django
import inspect

# Django 1.6 renamed Manager's get_query_set to get_queryset, and the old
# function will be removed entirely in 1.8. We work back to 1.4, so use a
# metaclass to not worry about it.
if django.VERSION < (1, 6):
    class GetQuerySetMetaclass(type):
        def __new__(cls, name, bases, attrs):
            new_class = super(GetQuerySetMetaclass, cls).__new__(cls, name, bases, attrs)

            old_method_name = 'get_query_set'
            new_method_name = 'get_queryset'
            for base in inspect.getmro(new_class):
                old_method = base.__dict__.get(old_method_name)
                new_method = base.__dict__.get(new_method_name)

                if not new_method and old_method:
                    setattr(base, new_method_name, old_method)
                if not old_method and new_method:
                    setattr(base, old_method_name, new_method)

            return new_class
else:
    # Nothing to do, make an empty metaclass
    from django.db.models.manager import RenameManagerMethods
    class GetQuerySetMetaclass(RenameManagerMethods):
        pass

