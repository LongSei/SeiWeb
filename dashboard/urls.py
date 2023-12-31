from django.urls import path
from .views import *
app_name = "SeiFinance"

urlpatterns = [
    path("", home, name="dashboard"),
    path("login", userLogin, name="login"),
    path("signup", userSignup, name="signup"),
    path("logout", userLogout, name="logout"),
    path("profile", profile, name="profile"),
    path("profile/myBlog", myBlog, name="myBlog"),
    path("editBlog/<int:postId>/", editBlog, name="editBlog"),
    path("addBlog", addBlog, name="addBlog"),
]