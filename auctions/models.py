from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass 
    

class Listing(models.Model): #ARTICULOS DE SUBASTA
    
    #id = models.AutoField(primary_key=True) #no estoy segura
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", null=True) #si el usuario se elimina, se elimina sus listing
    title=models.CharField(max_length=64)
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(decimal_places=2, verbose_name="Starting Bid", max_digits=15)
    category = models.CharField(max_length=64)
    image = models.URLField(blank=True, verbose_name="Image URL", null=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.title

class Bid(models.Model): #OFERTAS
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing", null=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    bid_price = models.DecimalField(decimal_places=2, verbose_name="Bid Price", max_digits=15, null=True)

    def __str__(self):
        return f"{self.bidder} bid ${self.bid_price} for {self.listing}"

class Comment(models.Model): #COMENTARIOS
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", null=True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True)
    content = models.TextField(verbose_name="Comment", default="")
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.commenter} commented on {self.listing} ({self.timestamp.date()})"
class watchlist(models.Model):
    creator_list = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creador", null=True)
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_id", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"{self.creator_list} watchlist  {self.listing_id}"
