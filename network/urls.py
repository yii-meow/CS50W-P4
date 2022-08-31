from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("posting", views.posting, name="posting"),
    path("posts", views.all_post, name="all_posts"),

    path("profile/<int:account_id>", views.profile, name="profileView"),
    path("profile/<int:account_id>/following", views.profile, name="following"),
    path("followeePost/", views.index, name="followeePost"),
    path("pagination", views.index, name="pagination"),
    path("likePost", views.like_post, name="likePost"),
    path("followOrUnfollowUser", views.follow_or_unfollow_user, name="followOrUnfollow"),

    # API
    path("profileView/<int:account_id>", views.profile_view, name="profileView"),
    path("profileView/<int:account_id>/following", views.following, name="followingView"),
    path("followeePostView", views.followee_post, name="followeePostView")
]
