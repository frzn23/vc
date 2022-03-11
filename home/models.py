from statistics import mode
from django.db import models
from datetime import date, datetime

# Create your models here.

class Services(models.Model):
    s_no = models.AutoField(primary_key=True)
    s_name = models.CharField(max_length=1000)
    s_desc = models.CharField(max_length=1000, default="")
    s_img = models.CharField(max_length=100, default="")
    s_price = models.CharField(max_length=100, default="")
    s_dc = models.CharField(max_length=100, default="10")
    s_ac = models.CharField(max_length=100, default="60")
    pr = models.CharField(max_length=100, default="true")
    def __str__(self):
        return self.s_name

class dry_clean_services(models.Model):
    s_no = models.AutoField(primary_key=True)
    s_name = models.CharField(max_length=100, default='')
    s_parent = models.CharField(max_length=100, default='')
    s_price = models.CharField(max_length=100,default="")
    
    def __str__(self):
        s = f"Name : {self.s_name} , Belongs to {self.s_parent}"
        return s

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    phone = models.IntegerField()
    order_name = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    timing = models.CharField(max_length=1000)
    status = models.CharField(max_length=1000, default="Order Placed")
    f_stat = models.IntegerField()
    comment = models.CharField(max_length=1000, default="-")
    weight = models.CharField(max_length=1000, default="Not Specified")
    laundry_price = models.CharField(max_length=1000, default="Not defined Yet")
    costumer_price = models.CharField(max_length=1000, default="Not defined Yet")
    laundry_review = models.CharField(max_length=1000, default="No review")
    delivery_review = models.CharField(max_length=1000, default="No review")
    refer_code = models.CharField(max_length=1000, default="-")

    def __str__(self):
        return f"ID : {self.order_id}, Order : {self.name}, Phone : {self.phone}, Order:{self.order_name}"

class Cred(models.Model):
    phone = models.IntegerField()
    name = models.CharField(max_length=1000)
    key = models.CharField(max_length=1000)
    def str(self):
        return f"Name: {self.name}, Phone: {self.phone}"

class deleted_orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    original_id = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    phone = models.IntegerField()
    order_name = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)

    def __str__(self):
        return f"ID : {self.original_id}"

 
