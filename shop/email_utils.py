from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_confirmation_email(order):
    """
    Отправляет email с подтверждением заказа
    
    Args:
        order: объект Order
    """
    # Проверяем, что у пользователя есть email
    if not order.user.email:
        return False
    
    # Подготавливаем контекст для шаблона
    context = {
        'order': order
    }
    
    # Рендерим HTML и текстовую версии письма
    html_content = render_to_string('email/order_confirmation.html', context)
    text_content = render_to_string('email/order_confirmation.txt', context)
    
    # Создаем email
    subject = f'Подтверждение заказа #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.user.email
    
    # Создаем и отправляем сообщение
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")
        return False
        
def send_registration_confirmation_email(user):
    """
    Отправляет email с подтверждением регистрации
    
    Args:
        user: объект User
    """
    # Проверяем, что у пользователя есть email
    if not user.email:
        return False
    
    # Подготавливаем контекст для шаблона
    context = {
        'user': user
    }
    
    # Рендерим HTML и текстовую версии письма
    html_content = render_to_string('email/registration_confirmation.html', context)
    text_content = render_to_string('email/registration_confirmation.txt', context)
    
    # Создаем email
    subject = 'Подтверждение регистрации'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    # Создаем и отправляем сообщение
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")
        return False