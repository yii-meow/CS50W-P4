from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "following":
                [{"username": follower.followee.username, "user_id": follower.followee.id} for follower in
                 Follow.objects.filter(follower=User.objects.get(pk=self.id))],
            "followers_count": len(
                [follower.follower for follower in self.followee.all()]),
            "posts": [post.serialize() for post in self.posts.all().order_by("-timestamp")]
        }

    def is_valid_followers_count(self):
        return self.follower.count() >= 0

    def is_valid_post_count(self):
        return self.posts.count() >= 0


class Follow(models.Model):
    # A person who is being followed
    followee = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followee")

    # A person who follow others
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="follower")

    def serialize(self):
        return {
            "Followee": self.followee.serialize(),
            "Follower": self.follower.serialize()
        }

    def __str__(self):
        return f"""
             Followee: {self.followee.username},
             Follower: {self.follower.username}
        """

    def is_valid_follow(self):
        return self.followee.username != self.follower.username


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField("User", related_name="user_like", default=None, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": {"user_id": self.user.id, "username": self.user.username},
            "content": self.content,
            "timestamp": self.timestamp,
            "likes": self.likes,
            "liked_by": [user.id for user in self.liked_by.all()]
        }

    def __str__(self):
        return f"""
            {self.user.username} wrote 
            '{self.content}' at {self.timestamp}
        """

    def is_valid_user(self):
        return len(User.objects.filter(pk=self.user.id)) != 0

    def is_valid_content(self):
        return self.content not in ["", None]

    def is_valid_likes_count(self):
        return self.liked_by.count() >= 0
