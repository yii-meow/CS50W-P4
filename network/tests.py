from django.db.models import Max
from django.test import TestCase, Client
from .models import User, Follow, Post


# Create your tests here.

class NetworkTestCase(TestCase):

    def setUp(self):
        # Create User
        user1 = User.objects.create_user("foo", "foo@gmail.com", "foo")
        user2 = User.objects.create_user("bar", "bar@gmail.com", "bar")
        user3 = User.objects.create_user("baz", "baz@gmail.com", "baz")

        # Create Posts
        post1 = Post.objects.create(user=user1, content="Hi")
        post2 = Post.objects.create(user=user1, content="Hey")

        # Create invalid post - blank
        Post.objects.create(user=user2)

        # Create like for posts 1
        post1.liked_by.add(user1)
        post1.liked_by.add(user2)
        post1.liked_by.add(user3)
        post1.liked_by.remove(user2)
        post1.liked_by.add(user2)

        # Create like for posts 2
        post2.liked_by.add(user1)
        post2.liked_by.add(user2)
        post2.liked_by.remove(user1)
        post2.liked_by.remove(user2)

        # Create Follow
        Follow.objects.create(followee=user1, follower=user2)
        Follow.objects.create(followee=user2, follower=user2)

    def test_post_validity(self):
        user1 = User.objects.get(username="foo")
        user2 = User.objects.get(username="bar")

        """Post count matches"""
        a = Post.objects.filter(user=user1)
        self.assertEqual(a.count(), 2)
        self.assertTrue(user1.is_valid_post_count())

        c = Post.objects.get(user=user2)
        self.assertTrue(c.is_valid_content)

        b = Post.objects.all()
        self.assertEqual(b.count(), 3)

    def test_likes(self):
        """Likes count"""
        post1 = Post.objects.get(pk=1)
        post2 = Post.objects.get(pk=2)

        self.assertEqual(post1.liked_by.count(), 3)
        self.assertTrue(post1.is_valid_likes_count())

        self.assertEqual(post2.liked_by.count(), 0)

    def test_follow(self):
        """Validity of Follow"""
        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)

        follow_status1 = Follow.objects.get(pk=1)
        follow_status2 = Follow.objects.get(pk=2)

        self.assertEqual(user1.followee.count(), 1)

        self.assertTrue(follow_status1.is_valid_follow())
        self.assertFalse(follow_status2.is_valid_follow())

        self.assertTrue(user1.is_valid_followers_count())

    def test_index(self):
        # Setup Client
        c = Client()

        response = c.get("/")

        self.assertEqual(response.status_code, 200)

    def test_valid_and_invalid_page(self):
        c = Client()

        valid_profile = c.get("/profile/1")
        self.assertEqual(valid_profile.status_code, 200)

        max_id = User.objects.all().aggregate(Max("id"))["id__max"]
        invalid_profile = c.get(f"/profile/{max_id + 1}")
        self.assertEqual(invalid_profile.status_code, 404)
