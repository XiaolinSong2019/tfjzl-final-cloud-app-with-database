from django.contrib import admin
# Seven imported classes:
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


# -------------------------------------------------------------
# Inlines
# -------------------------------------------------------------
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


# -------------------------------------------------------------
# ModelAdmin Classes
# -------------------------------------------------------------
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'course']


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['content', 'grade', 'course']
    search_fields = ['content']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['content', 'is_correct', 'question']


# -------------------------------------------------------------
# Registrations
# -------------------------------------------------------------
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission)
