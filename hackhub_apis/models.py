from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from .managers import CustomUserManager
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.db.models.signals import (
    post_save,
    post_delete
)
from django.dispatch import receiver
from django.core.cache import cache
from .utils import send_verification_email

class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.CharField(unique=True)
    username = models.CharField(unique=True,max_length=50)
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
    university = models.TextField(max_length=200,null=True,blank=True)
    github = models.TextField(blank=True,null=True)
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
    STATUS_CHOICES = [
        ("live","LIVE"),
        ("development","DEVELOPMENT"),
        ("archived","ARCHIVED")
    ]
    author = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='posts')
    title = models.CharField(max_length=100)
    content = models.TextField()
    technologies = models.JSONField(default=list,null=True,blank=True)
    category = models.JSONField(default=list,blank=True,null=True)
    likes = models.ManyToManyField(CustomUser,related_name='liked_posts',blank=True)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES,default="live")

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
    
class TeamFinder(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="team_finders")
    title = models.CharField(max_length=100)
    details = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    last_date = models.DateField()
    
@receiver([post_delete,post_save],sender = Post)
def clear_cache_func(sender,**kwargs):
    cache.delete("posts_lists")

@receiver([post_save],sender = CustomUser)
def send_email(sender,instance,created,*args,**kwargs):
    if created:
        send_verification_email(instance)
