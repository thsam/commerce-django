from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Listing, Comment, watchlist,User, Bid

LISTING_CATEGORIES = [
        ('BOOKS', 'Books'),
        ('MUSIC', 'Music'),
        ('MOVIES', 'Movies'),
        ('GAMES', 'Games'),
        ('COMPUTERS', 'Computers'),
        ('ELECTRONICS', 'Electronics'),
        ('HOME', 'Home'),
        ('HEALTH', 'Health'),
        ('TOYS', 'Toys'),
        ('FASHION', 'Fashion'),
    ]

#LISTING_CATEGORIES = ['Books','Electronics','Home','Health','Pets','Toys','Fashion','Sports']

def index(request):
    #1.- manejador de lista
    listing =Listing.objects.all()
    if request.user.is_authenticated:
        w=watchlist.objects.all().filter(creator_list=request.user).count()
        print("index watch",w)
    else:
        w = False
    print("index",listing)
    return render(request, "auctions/index.html",{
        "listings":listing,
        "watchlist":w
    })

#FORMULARIOS
class NewListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    price = forms.DecimalField(decimal_places=2,max_digits=15)
    category= forms.ChoiceField(choices=LISTING_CATEGORIES, label="Category")
    image=forms.URLField(label="Image URL", required=False)
    
 #fields = ['title', 'description', 'price', 'image', 'category']
#class NewBidForm(forms.Form):


class AddCommentForm(forms.Form):
    #listing=
    #commenter= user
    content=forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 5}))
    #timestamp=

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    print("hola")
    if request.method=="POST":
        print("enviando post...")
        form=NewListingForm(request.POST)
        if form.is_valid(): #todo correcto
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            #guardo en el modelo:
            listing = Listing(creator=request.user, title=title, description=description, price=price, image=image, category=category)
            listing.save()
            #redirecciono a index
            print("guardo")
            return HttpResponseRedirect(reverse("index"))
        
        else:
            return render(request, "auctions/create.html", { #le envío el form para que corrija
                "listing_form": form
            })

    return render(request, "auctions/create.html", { #al principio entrego el form
        "listing_form": NewListingForm()
    })

def listing(request,listing_id):
    #muestra el listing específico
    l=Listing.objects.get(id=listing_id) #aquí debo filtrar y colocar la última oferta más alta
    if request.user.is_authenticated:
        w=watchlist.objects.all().filter(creator_list=request.user).count()
        added=watchlist.objects.filter(creator_list=request.user,listing_id=listing_id) #da true o false
        if request.user == l.creator:
            creadorl=True
        else:
            creadorl=False
        #print("watchlist")
    else:
        w=False
        added=False
        creadorl=False
    #print(w)


    return render(request, "auctions/listing.html", {
        "listing": l,
        "comments":Comment.objects.filter(listing=l),
        "comment_form": AddCommentForm(),
        "watchlist": w,
        "added": added,
        "creador":creadorl
    })
@login_required
def close_listing(request,listing_id):
    set_close = Listing.objects.get(creator=request.user,id=listing_id)
    set_close.active=False
    set_close.save()
    #print("**** se ha desactivado")
    bidder_exits=Bid.objects.get(listing=set_close)
    print(bidder_exits)
    if(bidder_exits is not None):
        winner_name=bidder_exits.bidder

        return render(request, "auctions/closing.html", {
        "listing": set_close,
        "winner_name":winner_name
        })
    else:
        return HttpResponseRedirect(reverse("index"))
#lista de todos los articulos cerrados
@login_required
def closed_list(request):
    articles= Listing.objects.get(creator=request.user)
    a=Bid.objects.get(listing=articles)
    if(a is not None):
        
        winner_name=a.bidder

        return render(request, "auctions/closing.html", {
        "listing": articles,
        "winner_name":winner_name
        })
    else:
        return HttpResponseRedirect(reverse("index"))        

#mostrar los comentarios
def categories(request):
    categories = Listing.objects.filter(active=True).order_by("category").values_list("category", flat=True).distinct()
    categories = [category.capitalize() for category in categories if category is not None]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
def category_listings(request,category):
    #muestra solo las listas que pertenecen a la categoría específica

    return render(request, "auctions/index.html", {
        #"category": category,
        "listings": Listing.objects.filter(category=category.upper()).filter(active=True)#,
        #"page": "category"
    })
#  1) OFERTAS listing_id, bidder, timestamp, bid_price
@login_required
def add_comment(request, listing_id):
    #listing, comments, in_watchlist = listing_page_utility(request, listing_id)
    l=Listing.objects.get(id=listing_id)
    comments = Comment.objects.filter(listing=l)
    form = AddCommentForm(request.POST) #se crea el form

    if form.is_valid():
        content = form.cleaned_data["content"]
        comment = Comment(listing=l, commenter=request.user, content=content) #agrego un nuevo comentario
        comment.save() #guardo
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "comment_form": form #,
            
        })
@login_required
def get_watchlist(request):
    #aqui se va a mostrar todos los elementos que sigo
    
    w=watchlist.objects.all().filter(creator_list=request.user).values()
    #l=Listing.objects.get(w)
    items=[]
    for item in w.iterator():
       print(item['listing_id_id'])
       items.append(item['listing_id_id'])
    listing=Listing.objects.all().filter(id__in=items)
    #print("______",items)
    #print("lis   ",listing)
    return render(request, "auctions/index.html",{
        "listings":listing#,
        #"watchlist":w
    })

    if w is None:
        return HttpResponse("None")
    else:
        return HttpResponse("Hello, Brian!")
       
@login_required
def add_watchlist(request,listing_id): 
    #añade un documento a la watchlist o lo remueve si ya esta
    listing=Listing.objects.get(id=listing_id)
    added=watchlist.objects.filter(creator_list=request.user,listing_id=listing) #da true o false
    print("*******added",added)
    if added: #existe
        print("removido")
        added.delete()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:

        print("añadido")
        add = watchlist(creator_list=request.user, listing_id=listing)
        add.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
@login_required
def add_bid(request,listingid):
    current_bid = Listing.objects.get(id=listingid)
    current_bid=current_bid.price #obtenemos el precio
    print("precio actual",current_bid)
    if request.method == "POST":
        user_bid = float(request.POST.get("bid"))
        print("postulado",user_bid)
        if user_bid > current_bid:
            listing_items = Listing.objects.get(id=listingid)
            listing_items.price = user_bid #se intercambia el valor 
            listing_items.save()
            #comprobamos que no haya ofertado antes
            Bid_exist=Bid.objects.filter(listing=listing_items)   
            if Bid_exist:
                Bid_exist.bid_price=user_bid
                Bid_exist.bidder=request.user
                Bid.objects.filter(listing=listing_items).update(bidder=request.user,bid_price=user_bid)
                
            else:
                #guardamos en la lista de ofertas
                oferta=Bid(listing=listing_items, bidder=request.user,bid_price=user_bid)
                oferta.save()
                print("guardado oferta nueva")
            return listing(request,listingid)
        else:
            return HttpResponseRedirect(reverse("index")) #cambiar

@login_required
def winnings(request):
    #desactivamos el listing
    win = Bid.objects.filter(bidder=request.user)
    if(win is not None):

        return render(request, "auctions/winning.html", {
        "listing": win,
        "winner_name":win,
        "titulo":"My winnings"
        })
    else:
        return HttpResponseRedirect(reverse("index"))
        