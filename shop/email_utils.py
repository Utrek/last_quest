import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from typing import Optional, List
from .models import Order, User

class EmailThread(threading.Thread):
    """
    Класс для асинхронной отправки email
    """
    def __init__(self, subject: str, text_content: str, from_email: str, 
                 recipient_list: List[str], html_content: Optional[str] = None):
        self.subject = subject
        self.text_content = text_content
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(
            self.subject, self.text_content, self.from_email, self.recipient_list
        )
        if self.html_content:
            msg.attach_alternative(self.html_content, "text/html")
        try:
            msg.send()
        except Exception as e:
            print(f"Ошибка при отправке email: {str(e)}")

def send_async_email(subject: str, text_content: str, from_email: str, 
                  recipient_list: List[str], html_content: Optional[str] = None) -> None:
    """
    Отправляет email асинхронно
    """
    EmailThread(subject, text_content, from_email, recipient_list, html_content).start()

def send_order_confirmation_email(order: Order) -> bool:
    """
    Отправляет email с подтверждением заказа (синхронно)
    
    Args:
        order: объект Order
        
    Returns:
        bool: True если email отправлен успешно, иначе False
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

def send_order_confirmation_email_async(order: Order) -> bool:
    """
    Асинхронно отправляет email с подтверждением заказа через Celery
    
    Args:
        order: объект Order
        
    Returns:
        bool: True если задача запущена успешно, иначе False
    """
    from .tasks import send_order_confirmation_email
    
    # Запускаем задачу Celery
    send_order_confirmation_email.delay(order.id)
    return True

def send_registration_confirmation_email(user: User) -> bool:
    """
    Отправляет email с подтверждением регистрации (синхронно)
    
    Args:
        user: объект User
        
    Returns:
        bool: True если email отправлен успешно, иначе False
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

def send_registration_confirmation_email_async(user: User) -> bool:
    """
    Асинхронно отправляет email с подтверждением регистрации
    
    Args:
        user: объект User
        
    Returns:
        bool: True если email отправлен успешно, иначе False
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
    
    # Отправляем асинхронно
    send_async_email(subject, text_content, from_email, [to_email], html_content)
    return True

def send_supplier_order_notification_async(order: Order) -> bool:
    """
    Асинхронно отправляет уведомление поставщикам о новом заказе через Celery
    
    Args:
        order: объект Order
        
    Returns:
        bool: True если задача запущена успешно, иначе False
    """
    from .tasks import send_supplier_order_notification
    
    # Запускаем задачу Celery
    send_supplier_order_notification.delay(order.id)
    return True