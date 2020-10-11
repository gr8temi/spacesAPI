from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from spaces.views import notfound
from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from .views.auth import login
from .views.add_space import CreateSpace
from .views.space import Spaces, SingleSpace, EditSpace, DeleteSpace
from .views.reservation import ReservationDetail, PlaceReservation, ReservationList, RequestReservationExtension, PreviousReservationPerUser, UpcomingReservationPerUser
from .views.booking import BookingStatus, BookingView, BookingList, BookingCancellation, BookingCancellationActions, UpdateReferenceCode, PreviousBookingPerUser, UpcomingBookingPerUser
from .views import agent, customer
from .views import space_category, space_type, favourite
from .views.auth import login, forgot_password, reset_password, verify_email
from .views.subscription import Subscribe, SubscribeActions, UpdateRecurring
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


urlpatterns = [

    # register other routes here ...
    path('v1/request-reservation-extension/',
         RequestReservationExtension.as_view(), name="request_extension"),
    path('v1/reservation/', PlaceReservation.as_view(), name="reservation"),
    path('v1/all-reservations/', ReservationList.as_view(), name="all_reservations"),
    path('v1/single-reservation/<slug:reservation_id>/',
         ReservationDetail.as_view(), name="single_reservation"),
    path('v1/reservation/previous-reservation/<slug:user_id>/',
         PreviousReservationPerUser.as_view(), name="previous_reservation"),
    path('v1/reservation/upcoming-reservation/<slug:user_id>/',
         UpcomingReservationPerUser.as_view(), name="upcoming_reservation"),

    path('v1/booking/', BookingView.as_view(), name="booking"),
    path('v1/all-bookings/', BookingList.as_view(), name="all_bookings"),
    path('v1/booking/status/<slug:order_code>/',
         BookingStatus.as_view(), name='booking_status'),
    path('v1/booking-cancellation/', BookingCancellation.as_view(),
         name="booking_cancellation"),
    path('v1/booking-cancellation/<slug:cancellation_id>/',
         BookingCancellationActions.as_view(), name="booking_cancellation_actions"),
    path('v1/booking/update/<slug:order_code>/',
         UpdateReferenceCode.as_view(), name="update_reference"),
    path('v1/booking/previous-booking/<slug:user_id>/',
         PreviousBookingPerUser.as_view(), name="previous_booking"),
    path('v1/booking/upcoming-booking/<slug:user_id>/',
         UpcomingBookingPerUser.as_view(), name="upcoming_booking"),

    path('v1/favourites/', favourite.AddFavorite.as_view(), name="favourites"),
    path('v1/favourite/delete/<slug:favorite_id>/',
         favourite.DeleteFavourite.as_view(), name="delete_favourite"),
    path('v1/favourite/<slug:user_id>/',
         favourite.FetchUserFavourites.as_view(), name="favourite"),

    path('v1/space/<slug:space_id>/', SingleSpace.as_view(), name='single_space'),
    path('v1/space/edit/<slug:space_id>/',
         EditSpace.as_view(), name='edit_space'),
    path('v1/space/delete/<slug:space_id>/',
         DeleteSpace.as_view(), name='delete_space'),
    path('v1/spaces/', CreateSpace.as_view(), name="space"),
    path('v1/all-spaces/', cache_page(CACHE_TTL)
         (Spaces.as_view()), name="spaces"),

    path('v1/categories/', cache_page(CACHE_TTL)
         (space_category.SpacesCategory.as_view()), name="categories"),
    path('v1/space-type/', cache_page(CACHE_TTL)
         (space_type.SpaceTypeView.as_view()), name="space_type"),
    path('v1/space-type/<slug:space_type_id>/', cache_page(CACHE_TTL)
         (space_type.SpaceTypeDetail.as_view()), name="space_type_detail"),
    path('v1/space-type-category/<slug:category_id>/', cache_page(CACHE_TTL)
         (space_type.SpaceTypeByCategory.as_view()), name="space_type_by_category"),

    # match route that has not been registered above
    path('v1/auth/login/', login.UserLogin.as_view(), name='login'),
    
    path('v1/auth/agents/signup/',
         agent.AgentRegister.as_view(), name='agent_register'),
    path('v1/agents/', agent.AgentList.as_view(), name='agents'),
    path('v1/auth/agent/<uuid:agent_id>/',
         agent.AgentDetail.as_view(), name='agent_details'),
    
    path('v1/auth/customers/signup/',
         customer.CustomerRegister.as_view(), name='customer_register'),
    path('v1/customers/', customer.CustomerList.as_view(), name='customers'),
    path('v1/auth/customer/<uuid:customer_id>/',
         customer.CustomerDetail.as_view(), name='customer_details'),
    path('v1/customer/email/<email>/', customer.FetchByEmail.as_view(), name="customer_by_email"),
    path('v1/customer/phone_number/<slug:phone_number>/', customer.FetchByPhoneNumber.as_view(), name="customer_by_phone_number"),
    path('v1/auth/verify-email/',
         verify_email.VerifyEmail.as_view(), name="verify-email"),
    path('v1/auth/forgot-password/',
         forgot_password.ForgotPassword.as_view(), name="forgot-password"),
    path('v1/auth/reset-password/',
         reset_password.ResetPassword.as_view(), name='reset-password'),

    # Subscription
    path("v1/subscribe/", Subscribe.as_view(), name='subscribe'),
    path("v1/subscription/complete/<slug:reference_code>/",
         SubscribeActions.as_view(), name="complete_subscriptions"),
    path("v1/subscription/update-recurring/<slug:reference_code>/",
         UpdateRecurring.as_view(), name="update-subscription-recurring")

]
