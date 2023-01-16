from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import Prefetch
from django.contrib.auth.password_validation import validate_password


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff=False, is_superuser=False, **other_fields):
        if not email:
            raise ValueError('Email address must be specified')

        if not password:
            raise ValueError('Password must be specified')

        user = self.model(
                    email=self.normalize_email(email),
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    **other_fields
                )
        validate_password(password)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **other_fields):
        return self._create_user(email, password, False, False, **other_fields)

    def create_superuser(self, email, password, **other_fields):
        return self._create_user(email, password, True, True, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=256,
        unique=True)
    account = models.IntegerField(default=0)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = CustomUserManager()

    @staticmethod
    def prefetch(q):
        q = q.prefetch_related(Prefetch('usertest_set', queryset=UserTest.objects.order_by('passed')))
        q = q.prefetch_related(Prefetch('userframe_set', queryset=UserFrame.objects.filter(active=True)))
        return q


class Test(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def prefetch(q):
        q = q.prefetch_related(Prefetch('question_set', queryset=Question.objects.order_by('order')))
        return q


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    answer = models.CharField(max_length=256)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.text}"


class UserTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    result = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)


class Frame(models.Model):
    TYPES = [
        ('login', 'login'),
        ('background', 'background'),
    ]
    color = models.CharField(max_length=256)
    price = models.IntegerField(default=0)
    type = models.CharField(max_length=256, choices=TYPES)

    def __str__(self):
        return f"{self.type}: {self.color}"


class UserFrame(models.Model):
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)

