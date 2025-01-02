# orders/payment.py
import midtransclient
from django.conf import settings
import time

class MidtransPaymentGateway:
    def __init__(self):
        self.snap = midtransclient.Snap(
            is_production=False,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )

 
    def generate_payment_token(self, order):
        try:
            # Generate unique order ID using timestamp
            unique_order_id = f"ORDER-{order.id}-{int(time.time())}"
            
            items = [{
                "id": str(item.menu_item.id),
                "price": int(float(item.price)),
                "quantity": int(item.quantity),
                "name": str(item.menu_item.name)
            } for item in order.orderitem_set.all()]
            
            items.append({
                "id": "service-fee",
                "price": 2000,
                "quantity": 1,
                "name": "Biaya Layanan"
            })

            param = {
                "transaction_details": {
                    "order_id": unique_order_id,
                    "gross_amount": int(float(order.total_amount))
                },
                "customer_details": {
                    "first_name": str(order.user.username),
                    "email": str(order.user.email) if order.user.email else None
                },
                "item_details": items,
                "enabled_payments": [
                    "credit_card", "gopay", "shopeepay", 
                    "bca_va", "bni_va", "bri_va"
                ]
            }

            transaction = self.snap.create_transaction(param)
            return {
                'token': transaction['token'],
                'redirect_url': transaction['redirect_url']
            }
        except Exception as e:
            print(f"Midtrans Error: {str(e)}")
            return None