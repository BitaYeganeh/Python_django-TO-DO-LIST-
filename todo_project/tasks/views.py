from urllib import request
from django.shortcuts import render, redirect, get_object_or_404    
from .models import Task
from .forms import TaskForm
from django.contrib.auth.models import User
def task_list(request):

    # 🟢 LOGGED-IN USER MODE
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.user = request.user
                task.save()
                return redirect('task_list')
        else:
            form = TaskForm()

        tasks = Task.objects.filter(user=request.user)

        return render(request, 'tasks/task_list.html', {
            'tasks': tasks,
            'form': form,
            'demo': False
        })

# 🔵 DEMO MODE (NOT LOGGED IN)
    demo_user = User.objects.get(username='demo_user')
    tasks = Task.objects.filter(user=demo_user)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'demo': True
    })

# Complete a task
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')

# Delete a task, login required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.delete()
    return redirect('task_list')
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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

from django.contrib.auth.models import User

def demo_tasks(request):
    demo_user = User.objects.get(username='demo_user')
    tasks = Task.objects.filter(user=demo_user)
    return render(request, 'tasks/demo.html', {'tasks': tasks})

    