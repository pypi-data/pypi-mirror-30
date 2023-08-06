from django.contrib import admin

from .models import Project, Task


admin.site.register([Project, Task])
