
from django.apps import AppConfig




class AcademhubAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Academhub"

    def ready(self):
        # Импортируем модель здесь, внутри метода ready()
        from Academhub.models import GroupStudents
        from django.db import connection
        import threading
        import time

        def daily_task():
            from Academhub.models import CalendarGraphicOfLearningProcess
            from django.utils.timezone import now, localtime
            from django.utils.timezone import activate
            import pytz
            from django.conf import settings


            while True:
                print(f"Часовой пояс Django: {settings.TIME_ZONE}")
                activate(pytz.timezone("Europe/Moscow"))  # Устанавливаем Москву
                today = localtime().date()
                print(f"Исправленное локальное время: {today}")
                print(localtime().date())

                calendar_graphic = CalendarGraphicOfLearningProcess.objects.all()
                for calendar in calendar_graphic:
                    print(f"Группа: {calendar.group}, Дата сессии за первый семестр: {calendar.start_exam_date_first_semester},"
                          f"Дата сесии за второй семестр: {calendar.start_exam_date_second_semester}")
                    if today == calendar.start_exam_date_first_semester:
                        print("Ура, сегодня дата начала сессии первого семестра")
                    elif today == calendar.start_exam_date_second_semester:
                        print("Ура, сегодня дата начала сессии второго семестра")


                time.sleep(86400)  # Запуск раз в день

        thread = threading.Thread(target=daily_task, daemon=True)
        thread.start()
