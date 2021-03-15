from pytradesim.modules.orderbook import Order, Orderbook, Trade

def test_orderbook_market_order_no_match():
    orderbook = Orderbook("TEST")

    order = Order("TEST", 8, 1, "B", 2, "NEWORDER_1", "TESTSESSION")
    orderbook.new_order(order)

    order = Order("TEST", 8, 1, "B", 2, "NEWORDER_3", "TESTSESSION")
    orderbook.new_order(order)

    order = Order("TEST", 6, 1, "S", 2, "NEWORDER_2", "TESTSESSION")
    orderbook.new_order(order)

    assert orderbook.trades.qsize() == 0
    assert orderbook.bids[23.54][0].quantity == 100
    assert orderbook.bbo() == (23.54, float("inf"))


if __name__ == "__main__":
    test_orderbook_market_order_no_match()
