from django.contrib import admin

from .models import task

class ListForm(admin.ModelAdmin):
    list_display=('xlsname','crontime','createtime','interstat')
    list_filter=('xlsname',)

admin.site.register(task,ListForm)
