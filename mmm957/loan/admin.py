from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import MyUser, Borrower, Borrowing_Message, Price, Employee, Lender, Paying, Ad_Contact, Ad


class MyUserInline(admin.StackedInline):
    model = MyUser
    can_delete = False
    verbose_name_plural = "MyUser"


class UserAdmin(BaseUserAdmin):
    inlines = (MyUserInline,)


# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Borrower)
admin.site.register(Borrowing_Message)
admin.site.register(Price)
admin.site.register(Employee)
admin.site.register(Lender)
admin.site.register(Paying)
admin.site.register(Ad_Contact)
admin.site.register(Ad)