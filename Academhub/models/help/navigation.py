__all__ = ['Navigation', 'ParentLink', 'ChildLink']

class Navigation:
    def __init__(self, links=None):
        self.__app_nav = []
        if links:
            if isinstance(links, list):
                self.__app_nav.extend(links)
            else: 
                self.__app_nav.append(links)
    
    def get(self):
        return self.__app_nav

class ParentLink:
    def __init__(self, name=None, sub_links=None):
        self.name = name
        self.sub_links = sub_links if sub_links is not None else []

class ChildLink:
    def __init__(self, name, url, permission_required=None, teacher=False):
        self.name = name
        self.url = url
        self.permission_required = permission_required
        self.teacher = teacher