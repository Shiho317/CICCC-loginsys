from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Todo
from .forms import TodoForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
# Create your views here.

def home(req):
  return render(req, 'todo/home.html')

def signupuser(req):
    if req.method == 'GET':
        return render(req, 'todo/signupuser.html', { 'form': UserCreationForm() } )
    else:
        if req.POST['password1'] == req.POST['password2']:
            try:
                user = User.objects.create_user(req.POST['username'], password=req.POST['password1'])
                user.save()
                login(req, user)
                return redirect('currenttodos')

            except IntegrityError:
                return render(
                    req, 
                    'todo/signupuser.html', 
                    { 
                        'form': UserCreationForm(), 
                        'error': 'That username has already been taken. Please choose a different name'
                    })
        else:
            return render(
                    req, 
                    'todo/signupuser.html', 
                    { 
                        'form': UserCreationForm(), 
                        'error': 'Passwords did not match'
                    })

def loginuser(req):
    if req.method == 'GET':
        return render(req, 'todo/loginuser.html', { 'form': AuthenticationForm() }) 
    else:
        user = authenticate(req, username=req.POST['username'], password=req.POST['password'])

        if user is None:
            return render(
                req, 
                'todo/loginuser.html', 
                { 
                    'form': AuthenticationForm() ,
                    'error': 'Username and password are incorrect'
                }) 
        else:
            login(req, user)
            return redirect('currenttodos')

@login_required
def logoutuser(req): 
    if req.method == 'POST':
        logout(req)
        return redirect('home')

@login_required
def currenttodos(req):
    todos = Todo.objects.filter(user=req.user, datecompleted__isnull=True)
    # todos = Todo.objects.filter(datecompleted__isnull=True)
    return render(req, 'todo/currenttodos.html', { 'todos' : todos })

@login_required
def createtodo(req):
    if(req.method == 'GET'):
        return render(req, 'todo/createtodo.html', { 'form': TodoForm() })
    else:
        try:
            form = TodoForm(req.POST)
            #create, but dont save the instance yet
            newtodo = form.save(commit=False)
            newtodo.user = req.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(req, 'todo/createtodo.html', { 'form': TodoForm(), 'error': 'Bad data passed in. Try again' })

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', { 'todos': todos })
                
@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(request.POST)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'error': 'Bad information...'})

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

def handler404(request, exception):
    return render(request, 'todo/404.html', status=404)