from django.core.mail import send_mail
from django.conf import settings

def send_password_email(user_email, password, first_name, last_name):
    """Send an email with the temporary password to a new user."""
    subject = "Your WinasSacco Account Password"
    message = f"""
Hello {first_name} {last_name},

Your WinasSacco account has been created. Please use the following credentials to login:

Email: {user_email}
Password: {password}

Please change your password after your first login for security reasons.

Best regards,
WinasSacco Team
"""
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    try:
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False
        )
        return sent > 0
    except Exception as e:
        print(f"Error sending email to {user_email}: {str(e)}")
        return False