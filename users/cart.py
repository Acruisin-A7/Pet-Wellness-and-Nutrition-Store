from decimal import Decimal
from django.conf import settings
from users.models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart session."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Add or update a product in the cart."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Mark the session as modified to ensure it saves."""
        self.session.modified = True

    def __iter__(self):
        """Iterate through the cart items and retrieve product details."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(product.id): product for product in products}  # Map products by ID

        for product_id, item in self.cart.items():
            product = product_dict.get(product_id)
            if product:
                yield {
                    'product_id': product.id,  # Store ID explicitly
                    'name': product.name,  
                    'quantity': item['quantity'],  
                    'price': float(item['price']),  
                    'total_price': float(item['price']) * item['quantity'],
                    'image_url': product.image.url if product.image else None,
                }


    
    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate total cost of items in cart."""
        return float(sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values()))

    def clear(self):
        """Remove all items from the cart."""
        del self.session[settings.CART_SESSION_ID]
        self.save()
