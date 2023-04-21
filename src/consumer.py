"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, Lock
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

        self.print_lock = Lock()

    def do_operation(self, operation, cart_id):
        """
        Function which does an operation on a specific cart.

        :type operation: JSON
        :param operation: JSON object as described in the README.

        :type cart_id: int
        :param cart_id: the id of the desired cart
        """
        op_type = operation["type"]
        product_id = operation["product"]
        quantity = operation["quantity"]

        for _ in range(quantity):
            if op_type == "add":
                added_to_cart = False
                while not added_to_cart:
                    added_to_cart = self.marketplace.add_to_cart(cart_id, product_id)
                    if not added_to_cart:
                        sleep(self.retry_wait_time)
            elif op_type == "remove":
                self.marketplace.remove_from_cart(cart_id, product_id)

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()

            # execute each operation (add / remove)
            for operation in cart:
                self.do_operation(operation, cart_id)

            # after all operations executed, place order
            order = self.marketplace.place_order(cart_id)

            # syncronized printing of the result
            with self.print_lock:
                for prod in order:
                    print(self.name, "bought", prod)
