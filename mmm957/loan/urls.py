from django.urls import path

from . import views

app_name = 'loan'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('register_borrower/', views.RegisterBorrowerView.as_view(), name='register_borrower'),
    path('register_lender/', views.RegisterLenderView.as_view(), name='register_lender'),
    path('send_verification/', views.sendVerification, name='send_verification'),
    path('verify/', views.VerifyView.as_view(), name='verify'),
    path('forgot/', views.ForgotView.as_view(), name='forgot'), #forgot傳電話時要用GET
    path('resetpassword/', views.ResetpasswordView.as_view(), name='resetpassword'),
    path('submit_ad/', views.SubmitAdView.as_view(), name='submit_ad'),
    path('ad_success/', views.AdSuccessView.as_view(), name='ad_success'),
    path('borrowing_message/', views.BorrowingMessageView.as_view(), name='borrowing_message'),
    path('borrowing_message_region/<str:region>/', views.BorrowingMessageRegionView.as_view(), name='borrowing_message_region'), #region需改成判斷幾個縣市合在一起
    path('borrowing_message_detail/<int:pk>/', views.BorrowingMessageDetailView.as_view(), name='borrowing_message_detail'),#雲端檔案上沒有
    path('ad/', views.AdView.as_view(), name='ad'),#雲端檔案上沒有
    path('ad_region/<str:region>/', views.AdRegionView.as_view(), name='ad_region'),
    path('lending_message/', views.LendingMessageView.as_view(), name='lending_message'),
    path('lending_message/<str:region>/', views.LendingMessageRegionView.as_view(), name='lending_message_region'),
    path('lending_message_detail/<int:pk>/', views.LendingMessageDetailView.as_view(), name='lending_message_detail'),#雲端檔案上沒有
    path('update_borrower/', views.UpdateBorrowerView.as_view(), name='update_borrower'),
    path('create_borrower_message/', views.CreateBorrowerMessageView.as_view(), name='create_borrower_message'),
    path('borrowing_history/', views.BorrowingHistoryView.as_view(), name='borrowing_history'),
    path('borrowing_completed/<int:id>/', views.BorrowingCompletedView.as_view(), name='borrowing_completed'),
    path('update_lender/', views.UpdateLenderView.as_view(), name='update_lender'),
    path('create_lender_message/', views.CreateLenderMessageView.as_view(), name='create_lender_message'),
    path('paying_history/', views.PayingHistoryView.as_view(), name='paying_history'),
    path('paying/', views.PayingView.as_view(), name='paying'), #未完成
    path('paying_success/', views.PayingSuccessView.as_view(), name='paying_success'),
    path('privacy_policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.logout, name='logout'),
    path('backend/', views.BackendView.as_view(), name='backend')  #backend待撰寫
]