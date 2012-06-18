"""
Session based shopping cart
"""
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from .utils import import_cart

class CartItem(object):
    """
    Lightweight container for cart items
    """
    __slots__ = ('item', 'quantity',)

    def __init__(self, item, quantity):
        self.item = item
        self.quantity = quantity and quantity or 0

    def __repr__(self):
        return 'CartItem(%r, %r)' % (self.item, self.quantity)

    def __cmp__(self, other):
        if isinstance(other, CartItem):
            return cmp(self.item, other.item)
        return cmp(self.item, other)

class Cart(list):
    """
    Handles a list of items stored in the session
    """
    model = None

    def __init__(self, request, name='cart'):
        super(Cart, self).__init__()
        self.request = request
        self.name = name
        if self.model is None:
            from django.db import models
            try:
                Cart.model = import_cart(settings.CART_MODEL)
            except AttributeError:
                raise ImproperlyConfigured("%s isn't a valid Cart model." % settings.CART_MODEL)
        if settings.CART_MODEL_DB:
            self.database = settings.CART_MODEL_DB
        
        # Cart is stored as a list of ( item_id, quantity )
        for item, quantity in request.session.get(self.name, []):
            try:
                item = self._get(item)
                item.session_cart_quantity = quantity
                self.append(item, quantity)
            except self.model.DoesNotExist:
                pass

    def save(self):
        """
        Save this cart to the session
        """
        self.request.session[self.name] = tuple(
            (i.item.pk, i.quantity,)
            for i in self
        )

    def _get(self, item):
        """
        Ensure item is an instance of self.model
        """
        if not isinstance(item, self.model):
            if self.database:
                return self.model._default_manager.using(self.database).get(pk=item)
            else:
                return self.model._default_manager.get(pk=item)
        return item

    def index(self, value, **kwargs):
        """
        Overloaded parent class (list) method. Preventing duplication of (item, quantity) pairs.
        """
        if isinstance(value, self.model):
            for i in self:
                if i.item == value:
                    return self.index(i)
        return super(Cart, self).index(value, **kwargs)

    def append(self, item, quantity=1):
        """
        Append some amount of item to cart.
        """
        item = self._get(item)
        try:
            self[self.index(item)].quantity += quantity
        except ValueError:
            super(Cart, self).append(CartItem(item, quantity))

    def update_quantity(self, item, quantity):
        """
        Update quantity of specified item in the cart
        """
        item = self._get(item)
        try:
            self[self.index(item)].quantity = quantity
        except ValueError:
            super(Cart, self).append(CartItem(item, quantity))

    def update_quantities(self, dict):
        """
        Update quantities of specified items in the cart basing on provided dictionary
        Dictionary format is stupid simple: {item_id1: quantity1, item_id2: quantity2}
        """
        for item_id in dict:
            # item_id will be passed to _get() and transformed to real item
            try:
                self.update_quantity(item_id, dict[item_id])
            except self.model.DoesNotExist:
                # nobody cares - skipping this case silently
                pass

    def remove(self, item):
        """
        Remove single item from the cart
        """
        super(Cart, self).remove(self[self.index(self._get(item))])

    def remove_items(self, items_list):
        """
        Remove list of items from the cart
        """
        for item in items_list:
            self.remove(item)


    def empty(self):
        """
        Remove all items from cart
        """
        while len(self):
            self.pop()

    def __repr__( self ):
        return ','.join([repr(x) for x in self])

    @property
    def items_total(self):
        return len(self)

    @property
    def total_quantity(self):
        return reduce(lambda res, x: res+x, [i.quantity for i in self])
        
    @property
    def items(self):
        items = []
        for item in self:
            items.append(item.item)
        return items

    @property
    def total_price(self):
        if hasattr(self.model, 'price'):
            total_price = 0
            for item in self:
                print item
                total_price += item.item.price * item.quantity
            return total_price
