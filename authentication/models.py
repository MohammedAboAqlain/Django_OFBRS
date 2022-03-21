from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager,PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Market(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def _create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise AttributeError("User must set an email address")
        else:
            phone = phone
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_staffuser(self, phone, password=None, **extra_fields):
        """Creates and returns a new staffuser using an email address"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        """Creates and returns a new superuser using an email address"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Type(models.IntegerChoices):
        Admin = 0, "Admin"
        Seller = 1, "Seller"
        Fisherman_1 = 5, "Fisherman_1"
        Fisherman_2 = 6, "Fisherman_2"
    phone = models.CharField(
        _('phone number'),
        max_length=15,
        unique=True,
        error_messages={
            'unique': _("phone is used"),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    darsh_key = models.IntegerField(
        _('darsh key'),
        unique=True,
        null=True,
        error_messages={
            'unique': _("darsh key is used"),
        },
    )
    market = models.ForeignKey('authentication.Market',null=True,blank=True, on_delete=models.CASCADE,default=None)

    name = models.CharField(_('name'), max_length=100, blank=True , null=True)
    type_id = models.PositiveSmallIntegerField(
        choices=Type.choices,
        default=Type.Admin,
    )
    is_deleted = models.BooleanField(
        _('is deleted'),
        default=False,
    )
    def balance(self):
        return (sum(list(Entries.objects.filter(taker_id=self).values_list('quantity', flat=True))) - sum(list(Entries.objects.filter(giver_id=self).values_list('quantity', flat=True))))

    def __str__(self):
        return self.phone
    def market_id(self):
        if self.market:
            return self.market.id
        else:
            return None

class EntryType(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    category = models.IntegerField(default=0)
    short_desc = models.TextField(null=True,blank=True)
    def __str__(self):
        return str(self.category)


class Entries(models.Model):
    type = models.ForeignKey('authentication.EntryType', on_delete=models.CASCADE)
    giver_id = models.ForeignKey('authentication.User', on_delete=models.CASCADE ,related_name='giver_id')
    taker_id = models.ForeignKey('authentication.User', on_delete=models.CASCADE,related_name='taker_id')
    quantity = models.IntegerField(default=0)
    unit_price = models.IntegerField(null=True,blank=True)
    comment =  models.TextField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.giver_id.phone

    def giver_name(self):
        if self.giver_id:
            if self.giver_id.name:
                return self.giver_id.name
            else:
                return None
        else:
            return None
    def taker_name(self):
        if self.taker_id:
            if self.taker_id.name:
                return self.taker_id.name
            else:
                return None
        else:
            return None


class StorageEntry(models.Model):
    type = models.ForeignKey('authentication.EntryType', on_delete=models.CASCADE, related_name='type')
    caused_by = models.ForeignKey('authentication.EntryType', on_delete=models.CASCADE,related_name='caused_by')
    quantity_diff = models.IntegerField(default=0)
    comment = models.TextField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.caused_by.name

class StaticSettings(models.Model):
    project_name = models.CharField(max_length=255,null=True,blank=True)
    Admin_name = models.CharField(max_length=255,null=True,blank=True)
    in_storage = models.CharField(max_length=255,null=True,blank=True)

class FAQ(models.Model):
    question =  models.TextField(null=True,blank=True)
    answer =  models.TextField(null=True,blank=True)
