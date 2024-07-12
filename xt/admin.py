from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Department, Document, Employee, Category
from .resources import DocumentResource
import datetime

admin.site.site_header = '协同平台'
admin.site.site_title = '协同平台'
admin.site.index_title = '协同平台'

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department_type')


admin.site.register(Department, DepartmentAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department')
    list_filter = ('department',)


admin.site.register(Employee, EmployeeAdmin)


@admin.register(Document)
class DocumentAdmin(ImportExportModelAdmin):
    list_display = (
    'id', 'title', 'creator', 'assigned_at', 'department', 'due_date', 'status', 'submitter_name', 'submitter_phone', 'category')
    list_filter = (
    'status', 'creator', 'title', 'department', 'assigned_at', 'due_date', 'submitter_name', 'submitter_id_card',
    'submitter_phone', 'category')
    resource_class = DocumentResource  # 将资源类关联到Django管理后台

admin.site.register(Category)
