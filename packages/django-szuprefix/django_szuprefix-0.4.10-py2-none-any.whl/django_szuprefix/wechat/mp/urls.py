from django.conf.urls import url
import views
from .decorators import weixin_login_required

app_name = "wechat_mp"
urlpatterns = [
    url(r'^ports/', views.ports),
    url(r'^login/$', weixin_login_required(views.LoginView.as_view()), name="login"),
    url(r'^qr_login/(?P<task_id>[\w-]+)/$', weixin_login_required(views.QRLoginView.as_view()), name="qr-login"),
    url(r'^test_pay/$', weixin_login_required(views.TestPayView.as_view()), name="test_pay"),
]
