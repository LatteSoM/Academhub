class Navigation:
    """
    Класс для создания навигации.
    """

    def __init__(self, links=None):
        self.links = links or []

    def get(self):
        """
        Возвращает список ссылок навигации.
        """
        return self.links


class ParentLink:
    """
    Класс для родительской ссылки.
    """

    def __init__(self, name=None, sub_links=None):
        self.name = name
        self.sub_links = sub_links or []

    def get(self):
        """
        Возвращает словарь с данными родительской ссылки.
        """
        return {
            'name': self.name,
            'sub_links': [link.get() for link in self.sub_links],
        }


class ChildLink:
    """
    Класс для дочерней ссылки.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def get(self):
        """
        Возвращает словарь с данными дочерней ссылки.
        """
        return {
            'name': self.name,
            'url': self.url,
        }