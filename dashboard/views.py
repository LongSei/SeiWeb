from django.shortcuts import render, redirect
from .models import Profile, Blog
from django.contrib.auth.models import User
from .form import LoginForm, DeletePostForm, PostBlog, SignupForm
from django.contrib.auth import authenticate, login, logout
import datetime

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
    form = SignupForm(request.POST)
    if request.method == "POST": 
        if form.is_valid(): 
            isExist = User.objects.filter(username=request.POST['username']).exists()
            if isExist == False:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'])
                user.save()
                login(request, user)
                return redirect("SeiFinance:dashboard")
            else: 
                return render(request, "login/signup.html", {"isExist": isExist})
        else: 
            isExist = True
            return render(request, "login/signup.html", {"isExist": isExist})
    return render(request, "login/signup.html", {"form": form})

def userLogout(request): 
    logout(request)
    return redirect("SeiFinance:dashboard")

def profile(request): 
    form = DeletePostForm(request.POST)
    if request.method == "POST":
        if 'deleteId' in request.POST:
            instance = Blog.objects.get(id=request.POST['deleteId'])
            instance.delete()
            return redirect("SeiFinance:profile")
        if 'editId' in request.POST: 
            return redirect("SeiFinance:editBlog", request.POST['editId'])
    userId = request.user.id
    blog = Blog.objects.filter(user=userId).order_by('-created_at')
    return render(request, "blog/profile.html", {"blog": blog})

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
            return redirect("SeiFinance:profile")
    return render(request, "blog/editBlog.html")