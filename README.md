Name: CROITORU Adrian-Valeriu
Group: 332CA

# Homework 1 - MPMC (Multi Producer Multi Consumer) Marketplace

General
-

Efficient multi-threaded `MPMC` Marketplace implemented in `Python 3`.
There are 3 main classes - **Producer**, **Consumer** and the **Marketplace**.
The last one connects the producers and consumers, giving them access to
*thread-safe* methods which allow the exchange of products.\
The project is a very good mock example of the MPMC Classic Synchronization Problem,
and implementing it was an efficient way to deepen the theoretical knowledge.

Program flow & chosen approach
-

The **producer** infinitely generates its designated products. Each producer
has its own buffer, stored in the **Marketplace** instance:
    ```python
    self.producer_queues = {}
    ```
If a producer's buffer is full, it waits a given time and tries again.

The **consumer** simulates for each cart the given operations. The carts are
stored in the **Marketplace** instance:
    ```python
    self.carts = {}
    ```

The **marketplace** unites the producers and consumers. There are 2 dictionaries:
    * producer_queues
    * carts
The **producer_queues** and **carts** are synchronized using locks,
because multiple threads use these structures' length concurrently.\
Also, there is a lock for each element of **producer_queues**,
because multiple producers/consumers may try to add/remove elements from a queue
concurrently. There is no need to have locks for carts also, as only one consumer
may access its cart.\
There is also a synchronized structure, **returned_products**, used for storing
the products which were removed from carts. When a consumer wants to add a product
in its cart, it searches all producers queues and also the **returned_products**
structure.


Unit Testing & Logging
-

There are unit tests generated for each method of the **Marketplace** class
and all pass. Also, for each method of this class, there are logs at the
beginning of the function, as well as right before the return, in order to
make the debug easier and observe the general program flow.


Implementation
-

All requirements are completely fulfilled and everything is functional.
Unit & functional tests were done and there are no detected errors/bugs.

The only detected bug was on the 10th test, because it used to sometimes
fail as there were a lot of consumers trying to write to the output concurrently.
Although the python3 `print()` method is said to be thread-safe,
occasionally random characters were thrown at the output.\
To solve this issue, I used a lock in order to give access to only one consumer
at a time to output its processed order.


Documentation
-

* https://stackoverflow.com
* https://ocw.cs.pub.ro/courses/asc
* https://docs.python.org/3/library


Git
-

1. https://github.com/adriancroitoru97/mpmc-marketplace
