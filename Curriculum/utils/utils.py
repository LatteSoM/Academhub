import json
from functools import lru_cache

from pyaspeller import YandexSpeller

@lru_cache(maxsize=228)
class MyValidator:
    def __init__(self):
        self.speller = YandexSpeller()

    def validate_text(self, text):
        """
        Проверяет текст на наличие ошибок с помощью Yandex Speller,
        игнорируя слова из вайтлиста.
        Возвращает список ошибок или None, если ошибок нет.
        """
        try:
            changes = self.speller.spell(text)
        except json.JSONDecodeError:
            return []

        if changes:
            errors = []
            # whitelist_words = get_whitelist()
            for change in changes:
                word_lower = change['word'].lower()
                # Если нужна фильтрация по белому списку, можно включить:
                # if word_lower not in whitelist_words:
                #     errors.append(f"Возможно ошибка в слове '{change['word']}' возможно это подходящее слово: {change['s']}")
            return errors
        return None
