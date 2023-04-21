"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import unittest
import logging
from logging.handlers import RotatingFileHandler
import time
from threading import Lock

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.queue_size_per_producer = queue_size_per_producer

        self.producer_queues = {}
        self.producer_queues_locks = {}
        self.producers_lock = Lock()

        self.carts = {}
        self.carts_lock = Lock()

        self.returned_products = []
        self.returned_products_lock = Lock()

        # Set up logging
        self.logger = logging.getLogger(__name__)
        handler = RotatingFileHandler('marketplace.log', maxBytes=10000, backupCount=1)
        formatter = GMTFormatter('%(asctime)s %(levelname)s [%(threadName)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        self.logger.info('register_producer() called')

        with self.producers_lock:
            # Get an id for the new producer
            producer_id = len(self.producer_queues)

            # Create a queue for the new producer
            self.producer_queues[producer_id] = []
            self.producer_queues_locks[producer_id] = Lock()

        self.logger.info('Producer registered: id=%s', producer_id)

        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        self.logger.info('publish() called, params -> producer_id=%s, product=%s',
                         producer_id, product)

        # Add the product to the queue of the corresponding producer
        with self.producer_queues_locks[producer_id]:
            if len(self.producer_queues[producer_id]) < self.queue_size_per_producer:
                self.producer_queues[producer_id].append(product)
                self.logger.info('Product published!')
                return True

        self.logger.info('Product not published!')

        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        self.logger.info('new_cart() called')

        # Create an empty cart for the consumer
        with self.carts_lock:
            cart_id = len(self.carts)
            self.carts[cart_id] = []

        self.logger.info('New cart created!')

        return cart_id

    def take_product_from_producer(self, product):
        """
        'Takes' (removes) a product from a producer.
        It searches within all producers for the desired product and
        removes it from the first found producer who has it.

        :type product: Product
        :param product: the searched product

        :returns True or False. If False, the product has not been yet produced and
        the caller should try again later.
        """

        self.logger.info('take_product_from_producer() called, params -> product=%s', product)

        # get the total number of producers
        with self.producers_lock:
            num_producers = len(self.producer_queues)

        # seek each producer for the desired product and 'take it' if found
        for producer_id in range(num_producers):
            with self.producer_queues_locks[producer_id]:
                if product in self.producer_queues[producer_id]:
                    self.producer_queues[producer_id].remove(product)
                    self.logger.info('Product \'taken\'!')
                    return True

        # also check if the product is in the returned products array
        with self.returned_products_lock:
            if product in self.returned_products:
                self.returned_products.remove(product)
                self.logger.info('Product \'taken\'!')
                return True

        self.logger.info('Product not found!')

        return False

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        self.logger.info('add_to_cart() called, params -> cart_id=%s, product=%s',
                         cart_id, product)

        # take the product from a producer, if it exists
        product_taken = self.take_product_from_producer(product)
        if not product_taken:
            self.logger.info('Product not added!')
            return False

        # add the product in the cart
        self.carts[cart_id].append(product)
        self.logger.info('Product added!')

        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        self.logger.info('remove_from_cart() called, params -> cart_id=%s, product=%s',
                         cart_id, product)

        # remove the product from the cart
        self.carts[cart_id].remove(product)

        # add the product in the returned products structure,
        # to make it available for other clients
        with self.returned_products_lock:
            self.returned_products.append(product)

        self.logger.info('Product removed!')

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info('place_order() called, params -> cart_id=%s', cart_id)
        return self.carts[cart_id]


class TestMarketplace(unittest.TestCase):
    """
    Unit testing class used to test the behavior of the Marketplace class
    and its methods.
    """

    def setUp(self):
        self.marketplace = Marketplace(queue_size_per_producer=10)

    def test_register_producer(self):
        """
        Unit test for register_producer() method.
        """
        producer_id_1 = self.marketplace.register_producer()
        self.assertEqual(producer_id_1, 0)
        producer_id_2 = self.marketplace.register_producer()
        self.assertEqual(producer_id_2, 1)
        producer_id_3 = self.marketplace.register_producer()
        self.assertEqual(producer_id_3, 2)

    def test_publish(self):
        """
        Unit test for publish() method.
        """
        producer_id_1 = self.marketplace.register_producer()
        product_1 = "product_1"
        result_1 = self.marketplace.publish(producer_id_1, product_1)
        self.assertTrue(result_1)

        # Fill up the producer's queue and try to publish another product
        producer_id_2 = self.marketplace.register_producer()
        for i in range(self.marketplace.queue_size_per_producer):
            product_i = f"product_{i}"
            result_i = self.marketplace.publish(producer_id_2, product_i)
            self.assertTrue(result_i)

        product_overflow = "product_overflow"
        result_overflow = self.marketplace.publish(producer_id_2, product_overflow)
        self.assertFalse(result_overflow)

    def test_new_cart(self):
        """
        Unit test for new_cart() method.
        """
        cart_id_0 = self.marketplace.new_cart()
        self.assertEqual(cart_id_0, 0)
        cart_id_1 = self.marketplace.new_cart()
        self.assertEqual(cart_id_1, 1)
        cart_id_2 = self.marketplace.new_cart()
        self.assertEqual(cart_id_2, 2)

    def test_take_product_from_producer(self):
        """
        Unit test for take_product_from_producer() custom method.
        """
        producer_id_1 = self.marketplace.register_producer()
        product_1 = "product_1"
        result_1 = self.marketplace.publish(producer_id_1, product_1)
        self.assertTrue(result_1)

        product_2 = "product_2"
        result_2 = self.marketplace.take_product_from_producer(product_2)
        self.assertFalse(result_2)

        result_3 = self.marketplace.take_product_from_producer(product_1)
        self.assertTrue(result_3)

        result_4 = self.marketplace.take_product_from_producer(product_1)
        self.assertFalse(result_4)

    def test_add_to_cart(self):
        """
        Unit test for add_to_cart() method.
        """
        producer_id_1 = self.marketplace.register_producer()
        product_1 = "product_1"
        result_1 = self.marketplace.publish(producer_id_1, product_1)
        self.assertTrue(result_1)

        cart_id_1 = self.marketplace.new_cart()
        result_2 = self.marketplace.add_to_cart(cart_id_1, product_1)
        self.assertTrue(result_2)

        # Try to add the same product to the same cart, should fail
        result_3 = self.marketplace.add_to_cart(cart_id_1, product_1)
        self.assertFalse(result_3)

        # Try to add a product that does not exist in the marketplace, should fail
        product_2 = "product_2"
        result_4 = self.marketplace.add_to_cart(cart_id_1, product_2)
        self.assertFalse(result_4)

    def test_remove_from_cart(self):
        """
        Unit test for remove_from_cart() method.
        """
        producer_id_1 = self.marketplace.register_producer()
        product_1 = "product_1"
        result_1 = self.marketplace.publish(producer_id_1, product_1)
        self.assertTrue(result_1)

        # Create a cart and add a product to it
        cart_id = self.marketplace.new_cart()
        result_1 = self.marketplace.add_to_cart(cart_id, product_1)
        self.assertTrue(result_1)
        self.assertIn(product_1, self.marketplace.carts[cart_id])

        # Remove the product from the cart and assert that it's no longer in the cart
        self.marketplace.remove_from_cart(cart_id, product_1)
        self.assertNotIn(product_1, self.marketplace.carts[cart_id])

    def test_place_order(self):
        """
        Unit test for place_order() method.
        """
        producer_id_1 = self.marketplace.register_producer()
        product1 = "Product 1"
        product2 = "Product 2"
        result_1 = self.marketplace.publish(producer_id_1, product1)
        self.assertTrue(result_1)
        result_2 = self.marketplace.publish(producer_id_1, product2)
        self.assertTrue(result_2)

        # Create a cart and add two products to it
        cart_id = self.marketplace.new_cart()
        self.marketplace.add_to_cart(cart_id, product1)
        self.marketplace.add_to_cart(cart_id, product2)

        # Place the order and assert that it contains the expected products
        order = self.marketplace.place_order(cart_id)
        self.assertIn(product1, order)
        self.assertIn(product2, order)


class GMTFormatter(logging.Formatter):
    """
    Class used to customly format logs time using GMT.
    """
    converter = time.gmtime

    def formatTime(self, record, datefmt=None):
        converted_time = self.converter(record.created)
        if datefmt:
            formated_time = time.strftime(datefmt, converted_time)
        else:
            temp = time.strftime("%Y-%m-%d %H:%M:%S", converted_time)
            formated_time = f"{temp},{int(record.msecs):03}"
        return formated_time
