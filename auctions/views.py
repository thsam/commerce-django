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
    #listing, comments, in_watchlist = listing_page_utility(request, listing_id)
    #muestra el listing específico
    l=Listing.objects.get(id=listing_id) #aquí debo filtrar y colocar la última oferta más alta
    if request.user.is_authenticated:
        w=watchlist.objects.all().filter(creator_list=request.user).count()
        added=watchlist.objects.filter(creator_list=request.user,listing_id=listing_id) #da true o false
        #creadorl=Listing.objects.filter(creator=request.user,listing_id=listing_id)
        #print("\n CREADOR, ",creadorl,l.creator) 
        if request.user == l.creator:
            creadorl=True
        else:
            creadorl=False
        #print("watchlist")
    else:
        w=False
        added=False
        creadorl=False
    print(w)
    #datos = User.objects.all().values()
    #print(datos)
    #proceso para saber si la lista ha sido añadida o no
    #added=watchlist.objects.filter(creator_list=request.user,listing_id=listing_id) #da true o false
    #proceso para cerrar un listing 
    #1) similar al proceso de añadir a watchlist, preguntamos si el es el creador del listing
    #creadorl=Listing.objects.filter(creator=request.user) 


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
    #desactivamos el listing
    #return HttpResponse("Hello, Brian!")
    set_close = Listing.objects.get(creator=request.user,id=listing_id)
    set_close.active=False
    set_close.save()
    print("**** se ha desactivado")
    #una vez desactivado, hay que redirigir a la ventana
    product=set_close.title
    creador=set_close.creator
    pricef=set_close.price
    categoria=set_close.category
    if(Bid.objects.get(id=listing_id) is not None):
        winner=Bid.objects.get(id=listing_id)
        winner_name=winner.bidder

        return render(request, "auctions/listing.html", {
        "listing": l,
        "comments":Comment.objects.filter(listing=l),
        "comment_form": AddCommentForm(),
        "watchlist": w,
        "added": added,
        "creador":creadorl
    })
    
    pass
        

    

    #oferta=Bid(listing=listing_items, bidder=request.user,bid_price=user_bid)
    #return HttpResponseRedirect(reverse("index"))
#mostrar los comentarios
def categories(request):
    categories = Listing.objects.filter(active=True).order_by("category").values_list("category", flat=True).distinct()
    categories = [category.capitalize() for category in categories if category is not None]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
def category_listings(request,category):
    #muestra solo las listas que pertenecen a la categoría específica

    #return HttpResponse("Hello, Brian!")

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
            #"bid_form": NewBidForm(),
            #"in_watchlist": in_watchlist
        })
@login_required
def get_watchlist(request):
    #aqui se va a mostrar todos los elementos que sigo
    #listing=Listing.objects.get(id=listing_id)
    """if request.user.is_authenticated:
        in_watchlist = request.user.watchlist.all()
        print(in_watchlist)
    else:
        in_watchlist = False
    return render(request,"auctions/watchlist.html",{
        "watchlist": in_watchlist
        })"""
    w=watchlist.objects.all().filter(creator_list=request.user).values()
    print("holi",w)
    #l=Listing.objects.get(w)
    items=[]
    for item in w.iterator():
       print(item['listing_id_id'])
       items.append(item['listing_id_id'])
    listing=Listing.objects.all().filter(id__in=items)
    print("______",items)
    print("lis   ",listing)
    #listing =Listing.objects.filter(id=items)
    return render(request, "auctions/index.html",{
        "listings":listing#,
        #"watchlist":w
    })

    #datos = User.objects.all().values()
    

    if w is None:
        return HttpResponse("None")
    else:
        return HttpResponse("Hello, Brian!")
    #listing =Listing.objects.all()
    
    
@login_required
def add_watchlist(request,listing_id): 
    #añade un documento a la watchlist o lo remueve si ya esta
    #listing, _, in_watchlist = listing_page_utility(request, listing_id)
    listing=Listing.objects.get(id=listing_id)
    #p
    #add = watchlist(creator_list=request.user, listing_id=listing_id)
    added=watchlist.objects.filter(creator_list=request.user,listing_id=listing) #da true o false
    print("*******added",added)
    if added: #existe
        print("removido")
        added.delete()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        #return get_watchlist(request)
    else:

        print("añadido")
        add = watchlist(creator_list=request.user, listing_id=listing)
        add.save()
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        #return get_watchlist(request)
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
            #guardamos en la lista de ofertas
            oferta=Bid(listing=listing_items, bidder=request.user,bid_price=user_bid)
            oferta.save()
            print("guardado oferta")
            return listing(request,listingid)
        else:
            return HttpResponseRedirect(reverse("index")) #cambiar
    """ if request.method == "POST":
        user_bid = int(request.POST.get("bid"))
        if user_bid > current_bid:
            listing_items = Listing.objects.get(id=listingid)
            listing_items.price = user_bid
            listing_items.save()
            try:
                if Bid.objects.filter(id=listingid):
                    bidrow = Bid.objects.filter(id=listingid)
                    bidrow.delete()
                bidtable = Bid()
                bidtable.user=request.user.username
                bidtable.title = listing_items.title
                bidtable.listingid = listingid
                bidtable.bid = us """
    #pass
@login_required
def winnings(request,listingid):

    pass
    """if request.user.is_authenticated:
        in_watchlist = listing in request.user.watchlist.all()
    else:
        in_watchlist = False

    if in_watchlist:
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)

    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))"""
    