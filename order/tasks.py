# order/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from django.template.loader import render_to_string


@shared_task
def send_order_notifications_task(order_id):
    """
    Sends email notifications to the customer and vendor for a new order.
    """
    try:
        order = Order.objects.select_related("user", "vendor__user", "product").get(
            id=order_id
        )
    except Order.DoesNotExist:
        return f"Order with ID {order_id} not found. Cannot send notifications."

    customer = order.user
    vendor = order.vendor
    product = order.product

    # --- Notification to Vendor ---
    vendor_subject = f"New Order Request for {product.name}!"
    vendor_message = f"""
    Hello {vendor.company_name},

    You have received a new order request from customer {customer.first_name} {customer.last_name}.

    Product: {product.name}
    Quantity: {order.quantity}

    Customer Contact Information:
    Email: {customer.email}
    Phone: {customer.phone_number}

    Please log in to your vendor dashboard to review and confirm this order.

    Thank you,
    The PCRS Team
    """
    send_mail(
        vendor_subject,
        vendor_message,
        settings.DEFAULT_FROM_EMAIL,
        [vendor.user.email],
        fail_silently=False,
    )

    # --- Notification to Customer ---
    customer_subject = f"Your Order Request for {product.name} has been placed!"
    customer_message = f"""
    Hello {customer.first_name},

    Your order request has been sent to the vendor.

    Product: {product.name}
    Quantity: {order.quantity}
    Price per item: TSh {product.price:,.2f}
    Total: TSh {(product.price * order.quantity):,.2f}

    Vendor Contact Information:
    Company: {vendor.company_name}
    Location: {vendor.location}
    Phone: {vendor.user.phone_number}

    The vendor will contact you shortly to confirm the order and arrange payment and collection/delivery.

    Thank you for using PCRS,
    The PCRS Team
    """
    send_mail(
        customer_subject,
        customer_message,
        settings.DEFAULT_FROM_EMAIL,
        [customer.email],
        fail_silently=False,
    )

    # --- TODO: SMS Notification Logic ---
    # Here you would integrate with an SMS gateway like Twilio or another provider.
    # from your_sms_service import send_sms
    # vendor_sms_message = f"PCRS: New order for {product.name} from {customer.first_name}. Check your email or dashboard for details."
    # try:
    #     send_sms(to=vendor.user.phone_number, message=vendor_sms_message)
    # except Exception as e:
    #     print(f"Failed to send SMS to vendor {vendor.user.phone_number}: {e}")

    return f"Notifications sent successfully for Order ID {order_id}."
