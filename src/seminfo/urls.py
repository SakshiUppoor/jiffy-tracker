from django.urls import path
from . import views
'''from django.conf.urls import url'''

app_name = 'seminfo'

urlpatterns = [
    path('',views.sem,name="sem"),
    path('<int:id>',views.seminfo,name="seminfo"),
    path('tt/',views.timetable,name="timetable"),
    path('add/',views.create,name="create"),
    path('add/timetable',views.create_tt,name="create_tt"),
    path('calendar/',views.calendarToday,name="calendartoday"),
    path('calendar/<str:date>/<str:month>/<str:year>',views.Calendar,name="calendar"),
    path('add/sem',views.add_sem,name="add_sem"),
    path('add/subjects',views.add_sub,name="add_sub"),
    path('delete/subject/<int:id>',views.delete_subject,name="delete_subject"),
    path('statistics/',views.stats,name="stats"),
    path('statistics/<int:id>/<str:category>',views.statsDetail,name="statsDetail"),
    path('schedule',views.scheduleDefault,name="scheduleDefault"),
    path('schedule/<str:day>',views.schedule,name="schedule"),
    path('about',views.about,name="about"),
]
