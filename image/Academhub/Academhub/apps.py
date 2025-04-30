

from django.apps import AppConfig




class AcademhubAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Academhub"

    def ready(self, daily_task=None):
        from .signals import setup_signals
        setup_signals()
        # Импортируем модель здесь, внутри метода ready()
        import threading
        import time
        from Academhub.models import Gradebook
        from datetime import timedelta


        def daily_task():
            semester_number_of_grade_book = 0
            print(f"⏳ Поток daily_task запущен! Активные потоки: {[t.name for t in threading.enumerate()]}")
            from django.utils.timezone import localtime
            from django.utils.timezone import activate
            import pytz


            while True:
                activate(pytz.timezone("Europe/Moscow"))  # Устанавливаем Москву
                today = localtime().date()

                for gradebook in Gradebook.objects.all():
                    if gradebook.date_of_opening is not None and gradebook.amount_of_days_for_closing is not None:
                        if today > (gradebook.date_of_opening + timedelta(days=gradebook.amount_of_days_for_closing)) and \
                            gradebook.status not in ["Закрыта", "Заполнена"]:
                            print(f"Ведомость {gradebook.name} просрочена!")
                            gradebook.status = Gradebook.STATUS_CHOICE[4][1]
                            gradebook.save()

                time.sleep(86400)  # Запуск раз в день

        if not any(thread.name == "daily_task" for thread in threading.enumerate()):
            thread = threading.Thread(target=daily_task, name="daily_task", daemon=True)
            thread.start()
