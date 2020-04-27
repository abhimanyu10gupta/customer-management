from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .filters import OrderFilter
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .decorators import *
from django.contrib.auth.models import Group

# Create your views here.

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account was created for: ' + username)
            return redirect('login')
    context ={'form':form, 'messages':messages}
    return render(request,'accounts/register.html',context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'username or password is incorrect')
    context = {}
    return render(request,'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='pending').count()
    context = {
        'orders':orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
    }

    print(orders)

    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    context = {'form':form}

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    return render(request, 'accounts/account_settings.html', context)

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='pending').count()

    context = {'orders': orders, 'customers': customers,
               'total_orders':total_orders, 'delivered':delivered, 'pending':pending,
               'total_customers':total_customers}
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def product(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products':products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def customers(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()

    my_filter = OrderFilter(request.GET, queryset=orders)
    orders = my_filter.qs

    context = {
        'customer': customer,
        'orders': orders,
        'order_count': order_count,
        'my_filter': my_filter
    }
    return render(request, 'accounts/customers.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formSet = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # print('printing post', request.POST)
        formSet = OrderFormSet(request.POST, instance=customer)
        if formSet.is_valid():
            formSet.save()
            return redirect('/')
    context = {'formSet': formSet}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def updateOrder(request,pk):

    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        # print('printing post', request.POST)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method =='POST':
        order.delete()
        return redirect('/')
    context={'item': order}
    return render(request, 'accounts/delete.html', context)

