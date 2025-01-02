# orders/payment.py
import midtransclient
from django.conf import settings

class MidtransPaymentGateway:
    def __init__(self):
        self.snap = midtransclient.Snap(
            is_production=False,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )

    def generate_payment_token(self, order):
        # Calculate items total
        items = [{
            "id": str(item.menu_item.id),
            "price": int(item.price),
            "quantity": item.quantity,
            "name": item.menu_item.name
        } for item in order.orderitem_set.all()]
        
        # Add service fee as an item
        items.append({
            "id": "service-fee",
            "price": 2000,
            "quantity": 1,
            "name": "Biaya Layanan"
        })

        # Calculate delivery fee if applicable
        if "Diantar" in order.note:
            items.append({
                "id": "delivery-fee",
                "price": 10000,
                "quantity": 1,
                "name": "Biaya Pengiriman"
            })

        param = {
            "transaction_details": {
                "order_id": f"ORDER-{order.id}",
                "gross_amount": int(order.total_amount)
            },
            "customer_details": {
                "first_name": order.user.username,
                "email": order.user.email
            },
            "item_details": items,
            "enabled_payments": [
                "credit_card", "gopay", "shopeepay", 
                "bca_va", "bni_va", "bri_va"
            ]
        }

        try:
            transaction = self.snap.create_transaction(param)
            return {
                'token': transaction['token'],
                'redirect_url': transaction['redirect_url']
            }
        except Exception as e:
            print(f"Midtrans Error: {str(e)}")
            return None