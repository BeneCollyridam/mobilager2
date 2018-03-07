from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .models import *

qty_verify_funs = {'restock': {0: lambda a, b: a >= b,
                               1: lambda a, b: a <= b},
                   'replenish': {0: lambda a, b: a <= b,
                                 1: lambda a, b: a >= b},
                   'correction': {0: lambda a, b: True,
                                  1: lambda a, b: True}}


def _update_stock(request, change_type):
    products = Product.objects.all().filter(discontinued=False).order_by('name')
    if request.method == 'GET':
        if change_type == 'replenish':
            products = products.filter(quantity__gt=0)

        users = User.objects.all().filter(is_active=True).order_by('username')
        context = {'sellables': products.filter(category=0),  # FIXME: Magic numbers
                   'refundables': products.filter(category=1),
                   'names': users}
        return render(request, change_type + ".html", context)
    elif request.method == 'POST':
        if len(request.POST.getlist("who")) == 0:
            return HttpResponse("From validation error: no users selected")

        with transaction.atomic():
            updated = []
            for p in products:
                req_qty = int(request.POST[str(p.pk) + "_qty"])
                changed = req_qty != p.quantity
                updated.append((p, req_qty, changed))
                # TODO: Tell the user whats wrong in a nicer way
                if not (req_qty >= 0 and
                        qty_verify_funs[change_type][p.category](req_qty, p.quantity)):
                    transaction.set_rollback(True)
                    return HttpResponse("Form validation error: Invalid product quantity");

            if any(map(lambda t: t[2], updated)):
                # TODO: Do something better with EventType handling
                event = Event(description=request.POST['what'],
                              event_type=EventType.objects.get(tag=change_type),
                              logged_user=request.user)
                event.save()
                for u in request.POST.getlist("who"):
                    event.eventbyuser_set.add(EventByUser(
                        name = User.objects.get(pk = u)),
                                            bulk=False)

                for p, req_qty, changed in updated:
                    event.change_set.add(Change(product = p,
                                                quantity = req_qty,
                                                delta = req_qty - p.quantity),
                                         bulk=False)
                    if changed:
                        p.quantity = req_qty
                        p.save()

                return HttpResponseRedirect("/"+ change_type)
            else:
                transaction.set_rollback(True)
                return HttpResponse("Form validation error: No quantities changed")


@login_required
def stock(request):
    products = Product.objects.all().filter(discontinued=False)
    context = {'products': products}
    return render(request, "stock.html", context)


@login_required
def replenish(request):
    return _update_stock(request, "replenish")


@login_required
def restock(request):
    return _update_stock(request, "restock")


@login_required
def correction(request):
    return _update_stock(request, "correction")


@login_required
def history(request):
    events = Event.objects.order_by("-date", "-time")
    e = list(map(lambda x: {'event': x,
                            'changes': x.change_set.filter(~Q(delta = 0))},
             events))

    return render(request, "history.html", {'events': e})


@login_required
def addbtn_fragment(request):
    category = request.GET['category']
    return render(request, "addproduct-fragment.html", {'category': category})


@login_required
def addform_fragment(request):
    category = request.GET['category']
    if request.method == "GET":
        products = Product.objects.all()
        vendors = Vendor.objects.all()
        return render(request, "addproduct-form-fragment.html", {'products': products,
                                                                 'vendors': vendors,
                                                                 'category': category})
    elif request.method == "POST":
        # FIXME: Put this mapping into the model somehow
        catn = int(category == 'refundable')
        p = request.POST

        # Check if vendor exists by case-insensitive look up by name, otherwise create new
        try:
            vendor = Vendor.objects.get(name__iexact=p['vendor'].strip())
        except Vendor.DoesNotExist:
            vendor = Vendor(name=p['vendor'].strip())
            vendor.save()

        product = Product(category=catn, name=p['pname'], vendor=vendor)
        product.save()

        return render(request, "product-fragment.html", {'product': product,
                                                         'category': category})
        #  product = Product(category=catn, name=p['']
