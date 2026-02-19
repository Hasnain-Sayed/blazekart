from django.urls import path
from . import views

urlpatterns=[
    path('',views.store,name='store'),
    path('category/<slug:slug>/',views.store,name='prods_by_category'),
    path('category/<slug:slug>/<slug:prod_slug>/',views.product_details,name='product_details'),
    path('search/',views.search,name='search'),
    path('review/add/<int:product_id>/',views.add_review,name='add_review'),
    path('review/delete/<int:product_id>/',views.delete_review,name='delete_review'),
    path('review/react/',views.review_react,name='review_react'),
    path('reviews/load-more/', views.load_more_reviews, name='load_more_reviews'),

]