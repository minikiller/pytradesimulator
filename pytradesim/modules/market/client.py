import quickfix as fix
import quickfix44 as fix44

from .utils import BaseApplication, Book


class MarketDataClient(BaseApplication):
    def _generate_id(self):
        self.__count += 1
        return "TESTREQUEST" + str(self.__count)

    def set_logging(self, logger):
        self.logger = logger

    def onCreate(self, sessionID):
        self.__count = 0
        self.logger.info(f"Successfully created session {sessionID}.")
        return

    def onLogon(self, sessionID):
        self.logger.info(f"{sessionID} session successfully logged in.")
        return

    def onLogout(self, sessionID):
        self.logger.info(f"{sessionID} session successfully logged out.")
        return

    def toApp(self, message, sessionID):
        print(message.__str__().replace("\x01", "|"))
        self.logger.debug(f"Sending {message} session {sessionID}")

    def fromApp(self, message, sessionID):
        self.logger.info(f"Got message {message} for {sessionID}.")
        self.show(message)

    def show(self, message):
        msgtype = fix.MsgType()
        message.getHeader().getField(msgtype)

        print(message.__str__().replace("\x01", "|"))

        _bids = []
        _asks = []
        _trades = []

        if msgtype.getValue() == "W":
            symbol = fix.Symbol()
            message.getField(symbol)

            instrument = symbol.getValue()

            entry_type = fix.MDEntryType()
            entry_px = fix.MDEntryPx()
            entry_size = fix.MDEntrySize()
            entries = fix.NoMDEntries()

            message.getField(entries)

            group = fix44.MarketDataSnapshotFullRefresh().NoMDEntries()

            for i in range(entries.getValue()):
                message.getGroup(i + 1, group)
                group.getField(entry_type)
                group.getField(entry_px)
                group.getField(entry_size)

                if entry_type.getValue() == "0":
                    _bids.append((entry_px.getValue(), entry_size.getValue()))
                elif entry_type.getValue() == "1":
                    _asks.append((entry_px.getValue(), entry_size.getValue()))
                elif entry_type.getValue() == "2":
                    _trades.append((entry_px.getValue(), entry_size.getValue()))

            book = Book(instrument, _bids, _asks, _trades)

            print(book)

    def security_definition_request(self, sender_comp_id, target_comp_id):
        message = fix44.SecurityDefinitionRequest()
        header = message.getHeader()
        header.setField(fix.SenderCompID(sender_comp_id))
        header.setField(fix.TargetCompID(target_comp_id))
        message.setField(fix.SecurityReqID(self._generate_id()))
        message.setField(fix.SecurityRequestType(fix.SecurityRequestType_REQUEST_LIST_SECURITIES))
         
        # group = fix44.SecurityDefinitionRequest().Instrument()
        # Instrument 
        # for md_type in md_types:
        #     group.setField(fix.MDEntryType(md_type))
        #     message.addGroup(group)
        try:
            fix.Session.sendToTarget(message)
        except fix.SessionNotFound:
            raise Exception(f"No session found {message}, exiting...")

    def market_data_request(self, sender_comp_id, target_comp_id, symbols):
        md_types = [fix.MDEntryType_BID, fix.MDEntryType_OFFER, fix.MDEntryType_TRADE]

        message = fix44.MarketDataRequest()

        header = message.getHeader()
        header.setField(fix.SenderCompID(sender_comp_id))
        header.setField(fix.TargetCompID(target_comp_id))

        message.setField(fix.MDReqID(self._generate_id()))
        message.setField(
            fix.SubscriptionRequestType(
                fix.SubscriptionRequestType_SNAPSHOT_PLUS_UPDATES
            )
        )
        # message.setField(
        #     fix.SubscriptionRequestType(
        #         fix.SubscriptionRequestType_SNAPSHOT
        #     )
        # )
        
        """
        Valid values:

        0 = Full Book

        1 = Top of Book

        N>1 = Report best N price tiers of data
        """ 

        message.setField(fix.MarketDepth(0))

        """
        Valid values:
        0 = Full Refresh
        1 = Incremental Refresh
        """

        message.setField(fix.MDUpdateType(fix.MDUpdateType_INCREMENTAL_REFRESH))

        group = fix44.MarketDataRequest().NoMDEntryTypes()

        for md_type in md_types:
            group.setField(fix.MDEntryType(md_type))
            message.addGroup(group)

        group = fix44.MarketDataRequest().NoRelatedSym()

        for symbol in symbols:
            group.setField(fix.Symbol(symbol))
            message.addGroup(group)

        try:
            fix.Session.sendToTarget(message)
        except fix.SessionNotFound:
            raise Exception(f"No session found {message}, exiting...")
