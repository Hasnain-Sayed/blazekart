from django.urls import path
from . import views

urlpatterns=[
    path('user_dashboard/',views.dashboard,name='dashboard'),
    path('profile/',views.profile,name='profile'),
    path('enable_two_factor_authentication/',views.enable_2fa,name='enable_2fa'),

    path('cart/',views.dbcart,name='dbcart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_dbcart,name='remove_dbcart',),
    path('wishlist/',views.dbwishlist,name='dbwishlist'),
    path('remove_wishlist_item/<int:product_id>/',views.remove_dbwishlist,name='remove_dbwishlist'),
    path('move_to_cart/<int:product_id>/<item_id>/',views.move_to_dbcart,name='move_to_dbcart'),

    path('recent_orders/',views.recent_orders,name='recent_orders'),
    path('order_details/<int:order_num>/',views.order_details,name='order_details'),
    path('invoice/<str:order_number>/',views.download_invoice,name='download_invoice'),
    path('change-order-address/<int:order_number>/',views.change_order_address,name='change_order_address'),
    path('Cancel/<int:order_number>/',views.cancel_order,name='cancel_order'),

    path('Payment_methods',views.payments_methods,name='payments_methods'),

    path('help_and_support/',views.help_support,name='help_support'),
    path('logout/',views.logout,name='logout'),
]