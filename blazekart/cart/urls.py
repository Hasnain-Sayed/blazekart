from django.urls import path
from . import views

urlpatterns=[
    path('cart/',views.cart,name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_cart_item,name='remove_cart_item'),
    path('reduce_cart_item/<int:product_id>/<int:cart_item_id>/',views.reduce_cart_item,name="reduce_cart_item"),
    path('update_cart/<int:product_id>/<int:cart_item_id>/',views.update_cart,name="update_cart"),

    path('handle_product_action/<int:product_id>/',views.handle_product_action,name='handle_product_action'),
    path('add_to_wishlist/<int:product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_wishlist_item/<int:product_id>/',views.remove_wishlist_item,name='remove_wishlist_item'),
    path('move_to_wishlist/<int:product_id>/<int:item_id>/', views.move_to_wishlist, name='move_to_wishlist'),
    path('move_to_cart/<int:product_id>/<int:item_id>/', views.move_to_cart, name='move_to_cart'),

]