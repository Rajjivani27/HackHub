from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from .managers import CustomUserManager
from django.core.validators import FileExtensionValidator
from PIL import Image

class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True,max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','name']

    def __str__(self):
        return self.username
    
class Profile(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='profile')
    user_bio = models.TextField(max_length=300,blank=True,null=True)
    profile_pic = models.ImageField(upload_to='media/',blank=True,null=True)
    dob = models.DateField()
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        through='Follows',
        through_fields=('follower','followed')
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Post(models.Model):
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='posts')
    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.ManyToManyField(CustomUser,related_name='liked_posts',blank=True)
    created_at = models.DateField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.title
    
class PostMedia(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_media')
    files = models.FileField(
        upload_to='post_media/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','mp4','mov','webp'])]
    )
    
class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE,name='commented_posts')
    content = models.TextField(max_length=500)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}'s comment on {self.post}"
    
class Follows(models.Model):
    follower = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='following_relation')
    followed = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='follower_relation')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('follower','followed')

    def __str__(self):
        return f"{self.follower} follows {self.followed}"
