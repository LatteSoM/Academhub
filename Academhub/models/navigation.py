__all__ = [
    'Navigation',
    'ParentLink',
    'ChildLink'
]

class Navigation:
    __app_nav = []

    def __init__(self, links=None):
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
    def __init__(self, name, url):
        self.name = name
        self.url = url