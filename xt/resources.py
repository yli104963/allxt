from import_export import resources
from .models import Document


class DocumentResource(resources.ModelResource):
    class Meta:
        model = Document
        fields = (
        'id', 'title', 'creator__username', 'assigned_at', 'department__name', 'due_date', 'status', 'submitter_name',
        'submitter_phone')  # 定义要导入/导出的字段
