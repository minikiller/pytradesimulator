#!/usr/bin/env python

import configparser
import logging
from time import sleep
import quickfix as fix

import click
from quickfix import Message
from modules.userclient import (UserClient, delete_order,  new_order,
                                replace_order, sendMsg, send, test_order, send_bat_order)
from modules.utils import setup_logging


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    options_metavar="[options...]",
)
@click.argument(
    "client_config", type=click.Path(exists=True), metavar="[client config]", default="configs/client1.cfg"
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    default=False,
    show_default=True,
    help="Print debug messages.",
)
def main(client_config="configs/client1.cfg", debug=None):
    """FIX client

    Sends new order over a FIX session.

    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.info(f"Logging set to debug.")
    else:
        logger.setLevel(logging.INFO)
        logger.info(f"Logging set to info.")

    config = configparser.ConfigParser()

    config.read(client_config)

    sender_compid = config["SESSION"]["SenderCompID"]
    target_compid = config["SESSION"]["TargetCompID"]

    settings = fix.SessionSettings(client_config)
    store = fix.FileStoreFactory(settings)
    app = UserClient()

    app.set_logging(logger)

    initiator = fix.SocketInitiator(app, store, settings)

    initiator.start()

    sleep(1)

    while True:
        try:
            sleep(1)
            choice = int(
                input(
                    "Enter choice :- "
                    "\n1. New order"
                    "\n2. Replace order"
                    "\n3. Delete order"
                    "\n4. Test order"
                    "\n5. Test batch order"
                    "\n> "
                )
            )
            if choice == 1:
                print("Enter order :- ")
                symbol = input("Symbol: ")
                price = input("Price: ")
                quantity = input("Quantity: ")
                side = input("Side: ")
                order_type = input("Type: ")

                message = new_order(
                    sender_compid,
                    target_compid,
                    symbol,
                    quantity,
                    price,
                    side,
                    order_type,
                    0
                )

                print("Sending new order...")
                send(message)
            elif choice == 2:
                order_id = input("Enter OrderID: ")
                price = input("Price: ")
                quantity = input("Quantity: ")

                message = replace_order(
                    sender_compid, target_compid, quantity, price, order_id
                )

                print("Sending replace order...")
                send(message)
            elif choice == 3:
                order_id = input("Enter OrderID: ")

                message = delete_order(sender_compid, target_compid, order_id)

                print("Sending delete order...")
                send(message)
            elif choice == 4:
                message = test_order()
                sendMsg(message)
            elif choice == 5:
                send_bat_order()

        except KeyboardInterrupt:
            initiator.stop()
            print("Goodbye... !\n")


if __name__ == "__main__":
    logger = setup_logging("logs/", "client")
    main()
