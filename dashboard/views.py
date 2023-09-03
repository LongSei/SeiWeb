from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from .form import LoginForm, DeletePostForm, PostBlog, ChangeProfileForm
from django.contrib.auth import authenticate, login, logout
import datetime
import os 
from django.utils.crypto import get_random_string

def home(request):
    form = DeletePostForm(request.POST)
    if request.method == "POST":
        if 'deleteId' in request.POST:
            instance = Blog.objects.get(id=request.POST['deleteId'])
            instance.delete()
            return redirect("SeiFinance:dashboard")
        if 'editId' in request.POST: 
            return redirect("SeiFinance:editBlog", request.POST['editId'])
    # username = database.child('Data').child('name').get().val()
    username = request.user.username
    blog = Blog.objects.all().order_by('-created_at')
    return render(request, "dashboard/dashboard.html", {"username": username, "blog": blog})

def userLogin(request): 
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                form = LoginForm()
                return redirect("SeiFinance:dashboard")
            else: 
                return render(request, "login/login.html", {"isExist": True})
        else: 
            return render(request, "login/login.html", {"isExist": True})
    return render(request, "login/login.html", {"form": form})

def userSignup(request): 
    if request.method == "POST": 
        isExist = User.objects.filter(username=request.POST['username']).exists()
        if isExist == False:
            user = User.objects.create_user(first_name=request.POST['name'], username=request.POST['username'], password=request.POST['password'], email=request.POST['email'])
            user.save()
            login(request, user)
            return redirect("SeiFinance:dashboard")
        else: 
            return render(request, "login/signup.html", {"isExist": isExist})
    return render(request, "login/signup.html")

def userLogout(request): 
    logout(request)
    return redirect("SeiFinance:dashboard")

def profile(request):
    if request.method == "POST": 
        print(request.POST)
        print(request.FILES)
        response = dict()
        instance = User.objects.get(username=request.user.username)
        if 'passwordOld' in request.POST and instance.check_password(request.POST['passwordOld']):
            response['checkPassword'] = True
            if ('password' in  request.POST) or ('passwordAgain' in request.POST): 
                if ('password' in  request.POST) and ('passwordAgain' in request.POST): 
                    if (request.POST['password'] == request.POST['passwordAgain'] and (request.POST['password'].isspace() == False) and (request.POST['password'] != '')): 
                        response['password'] = True
                    else: 
                        response['password'] = False
                else: 
                    response['password'] = False

            if 'name' in request.POST: 
                if User.objects.filter(first_name=request.POST['name']).exists() == False:
                    if (request.POST['name'].isspace() == False) and (request.POST['name'] != ''):
                        response['name'] = True
                    else: 
                        response['name'] = False
                elif request.POST['name'] == request.user.first_name: 
                    response['name'] = True
                else: 
                    response['name'] = False

            if 'email' in request.POST: 
                if User.objects.filter(email=request.POST['email']).exists() == False:
                    response['email'] = True
                elif request.POST['email'] == request.user.email: 
                    response['email'] = True
                else: 
                    response['email'] = False
        else: 
            response['checkPassword'] = False

        if 'avatar' in request.FILES: 
            response['avatar'] = True
        else: 
            response['avatar'] = False
        if (response['checkPassword'] == True): 
            if 'password' in response and response['password'] == True: 
                instance.set_password(request.POST['password'])
            if 'name' in response and response['name'] == True:
                instance.first_name = request.POST['name']
            if 'email' in response and response['email'] == True: 
                instance.email = request.POST['email']
            instance.save()

        if 'avatar' in response and response['avatar'] == True: 
            instance = Profile.objects.get(user=request.user.id)
            if instance.avatar != "" and os.path.exists(instance.avatar.path) == True: 
                os.remove(instance.avatar.path)
            instance.avatar = request.FILES['avatar']
            instance.saveImage()
                
        return redirect("SeiFinance:profile")
    return render(request, "profile/profile.html")

def myBlog(request): 
    form = DeletePostForm(request.POST)
    if request.method == "POST":
        if 'deleteId' in request.POST:
            instance = Blog.objects.get(id=request.POST['deleteId'])
            instance.delete()
            return redirect("SeiFinance:myBlog")
        if 'editId' in request.POST: 
            return redirect("SeiFinance:editBlog", request.POST['editId'])
    userId = request.user.id
    blog = Blog.objects.filter(user=userId).order_by('-created_at')
    return render(request, "blog/myBlog.html", {"blog": blog})

def editBlog(request, postId): 
    form = PostBlog(request.POST or None)
    blog = Blog.objects.get(id=postId)
    if request.method == "POST": 
        if form.is_valid(): 
            blog.header=request.POST['header']
            blog.body=request.POST['description']
            blog.created_at = datetime.datetime.now()
            blog.save()
            listBlogs = Blog.objects.filter(user=blog.user.id).order_by('-created_at')
            return redirect("SeiFinance:profile")
    return render(request, "blog/editBlog.html", {"blog": blog})

def addBlog(request): 
    form = PostBlog(request.POST or None)
    if request.method == "POST": 
        if form.is_valid(): 
            blog=Blog(header=request.POST['header'], body=request.POST['description'], user=request.user, created_at=datetime.datetime.now())
            blog.save()
            return redirect("SeiFinance:dashboard")
    return render(request, "blog/editBlog.html")