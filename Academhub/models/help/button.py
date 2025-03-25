__all__ = (
    'Button',
)

class Button:
    def __init__(self, 
            name, 
            id=None, 
            link_name=None, 
            link_params=None,
            permission=None, 
            condition=None, 
        ):
        self.id = id
        self.name = name
        self.link_name = link_name
        self.link_params = link_params or []
        self.permission = permission
        self.condition = condition

    def is_accessible(self, user):
        if self.permission:
            return user.is_superuser or user.has_perm(self.permission)
        return True

    def is_visible(self, user, obj=None):
        if self.condition and obj:
            return self.condition(obj, user)
        return True