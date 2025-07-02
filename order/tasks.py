# order/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from django.template.loader import render_to_string


@shared_task
def send_order_notifications_task(order_id):
    """
    Sends email notifications to the customer and vendor for a new order using Django templates.
    """
    try:
        order = Order.objects.select_related("user", "vendor__user", "product").get(
            id=order_id
        )
    except Order.DoesNotExist:
        print(f"Order with ID {order_id} not found. Cannot send notifications.")
        return

    # Prepare a context dictionary for the templates
    context = {
        "order": order,
        "customer": order.user,
        "vendor": order.vendor,
        "product": order.product,
        "product_price": order.product.price,
        "total_price": order.product.price * order.quantity,
        "vendor_phone": order.vendor.user.phone_number,
    }

    try:
        # --- Notification to Vendor ---
        vendor_subject = f"New Order Request for {order.product.name}!"
        # Use render_to_string to load the template with the context
        vendor_message = render_to_string("order/vendor_notification.txt", context)
        send_mail(
            vendor_subject,
            vendor_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.vendor.user.email],
            fail_silently=False,
        )
        print(f"Vendor notification sent for Order ID {order_id}.")

        # --- Notification to Customer ---
        customer_subject = (
            f"Your Order Request for {order.product.name} has been placed!"
        )
        customer_message = render_to_string("order/customer_notification.txt", context)
        send_mail(
            customer_subject,
            customer_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
        print(f"Customer notification sent for Order ID {order_id}.")

    except Exception as e:
        # If sending mail fails, log the error but don't crash the task
        print(
            f"CRITICAL: Failed to send email notifications for Order ID {order_id}. Error: {e}"
        )
        # Optionally, you can re-raise the exception to have Celery retry the task
        # raise self.retry(exc=e, countdown=60)
        return f"Failed to send notifications for Order ID {order_id}."

    # --- TODO: SMS Notification Logic ---
    # Here you would integrate with an SMS gateway like Twilio or another provider.
    # from your_sms_service import send_sms
    # vendor_sms_message = f"PCRS: New order for {product.name} from {customer.first_name}. Check your email or dashboard for details."
    # try:
    #     send_sms(to=vendor.user.phone_number, message=vendor_sms_message)
    # except Exception as e:
    #     print(f"Failed to send SMS to vendor {vendor.user.phone_number}: {e}")

    return f"Notifications sent successfully for Order ID {order_id}."
