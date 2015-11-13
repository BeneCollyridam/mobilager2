from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    acribe = models.BooleanField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    vendor = models.ForeignKey(Vendor)
    quantity = models.IntegerField(default=0)
    discontinued = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class EventType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class Event(models.Model):
    name = models.ForeignKey(User)
    other_name = models.CharField(max_length=255, default="")
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ["date", "time"]

class EventName(models.Model):
    name = models.ForeignKey(User)
    event = models.ForeignKey(Event)

    def __str__(self):
        return self.name + " participating in " + self.event

class Change(models.Model):
    event = models.ForeignKey(Event)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    delta = models.IntegerField()
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.product

    def changed(self):
        return self.delta != 0