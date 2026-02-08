from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404    
from .models import Task
from .forms import TaskForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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
    if not request.user.is_authenticated or request.user.username == "demo_user":
        messages.warning(request, "You need to sign up to edit tasks.")
        return redirect('task_list')

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    messages.success(request, "Task updated ✔")
    return redirect('task_list')


# Delete a task
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
    demo_user = User.objects.get(username='demo_user')
    tasks = Task.objects.filter(user=demo_user)
    return render(request, 'tasks/demo.html', {
        'tasks': tasks,
        'demo': True
        })
