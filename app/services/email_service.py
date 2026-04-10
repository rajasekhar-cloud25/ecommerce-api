"""
Email service — currently logs to console.
Swap the `send_email` function to use Resend/Gmail/SES later
without changing any callers.
"""


def send_email(to: str, subject: str, body: str):
    """
    Send an email. Currently logs to console.
    To use a real provider later, replace this function's implementation.
    """
    print("\n" + "=" * 60)
    print(f"📧 EMAIL")
    print(f"To:      {to}")
    print(f"Subject: {subject}")
    print("-" * 60)
    print(body)
    print("=" * 60 + "\n")


# ===== Pre-built email templates =====

def send_welcome_email(to: str, name: str):
    subject = "Welcome to Raj Store!"
    body = f"""
Hi {name},

Thanks for creating an account at Raj Store! We're excited to have you.

Start browsing our catalog of 60+ products and find something you love.

Happy shopping,
The Raj Store Team
    """.strip()
    send_email(to, subject, body)


def send_order_confirmation_email(to: str, name: str, order_number: str, total: float, items: list):
    items_lines = "\n".join([
        f"  - {item.product.title} x {item.quantity} — ${item.price * item.quantity:.2f}"
        for item in items
    ])

    subject = f"Order Confirmation — {order_number}"
    body = f"""
Hi {name},

Thank you for your order! We've received your payment and your order is being processed.

Order: {order_number}
---------------
{items_lines}

Total: ${total:.2f}

We'll email you again when your order ships.

Thanks for shopping with us,
The Raj Store Team
    """.strip()
    send_email(to, subject, body)


def send_order_status_email(to: str, name: str, order_number: str, new_status: str):
    subject = f"{order_number} — Status Update"

    status_messages = {
        "confirmed": "Your order has been confirmed and is being prepared.",
        "shipped":   "Your order has shipped! 🚚 It's on its way to you.",
        "delivered": "Your order has been delivered. 🎉 We hope you love it!",
        "cancelled": "Your order has been cancelled.",
        "refunded":  "Your refund has been processed and will appear in your account within 5-10 business days.",
    }

    message = status_messages.get(new_status, f"Your order status has been updated to: {new_status}")

    body = f"""
Hi {name},

{message}

Order: {order_number} — Current status: {new_status.upper()}

Thanks,
The Raj Store Team
    """.strip()
    send_email(to, subject, body)