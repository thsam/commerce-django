from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("add_comment/<str:listing_id>",views.add_comment, name="add_comment"),
    path("watchlist",views.get_watchlist, name="get_watchlist"),
    path("add_watchlist/<str:listing_id>",views.add_watchlist, name="add_watchlist"),
    path("categories",views.categories,name="categories"),
    path("category_listings/<str:category>",views.category_listings,name="category_listings"),
    path("close_listing/<str:listing_id>",views.close_listing,name="close_listing"),
    path("add_bid/<int:listingid>", views.add_bid, name="add_bid"),
    path("winnings", views.winnings, name="winnings"),


]
