"""
Payment controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import numbers
import requests
from commands.write_payment import create_payment, update_status_to_paid
from queries.read_payment import get_payment_by_id

def get_payment(payment_id):
    return get_payment_by_id(payment_id)

def add_payment(request):
    """ Add payment based on given params """
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    order_id = payload.get('order_id')
    total_amount = payload.get('total_amount')
    result = create_payment(order_id, user_id, total_amount)
    if isinstance(result, numbers.Number):
        return {"payment_id": result}
    else:
        return {"error": str(result)}
    
def process_payment(payment_id, credit_card_data):
    """ Process payment with given ID, notify store_manager sytem that the order is paid """
    # S'il s'agissait d'une véritable API de paiement, nous enverrions les données de la carte de crédit à un payment gateway (ex. Stripe, Paypal) pour effectuer le paiement. Cela pourrait se trouver dans un microservice distinct.
    _process_credit_card_payment(credit_card_data)

    # Si le paiement est réussi, mettre à jour les statut de la commande
    # Ensuite, faire la mise à jour de la commande dans le Store Manager (en utilisant l'order_id)
    update_result = update_status_to_paid(payment_id)
    result_order_id = update_result['order_id']
    result_payment_id = update_result["payment_id"]
    result_is_paid = update_result["is_paid"]
    
    result = {
        "order_id": result_order_id,
        "payment_id": result_payment_id,
        "is_paid": result_is_paid
    }
    
    print(f"Updated order {result_order_id} to paid={update_result}")
    
    response = requests.put(
        "http://api-gateway:8080/store-api/orders",
        json={
            "order_id": result_order_id,
            "is_paid": True
        },
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.ok:
        print(f"Commande {result_order_id} mise à jour avec succès (is_paid=True)")
    else:
        print(f"Erreur lors de la mise à jour de la commande {result_order_id}: {response.status_code} - {response.text}")

    return result
    
def _process_credit_card_payment(payment_data):
    """ Placeholder method for simulated credit card payment """
    print(payment_data.get('cardNumber'))
    print(payment_data.get('cardCode'))
    print(payment_data.get('expirationDate'))