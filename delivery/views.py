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
from .pdf.fpdf import FPDF
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


def index(request):
    if not request.user.is_authenticated:
        return redirect('/delivery/login')

    if request.method=="POST":
        filter_id = request.POST['id']
        orders = list(Order.objects.filter(order_id=filter_id))
        orders_param = []
        for i in orders:
            if "Delivered" not in i.status:
                orders_param.append(i)
        if len(orders_param)==0:
            params = {'order':orders_param,'no_order':True}
        else:
            params = {'order':orders_param}
        return render(request, "delivery/index.html",params)

    orders = list(Order.objects.all().order_by("-order_id"))
    orders_param = []
    for i in orders:
        if "Delivered" not in i.status:
            orders_param.append(i)
    params = {'order':orders_param}
    return render(request, 'delivery/index.html',params)


def status(request,id):
    if not request.user.is_authenticated:
        return redirect('/delivery/login')

    c_id=int(id)
    orders = Order.objects.filter(order_id=c_id)[0]
    stat = orders.status.split(',')
    last_status=stat[-1]
    if request.method=="POST":
        update = request.POST['status_update']
        order_status = orders.status
        new_status = f"{order_status}, {update}"

        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        timing = now.strftime("%d/%m/%Y %I:%M %p")
        new_timing = f"{orders.timing}, {timing}"
        Order.objects.filter(order_id=c_id).update(status=new_status, timing=new_timing)

        if update=="Order Picked":
            weight = request.POST['weight']            

            Order.objects.filter(order_id=id).update(weight=weight)


            name = f"Name : {orders.name}"
            order_name = orders.order_name
            # print(order_name)
            if order_name=="Wash & Fold":
                total_price = float(weight)*50
                l_price = float(weight)*40
            if order_name=="Wash & Iron":
                total_price = float(weight)*70
                l_price = float(weight)*60
            
            try:
                price = f"Total Price : Rs. {int(total_price)}"
                Order.objects.filter(order_id=id).update(costumer_price=total_price+10, laundry_price=l_price)
                make_pdf(name,order_name,total_price)
            except Exception as e:
                var_pass = True            


            if orders.order_name == "Wash & Fold" or orders.order_name == "Wash & Iron":

                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Picked From Your Doorstep & Recieved at Laundry, It Will Be Delivered Within 20 Hours. Keep using hanzo.co.in"     
            else:
                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Picked From Your Doorstep & Recieved at Laundry, It Will Be Delivered Within 54 Hours. Keep using hanzo.co.in"     

            to_client =f"+91{orders.phone}"

    
        if update=="In Laundry":
            laundry_name = request.POST.get('laundry_name','')
            Order.objects.filter(order_id=id).update(refer_code=laundry_name)




        if update=="Delivered":
            if orders.order_name == "Wash & Fold" or orders.order_name == "Wash & Iron":
                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Delivered At Your Doorstep Within 20 Hours. Thanks For Ordering at hanzo.co.in"     
            else:
                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Delivered At Your Doorstep Within 54 Hours. Thanks For Ordering at hanzo.co.in"     


        
    return render(request, 'delivery/status.html',{'last_status':last_status,'orders':orders})


def comment(request,id):
    if not request.user.is_authenticated:
        return redirect('/delivery')
    orders = list(Order.objects.filter(order_id=id))
    params = {'order':orders}
    if request.method=="POST":
        comment = request.POST['comment']
        orders = Order.objects.get(order_id=id)
        orders.comment = comment
        orders.save()
    return render(request, 'delivery/comment.html',params)

def login_del(request):
    if request.user.is_authenticated:
        if request.user.last_name == 'delivery':
            return redirect('/delivery')
        else:
            return redirect('/delivery/logout')
    else:
        if request.method=="POST":
            user_name = request.POST.get('username','')
            pass_word = request.POST.get('password','')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                login(request, user)
                last_name = request.user.last_name
                if last_name == 'delivery':
                    return redirect('/delivery')
                else:
                    return redirect('/delivery/logout')
        
            else:
                return render(request, 'delivery/login.html',{'auth_fail':True})
        return render(request, 'delivery/login.html')

def logout_del(request):
    logout(request)
    return redirect('/delivery/login')


def make_pdf(n,s,p):
    no = random.randint(100,100000)
    # data which we are going to display as tables
    DATA = [
        [ "Name" , "Service", "Laundry Charge", "Delivery Charge" ],
        [
            n,
            s,
            f"{p}/-",
            "10/-",
        ],
        # [ "", "", "", ""],
        # [ "", "", "", ""],
        # [ "", "", "", ""],
        ["","",f"TOTAL: {p+10}/-"],
    ]

    # creating a Base Document Template of page size A4
    owd = os.getcwd()
    os.chdir('.')
    os.chdir('home/static/pdf')

    global file_name
    file_name = f"{no}.pdf"
    pdf = SimpleDocTemplate( f"{no}.pdf" , pagesize = A4 )

    # standard stylesheet defined within reportlab itself
    styles = getSampleStyleSheet()

    # fetching the style of Top level heading (Heading1)
    title_style = styles[ "Heading1" ]

    # 0: left, 1: center, 2: right
    title_style.alignment = 1

    # creating the paragraph with
    # the heading text and passing the styles of it
    title = Paragraph( "Billing Invoice - Hanzo (hanzo.co.in)" , title_style )

    # creates a Table Style object and in it,
    # defines the styles row wise
    # the tuples which look like coordinates
    # are nothing but rows and columns
    style = TableStyle(
        [
            ( "BOX" , ( 0, 0 ), ( -1, -1 ), 1 , colors.black ),
            ( "GRID" , ( 0, 0 ), ( 4 , 1 ), 1 , colors.black ),
            ( "BACKGROUND" , ( 0, 0 ), ( 3, 0 ), colors.gray ),
            ( "TEXTCOLOR" , ( 0, 0 ), ( -1, 0 ), colors.whitesmoke ),
            ( "ALIGN" , ( 0, 0 ), ( -1, -1 ), "CENTER" ),
            ( "BACKGROUND" , ( 0 , 1 ) , ( -1 , -1 ), colors.beige ),
        ]
    )

    # creates a table object and passes the style to it
    table = Table( DATA , style = style )


    # final step which builds the
    # actual pdf putting together all the elements
    pdf.build([ title , table ])

    os.chdir(owd)
