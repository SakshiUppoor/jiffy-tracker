from django.contrib import admin
from .models import Semester, Subject, Day, Timetable, Lecture, SubjectMonth
from django.contrib import admin

# Register your models here.


def save_model(self, request, obj, form, change):
    obj.added_by = request.user
    super().save_model(request, obj, form, change)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'attendance', 'lec_to_skip', 'user')

    def user(self, obj):
        return obj.semester.user


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')


class SubjectMonthAdmin(admin.ModelAdmin):
    list_display = ('month', 'subject',  'semester',
                    'lec_to_skip', 'attendance')

    def user(self, obj):
        return obj.semester.user


class LectureAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date', 'status')

    def user(self, obj):
        return obj.semester.user


class DayAdmin(admin.ModelAdmin):
    list_display = ('period', 'name')

    def user(self, obj):
        return obj.semester.user


admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Timetable)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(SubjectMonth, SubjectMonthAdmin)
