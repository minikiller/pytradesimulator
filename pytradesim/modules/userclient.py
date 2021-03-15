import quickfix as fix
import quickfix44 as fix44

from .utils import Message
from time import sleep

ORDERS = {}


class BaseApplication(fix.Application):
    def onCreate(self, sessionID):
        return

    def onLogon(self, sessionID):
        return

    def onLogout(self, sessionID):
        return

    def toAdmin(self, message, sessionID):
        self.sessionID = sessionID
        return

    def fromAdmin(self, message, sessionID):
        return

    def toApp(self, message, sessionID):
        return

    def fromApp(self, message, sessionID):
        return


ORDER_TABLE = {}


class UserClient(BaseApplication):
    sessionId = None

    @staticmethod
    def getSessionId():
        return UserClient.sessionId

    def set_logging(self, logger):
        self.logger = logger

    def onCreate(self, sessionID):
        self.logger.info(f"Successfully created session {sessionID}.")
        UserClient.sessionId = sessionID
        return

    def onLogon(self, sessionID):
        self.logger.info(f"{sessionID} session successfully logged in.")
        return

    def onLogout(self, sessionID):
        self.logger.info(f"{sessionID} session successfully logged out.")
        return

    def toApp(self, message, sessionID):
        self.logger.debug(f"Sending {message} session {sessionID}")

    def fromApp(self, message, sessionID):
        print("receive msg", message.__str__().replace('\x01', '|'))
        self.logger.info(f"Got message {message} for {sessionID}.")
    #     self.process(message, sessionID)

    # def process(self, message, sessionID):
        self.logger.debug("Processing message.")
        print(message.__str__().replace("\x01", "|"))
        msgtype = fix.MsgType()
        exectype = fix.ExecType()
        message.getHeader().getField(msgtype)
        message.getField(exectype)

        if msgtype.getValue() == "8":
            if exectype.getValue() == "2":
                self.logger.info("Trade received.")
                # (
                #     symbol,
                #     price,
                #     quantity,
                #     side,
                #     client_order_id,
                #     trade_exec_id,
                #     order_status,
                # ) = self.__get_attributes(message)
                # self.logger.info(
                #     f"Trade: {trade_exec_id}, {client_order_id} {symbol}"
                #     f" {quantity}@{price} {side}"
                # )
            elif exectype.getValue() == "0":
                self.logger.info("Order placed successfully.111111")
                # (
                #     symbol,
                #     price,
                #     quantity,
                #     side,
                #     client_order_id,
                #     exec_id,
                #     order_status,
                # ) = self.__get_attributes(message)

                # ORDERS[client_order_id.getValue()] = [symbol, price, quantity, side]

                # self.logger.info(
                #     f"Order: {exec_id}, {client_order_id} {symbol}"
                #     f" {quantity}@{price} {side}"
                # )
            elif exectype.getValue() == "5":
                self.logger.info("Order replaced successfully.")
                # (
                #     symbol,
                #     price,
                #     quantity,
                #     side,
                #     client_order_id,
                #     exec_id,
                #     order_status,
                # ) = self.__get_attributes(message)

                # ORDERS[client_order_id.getValue()] = [symbol, price, quantity, side]

                # self.logger.info(
                #     f"Order: {exec_id}, {client_order_id} {symbol}"
                #     f" {quantity}@{price} {side}"
                # )

    def __get_attributes(self, message):
        price = fix.LastPx()
        quantity = fix.LastQty()
        symbol = fix.Symbol()
        side = fix.Side()
        client_order_id = fix.ClOrdID()
        exec_id = fix.ExecID()
        order_status = fix.OrdStatus()

        message.getField(client_order_id)
        message.getField(side)
        message.getField(symbol)
        message.getField(price)
        message.getField(quantity)
        message.getField(order_status)
        message.getField(exec_id)

        return (symbol, price, quantity, side, client_order_id, exec_id, order_status)


def get_order_id(sender_comp_id, symbol):
    if symbol in ORDER_TABLE:
        _id = ORDER_TABLE[symbol]
    else:
        _id = 1

    order_id = sender_comp_id + symbol + str(_id)
    ORDER_TABLE[symbol] = _id + 1

    return order_id


def new_order(
    sender_comp_id, target_comp_id, symbol, quantity, price, side, order_type, order_status
):
    if side.lower() == "buy":
        side = fix.Side_BUY
    else:
        side = fix.Side_SELL

    message = Message()
    header = message.getHeader()
    header.setField(fix.BeginString("FIX.4.4"))
    # header.setField(fix.BeginString("FIXT.1.1"))
    
    # header.setField(fix.BeginString("FIX.4.2"))
    
    header.setField(fix.SenderCompID(sender_comp_id))
    header.setField(fix.TargetCompID(target_comp_id))
    header.setField(fix.MsgType("D"))
    ord_id = get_order_id(sender_comp_id, symbol)
    message.setField(fix.ClOrdID(ord_id))
    message.setField(fix.Symbol(symbol))
    message.setField(fix.Side(side))
    message.setField(fix.Price(float(price)))
    if order_type.lower() == "market":
        message.setField(fix.OrdType(fix.OrdType_MARKET))
    else:
        message.setField(fix.OrdType(fix.OrdType_LIMIT))
    # message.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))
    message.setField(fix.HandlInst(
        fix.HandlInst_AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION))

    message.setField(fix.TransactTime())
    message.setField(fix.OrderQty(float(quantity)))
    # message.setField(fix.ExecType(0))
    message.setField(fix.Text(f"{side} {symbol} {quantity}@{price}"))
    print(message)
    return message


