from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import *
# Create your views here.

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


def product(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products':products})


def customers(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()

    context = {
        'customer': customer,
        'orders': orders,
        'order_count': order_count
    }
    return render(request, 'accounts/customers.html',context)


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


def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method =='POST':
        order.delete()
        return redirect('/')
    context={'item': order}
    return render(request, 'accounts/delete.html', context)