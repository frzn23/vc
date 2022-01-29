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
    return render(request, 'master/index.html')


def handle(request):
    if request.method=="POST":
        user_name = request.POST['user']
        password = request.POST['pass']
        user = authenticate(username=user_name, password=password)
        if user is not None:
            login(request,user)
            return render(request,'master/welcome.html')
        else:
            return render(request,'master/index.html',{'error':True})

    else:
        return render(request,'master/index.html')

def out(request):
    # if request.method=="POST":
    logout(request)
    return render(request,'master/index.html')

def manage(request):
    if request.method=="POST":
        filter_id = request.POST['id']
        orders = list(Order.objects.filter(order_id=filter_id))
        orders_param = []
        for i in orders:
            if "Delivered" not in i.status:
                orders_param.append(i)

        params = {'order':orders_param}
        return render(request, "master/manage.html",params)



    orders = list(Order.objects.all().order_by("-order_id"))
    orders_param = []
    for i in orders:
        if "Delivered" not in i.status:
            orders_param.append(i)
    params = {'order':orders_param}
    return render(request, "master/manage.html",params)

def manage_int(request,int):
    
    c_id=int
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
        params = {'order':orders,'last_status':last_status,'success':True}

        if update=="In Laundry":
            if orders.order_name == "Wash & Fold" or orders.order_name == "Wash & Iron":

                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Picked From Your Doorstep & Recieved at Laundry, It Will Be Delivered Within 20 Hours. Keep using hanzo.co.in"     
            else:
                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Picked From Your Doorstep & Recieved at Laundry, It Will Be Delivered Within 54 Hours. Keep using hanzo.co.in"     

            to_client =f"+91{orders.phone}"
    
            account_sid = "AC956c0481a1259cf06686130dce2679df"
            auth_token  = "b168342293e80d3a0c7bfcf04f574ea5"
            
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                to=to_client, 
                from_="+17067603908",
                body=msg_for_client)

        if update=="Delivered":
            if orders.order_name == "Wash & Fold" or orders.order_name == "Wash & Iron":
                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Delivered At Your Doorstep Within 20 Hours. Thanks For Ordering at hanzo.co.in"     
            else:
                msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Delivered At Your Doorstep Within 54 Hours. Thanks For Ordering at hanzo.co.in"     

            to_client =f"+91{orders.phone}"

            account_sid = "AC956c0481a1259cf06686130dce2679df"
            auth_token  = "b168342293e80d3a0c7bfcf04f574ea5"
            
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                to=to_client, 
                from_="+17067603908",
                body=msg_for_client)


            
        messages.success(request,"Status Added")
        return redirect('/master')


    params = {'order':orders,'last_status':last_status}
    return render(request,'master/change.html',params)

def comment(request,id):
    orders = list(Order.objects.filter(order_id=id))
    params = {'order':orders}
    if request.method=="POST":
        comment = request.POST['comment']
        orders = Order.objects.get(order_id=id)
        orders.comment = comment
        orders.save()
        messages.success(request,"Comment Added/Updated")
        return redirect('/master')
        

    return render(request,'master/comment.html', params)

def wait(request,id):
    orders = Order.objects.filter(order_id=id)[0]
    if request.method=="POST":
        weight = request.POST['weight']
        Order.objects.filter(order_id=id).update(weight=weight)


        name = f"Name : {orders.name}"
        # address = orders.address
        # type = orders.order_name
        order_name = orders.order_name
        # print(order_name)
        if order_name=="Wash & Fold":
            
            total_price = float(weight)*50
            l_price = float(weight)*40
        if order_name=="Wash & Iron":
            total_price = float(weight)*70
            l_price = float(weight)*60
        
        price = f"Total Price : Rs. {int(total_price)}"

        Order.objects.filter(order_id=id).update(costumer_price=total_price+10, laundry_price=l_price)


        make_pdf(name,order_name,total_price)
        
        msg_for_client = f"Hello {orders.name}. Your Order Of - {orders.order_name} Has Been Picked From Your Doorstep, View Your Payment Reciept Here: hanzo.co.in/static/pdf/{file_name}"
        
        to_client =f"+91{orders.phone}"
    
        account_sid = "AC956c0481a1259cf06686130dce2679df"
        auth_token  = "b168342293e80d3a0c7bfcf04f574ea5"
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to=to_client, 
            from_="+17067603908",
            body=msg_for_client)
    

    return render(request,'master/weight.html')


    
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

