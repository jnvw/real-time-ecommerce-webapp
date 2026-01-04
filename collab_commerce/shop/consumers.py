import json
from decimal import Decimal
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import render
from .models import Coupon, ShoppingGroup, CartItem, User
from .forms import CouponApplyForm

class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['secret_code']
        self.room_group_name = f'group_{self.room_name}'
        self.user = self.scope['user']

        if self.user.is_anonymous or not await self.is_member(self.user, self.room_name):
             await self.close()
             return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        message_content = text_data_json.get('message', '')

        if message_type == 'chat_message' and message_content:
            new_message = await self.save_chat_message(message_content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'message': new_message.message,
                    'user': new_message.user.username,
                    'timestamp': new_message.timestamp.strftime('%I:%M %p')
                }
            )
        elif message_type == 'get_cart':
            await self.send_cart_update()


    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_chat_message',
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp']
        }))
        
    async def cart_update(self, event):
        await self.send_cart_update()
        
        notification_message = event.get('notification_message')
        if notification_message:
            await self.send(text_data=json.dumps({
                'type': 'show_notification',
                'message': notification_message
            }))

    async def send_cart_update(self):
        cart_html = await self.get_rendered_cart()
        await self.send(text_data=json.dumps({
            'type': 'cart_update',
            'cart_html': cart_html
        }))

    @database_sync_to_async
    def is_member(self, user, secret_code):
        try:
            group = ShoppingGroup.objects.get(secret_code=secret_code)
            return user in group.members.all()
        except ShoppingGroup.DoesNotExist:
            return False

    @database_sync_to_async
    def save_chat_message(self, message):
        from .models import ChatMessage
        group = ShoppingGroup.objects.get(secret_code=self.room_name)
        return ChatMessage.objects.create(group=group, user=self.user, message=message)

    @database_sync_to_async
    def get_rendered_cart(self):
        group = ShoppingGroup.objects.get(secret_code=self.room_name)
        cart_items = group.shared_cart.items.all().select_related('product', 'added_by')
        total_price = group.shared_cart.get_total_price()
        
        coupon_id = self.scope['session'].get('coupon_id')
        discount_amount = Decimal('0')
        coupon_code = None
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                coupon_code = coupon.code
                discount = total_price * (Decimal(coupon.discount) / Decimal(100))
                total_price -= discount
                discount_amount = discount
            except Coupon.DoesNotExist:
                pass 
        
        html = f"""
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0">Cart Summary</h5>
                <h5 class="mb-0">Total: ${total_price:.2f}</h5>
            </div>
        """
        if discount_amount > 0:
             html += f"<p class='text-success'>Discount ({coupon_code}): -${discount_amount:.2f}</p>"
        
        if not cart_items:
            html += '<div class="text-center text-muted p-5">The cart is empty.</div>'
        else:
            html += '<ul class="list-group list-group-flush">'
            for item in cart_items:
                image_url = item.product.image.url if item.product.image else f"https://placehold.co/100x100/E1E1E1/444444?text={item.product.name.replace(' ', '+')}"
                html += f"""
                <li class="list-group-item d-flex align-items-center">
                    <img src="{image_url}" alt="{item.product.name}" class="rounded" style="width: 60px; height: 60px; object-fit: cover; margin-right: 15px;">
                    <div class="flex-grow-1">
                        <div class="fw-bold">{item.product.name}</div>
                        <small class="text-muted">Added by {item.added_by.username if item.added_by else 'a user'}</small>
                    </div>
                    <div class="d-flex align-items-center" style="min-width: 100px;">
                        <a href="/cart/update/{item.id}/decrease/" class="btn btn-outline-secondary btn-sm">-</a>
                        <span class="mx-2 fw-bold">{item.quantity}</span>
                        <a href="/cart/update/{item.id}/increase/" class="btn btn-outline-secondary btn-sm">+</a>
                    </div>
                    <a href="/cart/remove/{item.id}/" class="btn btn-outline-danger btn-sm ms-3" title="Remove item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                          <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                          <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                        </svg>
                    </a>
                </li>
                """
            html += '</ul>'
        
        csrf_token = self.scope['cookies'].get('csrftoken', '')
        
        html += f"""
        <form action="/coupons/apply/" method="post" class="mt-3">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <input type="hidden" name="secret_code" value="{self.room_name}">
            <div class="input-group">
                <input type="text" name="code" class="form-control" placeholder="Enter Coupon Code">
                <button type="submit" class="btn btn-secondary">Apply</button>
            </div>
        </form>
        """

        if cart_items:
            html += '<div class="d-grid gap-2 mt-3"><a href="/order/create/" class="btn btn-success">Proceed to Checkout</a></div>'

        return html
