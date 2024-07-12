from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Department(models.Model):
    DEPARTMENT_TYPE_CHOICES = [
        ('gov', '政务部门'),
        ('functional', '承接部门')
    ]

    name = models.CharField(max_length=100, verbose_name="部门名字")
    department_type = models.CharField(max_length=20, choices=DEPARTMENT_TYPE_CHOICES, verbose_name="部门类型")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = verbose_name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name


class Document(models.Model):
    STATUS_CHOICES = [
        ('未接收', '未接收'),
        ('处理中', '处理中'),
        ('已完成', '已完成'),
        ('已流转', '已流转')
    ]

    title = models.CharField(max_length=100, verbose_name="办件名")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="分类", null=True, blank=True)
    submitter_name = models.CharField(max_length=100, verbose_name="递交人姓名")
    submitter_id_card = models.CharField(max_length=18, verbose_name="递交人身份证号")
    submitter_phone = models.CharField(max_length=11, verbose_name="递交人手机号")
    content = models.TextField(verbose_name="备注")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='documents',
                                   verbose_name="承接部门")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='未接收', verbose_name="状态")
    assigned_at = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name="分配时间")
    due_date = models.DateTimeField(verbose_name="截至日期")
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="修改人",
                                    related_name='modified_documents')
    history = HistoricalRecords()

    previous_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                            verbose_name="上一个承接部门", related_name='previous_documents')

    ordered_departments_text = models.TextField(verbose_name="按顺序承接的部门列表", blank=True)

    delivery_time = models.DateTimeField(null=True, blank=True, verbose_name="递送资料时间")
    @property
    def is_urgent(self):
        """判断办件是否紧急"""
        # 获取当前时间
        current_time = timezone.now()
        # 计算距离截止日期还有多少时间（以天为单位）
        remaining_days = (self.due_date - current_time).days
        # 如果距离截止日期不足3天，则视为紧急
        return remaining_days <= 3

    @property
    def is_overdue(self):
        """判断办件是否超时"""
        # 获取当前时间
        current_time = timezone.now()
        # 如果当前时间超过截止日期，则办件超时
        return current_time > self.due_date

    def save(self, *args, **kwargs):
        if self.previous_department != self.department:
            # 如果部门发生变化，更新按顺序承接的部门列表文本字段
            self.ordered_departments_text += f"{self.department.name} ,"
            self.previous_department = self.department  # 更新上一个承接部门为当前部门
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "办件"
        verbose_name_plural = verbose_name


