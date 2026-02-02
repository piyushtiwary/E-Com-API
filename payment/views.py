import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backends.async_send_mail import send_email_async
from backends.permission import IsAdminOrReadOnly
from order.models import Order

from .models import Payment
from .permission import IsAuthorizedAndPaymentNotComplete
from .serializer import ReadPaymentSerializer, WritePaymentSerializer

logger = logging.getLogger(__name__)

# Only import stripe if enabled
if settings.STRIPE_ENABLED:
    import stripe


class PaymentViewset(ModelViewSet):
    """A viewset for Payment model"""

    http_method_names = ["get", "patch", "delete"]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Overriding to return user specific order"""
        if self.request.user.is_staff:
            return Payment.objects.select_related("order").all()
        return Payment.objects.select_related("order").filter(
            order__user=self.request.user
        )

    def get_serializer_class(self):
        """Overriding to return serializer class based on HTTP method"""
        if self.request.method == "PATCH":
            return WritePaymentSerializer
        return ReadPaymentSerializer


# Configure Stripe only if enabled
if settings.STRIPE_ENABLED:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateStripeCheckoutSession(APIView):
    """
    Create and return checkout session ID for order payment of type 'Stripe'
    """

    permission_classes = [IsAuthenticated, IsAuthorizedAndPaymentNotComplete]

    def post(self, request, *args, **kwargs):
        if not settings.STRIPE_ENABLED:
            logger.warning("Stripe is not configured. Please add Stripe API keys.")
            return Response(
                {"error": "Stripe payment is not configured. Please configure Stripe API keys."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        order_items = []
        for item in order.items.all():
            product = item.product
            quantity = item.quantity
            data = {
                "price_data": {
                    "currency": "usd",
                    "unit_amount_decimal": product.price,
                    "product_data": {
                        "name": product.name,
                        "description": product.description,
                    },
                },
                "quantity": quantity,
            }
            order_items.append(data)

        logger.info("Creating Stripe Session")
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=order_items,
                metadata={"order_id": order.id},
                mode="payment",
                success_url=settings.PAYMENT_SUCCESS_URL,
                cancel_url=settings.PAYMENT_CANCEL_URL,
            )
        except Exception as e:
            logger.error(f"Stripe Error while creating checkout {e}")
            return Response(
                {"error": f"Failed to create checkout session: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"sessionId": checkout_session["id"], "url": checkout_session["url"]},
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    permission_classes = [IsAuthenticated, IsAuthorizedAndPaymentNotComplete]

    def post(self, request, format=None):
        if not settings.STRIPE_ENABLED:
            logger.warning("Stripe webhook received but Stripe is not configured.")
            return HttpResponse(status=503)

        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        if not sig_header:
            logger.warning("Stripe webhook missing signature header")
            return HttpResponse(status=400)

        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            logger.error(f"Error in stripe webhook while constructing event {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Error in stripe webhook while constructing event {e}")
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            logger.info("Payment successful")
            session = event["data"]["object"]

            customer_email = session["customer_details"]["email"]
            order_id = session["metadata"]["order_id"]

            payment = Payment.objects.get(pk=order_id)
            payment.status = "C"
            payment.save()

            send_email_async.delay(
                to_email=customer_email,
                subject="Thank you for purchasing",
                message=f"Your order {order_id} have been placed",
                from_email="ecom89@gmail.com",
            )

        return HttpResponse(status=200)