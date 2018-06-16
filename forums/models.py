from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import Truncator
from django.contrib.auth.models import User
from uuslug import slugify
from tools.utils import random_str
import datetime

##版块
class Board(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    board_headimage = models.ImageField(upload_to='user_image', default='user_image/user0.jpg')  # 论坛版块头像
    slug = models.SlugField(max_length=30, unique=True, editable=False)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('board_topics', args=[self.slug])

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()

    def save(self, *args, **kwargs):
        truncated = Truncator(self.name)
        self.slug = slugify('{0}{1}'.format(self.id, truncated.chars(10)))
        super(Board,self).save(*args, **kwargs)


##主题
class Topic(models.Model):
    ##帖子标题
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=256)
    last_updated = models.DateTimeField(auto_now_add=True)
    ##版块
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='topics',
    )
    ##帖子创建者
    starter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topics',
    )
    ##浏览次数
    views = models.PositiveIntegerField(default=0)
    ##slug
    slug = models.SlugField(editable=False, unique=True, max_length=40)
    ######状态管理######
    state = models.CharField(max_length=20, choices=(('hot', '热帖'), ('normal', ' 普通'), ('water', '刷屏'),
                                                     ('attack', '攻击'), ('ad', '广告'), ('illegal', '违规')),
                             default=('normal', '普通'))
    report = models.CharField(max_length=10, null=True, blank=True,
                              choices=(('water', '刷屏'), ('attack', '攻击'), ('ad', '广告'), ('illegal', '违规')))
    agree = models.PositiveIntegerField(default=0)  # 点赞数量，这个与view共同组成热帖参考因子



    def __str__(self):
        return self.subject

    ##获取绝对路径
    def get_absolute_url(self):
        return reverse('topic_posts', kwargs={
            'slug': self.board.slug,
            'topic_slug': self.slug
        })

    ##自动生成slug
    def save(self, *args, **kwargs):
        truncated = Truncator(self.subject)
        self.slug = slugify('{0}{1}'.format(self.id, truncated.chars(10)))
        super(Topic, self).save(*args, **kwargs)


##帖子内容
class Post(models.Model):
    # 内容
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='+',
    )
    slug = models.SlugField(editable=False, unique=True, max_length=40)

    def __str__(self):
        truncated = Truncator(self.message)
        return truncated.chars(30)

    def save(self, *args, **kwargs):
        truncated = Truncator(self.message)
        self.slug = slugify(truncated.chars(10))
        super(Post, self).save(*args, **kwargs)

##论坛用户
class ForumUser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forum_user')
    nickname = models.CharField(max_length=30, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='user_image', blank=True, verbose_name='头像')
    signature = models.CharField(max_length=30, blank=True, verbose_name='个性签名', default='这家伙很懒')
    gender = models.SmallIntegerField(default=-1) # choaices=(('1', '男性'), ('0', '女性'), ('-1', '保密')), blank=True)  ##1代表男性， 0代表女性， -1代表未设定
    # 论坛活动数据
    total_topic = models.PositiveIntegerField(default=0, verbose_name='总帖子')
    total_post = models.PositiveIntegerField(default=0, verbose_name='总回复')
    total_agree = models.PositiveIntegerField(default=0, verbose_name='总赞数积分')
    collection = models.ManyToManyField(Topic, verbose_name="收藏", related_name='collection_users', blank=True)

    # 设置5个权限字段，拥有权限者可操作此表(在admin中授权用户)
    class Meta:
        permissions = (('read', '阅读'),
                       ('reply', '回复'),
                       ('post', '发帖'),
                       ('delete', '删除'),
                       ('control', '控制'))

    def save(self, *args, **kwargs):
        self.nickname = self.user.username  ##初始nickname与用户名相同
        super(ForumUser, self).save(*args, **kwargs)


