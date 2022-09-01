import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from .models import User, Post, Follow


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def posting(request):
    """Post a posting"""

    # Posting a post must be post method
    if request.method not in ["POST", "PUT"]:
        return JsonResponse({
            "error": "Must be a POST method to /post"
        }, status=400)

    if request.method == "POST":
        # Check the post
        data = json.loads(request.body)
        content = data.get("content", "")

        if not content:
            return JsonResponse({
                "error": "Content cannot be blank"
            }, status=400)

        # Save the post to user
        post = Post(
            user=User.objects.get(pk=request.user.id),
            content=content
        )
        post.save()

        return JsonResponse({
            "message": "Post Successfully"
        }, status=201)

    # PUT method
    elif request.method == "PUT":
        data = json.loads(request.body)

        if data.get("post_content") is None:
            return JsonResponse({
                "error": "Content must not be blank"
            }, status=400)
        else:
            # Check if this owner own this post
            try:
                user_posts = Post.objects.filter(user=User.objects.get(pk=request.user.id), id=int(data["post_id"]))

                if len(user_posts) != 0:
                    post = Post.objects.get(pk=int(data["post_id"]))
                    post.content = data["post_content"]
                    post.save()

                else:
                    return JsonResponse({
                        "error": "Only post owner can change the post content"
                    }, status=400)

            except Post.DoesNotExist:
                return JsonResponse({
                    "error": "Post does not exists."
                }, status=400)

        return HttpResponse(status=204)


def all_post(request):
    """Main Page which shows all posts"""
    posts = Post.objects.all()
    return JsonResponse([post.serialize() for post in posts.order_by("-timestamp")], safe=False)


def profile(request, account_id):
    try:
        User.objects.get(id=account_id)
    except User.DoesNotExist:
        return JsonResponse({
            "error": "User does not exist, ID: " + str(account_id)
        }, status=404)

    return render(request, "network/index.html")


@csrf_exempt
def profile_view(request, account_id):
    """Profile Details"""
    context = {}

    # Check for this profile
    try:
        account = User.objects.get(pk=account_id)

    except User.DoesNotExist:
        return JsonResponse({
            "error": "User does not exist, ID: " + str(request.user.id)
        }, status=404)

    # Check whether this user has followed this account
    try:
        follower = User.objects.get(pk=request.user.id)

        checkFollowStatus = Follow.objects.filter(followee=account, follower=follower)

        if checkFollowStatus:
            context["follow_status"] = True
        else:
            context["follow_status"] = False


    # User not logged in
    except User.DoesNotExist:
        context["follow_status"] = False  # Set preset value

    finally:
        context["account"] = account.serialize()
        return JsonResponse(context)


@csrf_exempt
@login_required()
def follow_or_unfollow_user(request):
    if request.method != "PUT":
        return JsonResponse({
            "Error": "Follow A user must be a put method"
        }, status=400)

    data = json.loads(request.body)

    # Check is data valid
    if data.get("user") is None or data.get("followStatus") is None:
        return JsonResponse({
            "Error": "Insufficient Information for follow/unfollow a user."
        }, status=400)

    # Check if this user exists
    try:
        target_user = User.objects.get(pk=data["user"])

    except User.DoesNotExist:
        return JsonResponse({
            "Error": "The target user does not exists."
        }, status=400)

    # If follow the target user
    if data["followStatus"]:
        # Add user to the target user's followers list
        new_follow = Follow(
            followee=target_user,
            follower=User.objects.get(pk=request.user.id)
        )
        new_follow.save()

    else:
        # Remove user from the followers list
        remove_follow = Follow.objects.filter(followee=target_user, follower=User.objects.get(pk=request.user.id))
        remove_follow.delete()

    return HttpResponse(status=204)


def following(request, account_id):
    """Show people who are being followed"""
    # Check for this profile
    try:
        following = User.objects.get(pk=account_id)

    except User.DoesNotExist:
        return JsonResponse({
            "error": "User does not exist, ID: " + str(account_id)
        }, status=404)

    return JsonResponse(following.serialize())


@login_required()
def followee_post(request):
    following_users = Follow.objects.filter(follower=User.objects.get(pk=request.user.id))

    posts = Post.objects.filter(user__in=[following_user.followee for following_user in following_users])

    return JsonResponse([post.serialize() for post in posts.order_by("-timestamp")], safe=False)


@csrf_exempt
@login_required()
def like_post(request):
    # Only Put Method
    if request.method != "PUT":
        return JsonResponse({
            "Error": "Only put method is allowed"
        }, status=400)

    try:
        data = json.loads(request.body)

        if data.get("like_status") is None or data.get("postId") is None:
            return JsonResponse({
                "Error": "number of likes cannot be empty"
            }, status=400)

        post = Post.objects.get(pk=int(data.get("postId")))

        # If user likes
        if data["like_status"]:
            post.likes += 1
            # Add users to liked by
            post.liked_by.add(User.objects.get(pk=request.user.id))

        # If user unlikes
        else:
            post.likes -= 1
            post.liked_by.remove(User.objects.get(pk=request.user.id))

        post.save()

    except Post.DoesNotExist:
        return JsonResponse({
            "Error": "Post does not exists"
        }, status=400)

    return HttpResponse(status=204)
