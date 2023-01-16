from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_filter = ()
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password', 'account')}),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'account')}
         ),
    )
    list_display = ('email', )
    search_fields = ('email', )
    ordering = ('email',)


class TestQuestionInline(admin.TabularInline):
    model = Question

    ordering = ('order',)

    readonly_fields = ['_pk']

    def _pk(self, obj: Question):
        return f'{obj.pk}'


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [TestQuestionInline]


@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    pass



