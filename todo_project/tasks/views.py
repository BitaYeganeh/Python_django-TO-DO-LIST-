from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404    
from .models import Task
from .forms import TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.http import require_POST


def demo_task_list():
    # Demo tasks; empty (instead of a crash) when no demo_user exists yet
    return Task.objects.filter(user__username='demo_user').order_by('completed', 'created_at')

def task_list(request):
    # 🟢 LOGGED-IN USER MODE
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.user = request.user
                task.save()
                messages.success(request, "Task added ✔")
                return redirect('task_list')
        else:
            form = TaskForm()

        # Open tasks first, then finished ones
        tasks = Task.objects.filter(user=request.user).order_by('completed', 'created_at')

        return render(request, 'tasks/task_list.html', {
            'tasks': tasks,
            'done_count': tasks.filter(completed=True).count(),
            'form': form,
            'demo': False
        })

    # 🔵 DEMO MODE (NOT LOGGED IN)
    tasks = demo_task_list()

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'done_count': tasks.filter(completed=True).count(),
        'demo': True
    })


# Complete a task (POST only: a plain link must never change data)
@require_POST
def complete_task(request, task_id):
    if not request.user.is_authenticated or request.user.username == "demo_user":
        messages.warning(request, "You need to sign up to edit tasks.")
        return redirect('task_list')

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    messages.success(request, "Task updated ✔")
    return redirect('task_list')


# Delete a task (POST only: a plain link must never delete data)
@require_POST
def delete_task(request, task_id):
    if not request.user.is_authenticated or request.user.username == "demo_user":
        messages.warning(request, "You need to sign up to delete tasks.")
        return redirect('task_list')

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, "Task deleted 🗑️")
    return redirect('task_list')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            return redirect('task_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


def demo_tasks(request):
    tasks = demo_task_list()
    return render(request, 'tasks/demo.html', {
        'tasks': tasks,
        'done_count': tasks.filter(completed=True).count(),
        'demo': True
        })
