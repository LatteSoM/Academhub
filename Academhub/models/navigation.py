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

    def get(self, user=None):
        filtered_nav = []

        for link in self.__app_nav:
            if self._filter_link(link, user):
                filtered_nav.append(link)
                
        return filtered_nav

    def _filter_link(self, link, user):
        """Рекурсивная фильтрация ссылок"""
        if hasattr(link, 'sub_links'):
            # Фильтруем вложенные ссылки
            link.sub_links = [sub_link for sub_link in link.sub_links if self._filter_link(sub_link, user)]
            # ParentLink остается, только если sub_links не пустой
            return bool(link.sub_links)
        else:
            # Для ChildLink проверяем права
            return link.is_accessible(user)

class ParentLink:
    def __init__(self, name=None, sub_links=None):
        self.name = name
        self.sub_links = sub_links if sub_links is not None else []

class ChildLink:
    def __init__(self, name, url, permission_required=None):
        self.name = name
        self.url = url
        self.permission_required = permission_required

    def is_accessible(self, user):
        if not self.permission_required:
            return True
        return user.has_perm(self.permission_required) or user.is_superuser