
from django.urls import path
from ecom_app import views
from django.conf.urls.static import static
from ecom import settings


urlpatterns = [
    path('', views.home),   
    path('about',views.about),   
    path('edit/<rid>', views.edit),
    path('delete/<x1>/<x2>', views.delete),
    path('myview', views.SimpleView.as_view()),
    path('pdetails/<pid>', views.product_details),
    path('register', views.register),
    path('login', views.user_login),
    path('logout', views.user_logout),
    path('catfilter/<cv>', views.catfilter),
    path('sort/<sv>', views.sort),
    path('range', views.range),
    path('addtocart/<pid>', views.addtocart),
    path('viewcart', views.viewcart),
    path('remove/<cid>', views.remove),
    path('updateqty/<qv>/<cid>', views.updateqty),
    path('placeorder', views.placeorder),
    path('makepayment', views.makepayment),
    path('sendmail/<uemail>', views.sendusermail),
    path('search', views.search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
