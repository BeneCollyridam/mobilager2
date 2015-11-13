from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import *

def stock(request):
    products = Product.objects.all().filter(discontinued=False)
    context = {'products': products}
    return render(request, "stock.html", context)

def replenish(request):
    products = Product.objects.all().filter(discontinued=False)
    if request.method == 'GET':
        users = User.objects.all()
        context = {'products': products, 'names': users}
        return render(request, "replenish.html", context)
    elif request.method == 'POST':
        print(request.POST)

        updated = []
        for p in products:
            req_qty = int(request.POST[str(p.pk) + "_qty"])
            if req_qty != p.quantity:
                # FIXME: Do log handling here
                old_qty = p.quantity
                p.quantity = req_qty
                print("Changed quantity" + str(req_qty))
                updated.append((p, old_qty))
                p.save()
        changes = []
        if len(updated) > 0:
            user = User.objects.get(pk = request.POST['who'])
            event = Event(name = user,
                          description = request.POST['what'])
            event.save()
            for p, old_qty in updated:
                print("old_qty " + str(old_qty))
                event.change_set.add(Change(product = p,
                                             quantity = p.quantity,
                                            delta = p.quantity - old_qty))

        return HttpResponseRedirect("/replenish/")

def restock(request):
    pass

def correction(request):
    pass

def history(request):
    events = Event.objects.order_by("-date").order_by("-time")
    return render(request, "history.html", {'events': events})