def replace_order(
    sender_comp_id, target_comp_id, quantity, price, orig_client_order_id
):
    symbol = ORDERS[orig_client_order_id][0].getValue()
    side = ORDERS[orig_client_order_id][3].getValue()

    message = fix44.OrderCancelReplaceRequest()
    header = message.getHeader()
    header.setField(fix.SenderCompID(sender_comp_id))
    header.setField(fix.TargetCompID(target_comp_id))
    ord_id = get_order_id(sender_comp_id, symbol)
    message.setField(fix.OrigClOrdID(orig_client_order_id))
    message.setField(fix.ClOrdID(ord_id))
    message.setField(fix.Symbol(symbol))
    message.setField(fix.Side(side))
    message.setField(fix.Price(float(price)))
    message.setField(fix.OrdType(fix.OrdType_LIMIT))
    message.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))
    message.setField(fix.TransactTime())
    message.setField(fix.TransactTime())
    message.setField(fix.OrderQty(float(quantity)))
    message.setField(fix.Text(f"{side} {symbol} {quantity}@{price}"))

    return message


def delete_order(sender_comp_id, target_comp_id, orig_client_order_id):
    symbol = ORDERS[orig_client_order_id][0].getValue()
    side = ORDERS[orig_client_order_id][3].getValue()

    message = fix44.OrderCancelRequest()
    header = message.getHeader()
    header.setField(fix.SenderCompID(sender_comp_id))
    header.setField(fix.TargetCompID(target_comp_id))
    ord_id = get_order_id(sender_comp_id, symbol)
    message.setField(fix.OrigClOrdID(orig_client_order_id))
    message.setField(fix.ClOrdID(ord_id))
    message.setField(fix.Symbol(symbol))
    message.setField(fix.Side(side))
    message.setField(fix.TransactTime())
    message.setField(fix.Text(f"Delete {orig_client_order_id}"))

    return message


def send_bat_order():
    step1 = "8=FIX.4.4\0019=142\00135=D\00134=69\00149=N2N\00152=20210206-02:12:04.215\00156=FEME\00111=1612577524199\00121=1\00138=1\00140=2\00144=111.25\00154=1\00155=FMG3-DEC20\00159=0\00160=20210206-02:12:04.212\00110=073\001"
    step2 = "8=FIX.4.4\0019=142\00135=D\00134=70\00149=N2N\00152=20210206-02:13:21.524\00156=FEME\00111=1612577601535\00121=1\00138=1\00140=2\00144=110.15\00154=2\00155=FMG3-MAR21\00159=0\00160=20210206-02:13:21.523\00110=083\001"
    step3 = "8=FIX.4.4\0019=145\00135=D\00134=71\00149=N2N\00152=20210206-02:14:03.572\00156=FEME\00111=1612577643586\00121=1\00138=1\00140=2\00144=1.5\00154=2\00155=FMG3-DEC20-MAR21\00159=0\00160=20210206-02:14:03.572\00110=053\001"
    step4 = "8=FIX.4.4\0019=142\00135=D\00134=72\00149=N2N\00152=20210206-02:17:14.602\00156=FEME\00111=1612577834617\00121=1\00138=1\00140=2\00144=109.95\00154=1\00155=FMG3-JUN21\00159=0\00160=20210206-02:17:14.602\00110=129\001"
    step5 = "8=FIX.4.4\0019=142\00135=D\00134=73\00149=N2N\00152=20210206-02:18:59.381\00156=FEME\00111=1612577939399\00121=1\00138=1\00140=2\00144=109.35\00154=2\00155=FMG3-MAR21\00159=0\00160=20210206-02:18:59.381\00110=153\001"
    
    data_dictionary = fix.DataDictionary("spec/FIX42.xml")
    message = Message()

    message.setString(step1, True, data_dictionary)
    send(message)
    sleep(1)
    message.setString(step2, True, data_dictionary)
    send(message)
    sleep(1)
    message.setString(step3, True, data_dictionary)
    send(message)
    sleep(1)
    message.setString(step4, True, data_dictionary)
    send(message)
    sleep(1)
    # message.setString(step5, True, data_dictionary)

def send(message):
    try:
        fix.Session.sendToTarget(message)
    except fix.SessionNotFound:
        raise Exception(f"No session found {message}, exiting...")


"""
发送任何fix字符串给server，中间以\001分隔
"""


def test_order():
    # _str = "8=FIX.4.4\0019=267\00135=D\00134=1284\00149=N2N\00150=ricky1\00152=20210112-02:47:10.159\00156=FEME\00157=G\001142=MY\0011=B10013\00111=MY011206\00121=1\00138=2\00140=2\00144=3381.000000\00154=1\00155=1004\00159=0\00160=20210112-10:47:00.999\001107=FCPON1\001167=FUT\001204=1\0011028=Y\0011031=Y\0011603=global connect\0011604=3.0\0011605=N2N\0019702=4\0019717=MY011206\00110=118\001"
    _str = "8=FIX.4.4\0019=127\00135=D\00149=CLIENT6\00156=FEME\00111=CLIENT6HEL-Apr211\00121=1\00138=2\00140=2\00144=100\00154=2\00155=HEL-Apr21\00158=2 HEL-Apr21 2@100\00160=20210115-12:29:05\00110=071\001"

    data_dictionary = fix.DataDictionary("spec/FIX42.xml")
    message = Message()

    message.setString(_str, True, data_dictionary)
    # message = Message(_str, data_dictionary, False)
    return message

 


"""
发送消息给sessionId
"""


def sendMsg(msg):
    try:
        fix.Session.sendToTarget(msg, UserClient.getSessionId())
    except fix.SessionNotFound:
        raise Exception(f"No session found {msg}, exiting...")
