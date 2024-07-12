# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, DocumentForm
from .models import Document, Department, Category
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from simple_history.utils import update_change_reason
from datetime import datetime

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.employee.department.department_type == 'gov':
                    return redirect('/')  # 政务中心用户跳转到创建办件页面
                else:
                    return redirect('document_list')  # 非政务中心用户跳转到办件列表页面
            else:
                messages.error(request, '不存在的用户或者密码错误')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


def is_government_center(user):
    return user.employee.department.department_type == 'gov'


@login_required
@user_passes_test(is_government_center)
def create_document(request):
    if request.user.employee.department.department_type != 'gov':
        return HttpResponseForbidden("You don't have permission to access this page.")

    departments = Department.objects.exclude(department_type='gov')
    categories = Category.objects.all()
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.creator = request.user

            document.save()
            messages.success(request, 'Document created successfully.')
            update_change_reason(document, f'由政务中心 - {request.user.username} 创件')
            return redirect('document_list')
        else:
            messages.error(request, 'Failed to create document. Please check the form data.')
    else:
        form = DocumentForm()

    return render(request, 'create_document.html', {'categories': categories, 'form': form, 'departments': departments})


@login_required
def document_list(request):
    # 获取用户的部门类型
    user_department_type = request.user.employee.department.department_type

    # 获取状态筛选参数
    status = request.GET.get('status')

    # 获取紧急状态和超时状态筛选参数
    is_urgent = request.GET.get('is_urgent')
    is_overdue = request.GET.get('is_overdue')

    # 根据用户部门类型筛选文档列表
    if user_department_type == 'gov':
        documents = Document.objects.all()
    else:
        user_department_name = request.user.employee.department.name
        documents = Document.objects.filter(ordered_departments_text__contains=user_department_name)

    # 根据状态筛选文档
    if status:
        documents = documents.filter(status=status)

    # 根据紧急状态筛选文档
    if is_urgent == 'true':
        documents = [doc for doc in documents if doc.is_urgent]

    # 根据超时状态筛选文档
    if is_overdue == 'true':
        documents = [doc for doc in documents if doc.is_overdue]

    # 将过滤后的文档传递到模板中
    return render(request, 'document_list.html', {'documents': documents})


@login_required
def process_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['处理中', '已完成']:
            document.status = status
            user_instance = request.user.employee.user
            document.modified_by = user_instance
            document.save()
            update_change_reason(document, f'{user_instance.employee.department} - {request.user.username}')

            messages.success(request, f'Document status updated to {status}.')
            return redirect('document_list')
        else:
            messages.error(request, 'Invalid document status.')
    return render(request, 'process_document.html', {'document': document})


@login_required
def document_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render(request, 'document_detail.html', {'document': document})


@login_required
def transit_document(request, document_id):
    # 获取当前办件对象
    document = Document.objects.get(id=document_id)
    if request.method == 'POST':
        next_department_id = request.POST.get('next_department')
        # 检查是否选择了下一个承接部门
        if next_department_id:
            next_department = Department.objects.get(id=next_department_id)
            # 更新办件的承接部门为下一个部门
            document.department = next_department
            document.status = '已流转'  # 更新办件状态为已流转
            user_instance = request.user.employee.user
            document.modified_by = user_instance
            document.save()
            update_change_reason(document,
                                 f'由{user_instance.employee.department}的{request.user.username}流转至{document.department}')
            messages.success(request, '办件已成功流转至下一部门。')
            return redirect('document_detail', document_id=document.id)
        else:
            messages.error(request, '请选择下一个承接部门。')

    # 获取下一个可选的承接部门列表
    next_departments = Department.objects.exclude(id=document.department.id).exclude(department_type='gov')

    return render(request, 'transit_document.html', {'document': document, 'next_departments': next_departments})


def index(request):
    return render(request, 'index.html')


@login_required
@user_passes_test(lambda u: u.employee.department.department_type == 'gov')
def search_documents(request):
    # 获取查询参数的值
    submitter_id_card = request.GET.get('id_card')

    print("Submitter ID Card:", submitter_id_card)

    # 根据查询参数进行筛选
    documents = Document.objects.all()
    if submitter_id_card:
        documents = documents.filter(submitter_id_card=submitter_id_card)

    print("Number of documents:", documents.count())  # 输出符合条件的办件数量

    # 渲染模板并将查询结果传递给模板
    return render(request, 'search_documents.html', {'documents': documents})


# @login_required
# @user_passes_test(lambda u: u.employee.department.department_type == 'gov')
# def update_delivery_time(request):
#     if request.method == 'POST':
#         delivery_time_str = request.POST.get('delivery_time')
#         documents_to_update = request.POST.getlist('documents_to_update')
#
#
#         if not delivery_time_str:
#             messages.error(request, '请选择递送资料时间')
#             return redirect('document_list')
#
#         try:
#             # 使用带时区信息的当前时间
#             delivery_time = timezone.now()
#         except ValueError:
#             messages.error(request, '递送资料时间格式无效')
#             return redirect('document_list')
#
#         documents = Document.objects.filter(id__in=documents_to_update)
#         documents.update(delivery_time=delivery_time)
#         messages.success(request, '递送资料时间已成功更新')
#
#         return redirect('document_list')
#     else:
#         documents = Document.objects.all().order_by('-id')
#         return render(request, 'update.html', {'documents': documents})
@login_required
@user_passes_test(lambda u: u.employee.department.department_type == 'gov')
def update_delivery_time(request):
    if request.method == 'POST':
        delivery_time_str = request.POST.get('delivery_time')
        documents_to_update = request.POST.getlist('documents_to_update')

        if not delivery_time_str:
            messages.error(request, '请选择递送资料时间')
            return redirect('document_list')

        try:
            # 使用带时区信息的当前时间
            delivery_time = timezone.now()
        except ValueError:
            messages.error(request, '递送资料时间格式无效')
            return redirect('document_list')

        documents = Document.objects.filter(id__in=documents_to_update)
        documents.update(delivery_time=delivery_time)
        messages.success(request, '递送资料时间已成功更新')

        return redirect('document_list')
    else:
        date_filter = request.GET.get('date', None)
        if date_filter:
            # 这里理论上应该处理一下日期的格式，确保它是符合要求的
            documents = Document.objects.filter(assigned_at__date=date_filter).order_by('-id')
        else:
            documents = Document.objects.all().order_by('-id')

        return render(request, 'update.html', {'documents': documents})