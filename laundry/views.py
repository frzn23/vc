from ast import Or
from asyncio import current_task
from wsgiref.util import request_uri
from home.views import order
from django import http
from django.contrib import auth
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from home.models import Order
from datetime import datetime
import pytz, os, random
from twilio.rest import Client
import requests


def index(request):
    if request.user.is_authenticated and request.user.last_name!='c' and request.user.last_name!='delivery':
        my_code = request.user.last_name
        orders = Order.objects.filter(refer_code=my_code)
        orders_param = []
        for i in orders:
            if "Delivered" not in i.status:
                orders_param.append(i)
        params = {'order':orders_param, 'name':request.user.first_name}
        return render(request, 'laundry/shop.html', params)


    else:
        return redirect('/laundry-panel/login')


def more(request,id):

    if request.method=="POST":
        order_id = request.POST['id']
        order = Order.objects.filter(order_id=order_id)[0]
        my_code = request.user.last_name
        if my_code != 'db' or my_code != '':
            orders = Order.objects.filter(refer_code=my_code)
            if my_code=='fine':
                laundry="Finewash Laundry"
            elif my_code=='bilal':
                laundry="Bilal Dry Clean"
            else:
                laundry="Undefined"

            
            msg = f"Order with order Id - {order_id}, Name-{order.name}, Laundry-{laundry} Is Ready To Be Picked Please Reach As Soon As Possible."
            url_link = f"https://api.telegram.org/bot5282886784:AAHTAX7RvbhewVLYI1lWQ5EH46cAdn35NTk/sendMessage?chat_id=-791553727&text={msg}"
            requests.get(url_link)
            orders_param = []
            for i in orders:
                if "Delivered" not in i.status:
                    orders_param.append(i)
            params = {'order':orders_param, 'ready':True,'name':request.user.first_name}
            return render(request, 'laundry/shop.html', params)

        return render(request, 'laundry/shop.html',params)

    if request.user.is_authenticated:
        my_code = request.user.last_name
        if my_code != 'db' or my_code != '':
            orders = Order.objects.filter(refer_code=my_code,order_id=id)[0]
            if orders.refer_code == my_code:
                refer = True
            else:
                refer = False
            order_time = orders.timing
            order_time = order_time.split(',')
            order_time = order_time[0]

            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            timing = now.strftime("%d/%m/%Y %I:%M %p")

            og_time = datetime.strptime(order_time, '%d/%m/%Y %I:%M %p')
            current_time = datetime.strptime(timing, '%d/%m/%Y %I:%M %p')
            time_passed = current_time-og_time
            
            try:
                hours = int(str((time_passed))[:2])
            except Exception as e:
                hours = int(str((time_passed))[:1])

            if orders.order_name != "Wash & Fold" or orders.order_name != "Wash & Iron":
                if hours>59:
                    time_surpass = 'danger'
                else:
                    if 'days' in str(time_passed):
                        time_surpass = 'danger'
            else:
                if hours>19:
                    time_surpass = 'danger'
                else:
                    time_surpass = 'primary'

            try:
                params = {'order':orders, 'refer':refer, 'order_time':order_time,'time_passed':time_passed,'time_surpass':time_surpass}
            except Exception as e:
                params = {'order':orders, 'refer':refer, 'order_time':order_time,'time_passed':time_passed,'time_surpass':'primary'}

            return render(request, 'laundry/more.html', params)
        else:
            return redirect('/')

    else:
        return render(request, 'laundry/more.html')


def signin(request):
    laundry_list = ['hamd', 'bilal', 'fine']
    if request.user.is_authenticated:
        laundry_exist = laundry_list.count(request.user.last_name)
        if laundry_exist < 1:
            return redirect('/laundry-panel')
        else:
            return redirect('/')
    if request.method == "POST":
        username = request.POST.get('user','')
        passw = request.POST.get('password','')
        user = authenticate(username=username, password=passw)
        if user is not None:
            login(request, user)
            laundry_exist = laundry_list.count(request.user.last_name)

            if laundry_exist == 1:
                return redirect('/laundry-panel')
            else:
                return redirect('/')
    
        else:
            return render(request, 'laundry/login.html',{'auth_fail':True})
    return render(request, 'laundry/login.html')