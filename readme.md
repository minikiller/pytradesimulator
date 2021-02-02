## 各个功能模块功能分析
#### market_data
* 功能类似大盘
* Listener 用于server链接
* SocketAcceptor链接market_client
#### market_client
* 获得大盘信息的客户端，通过订阅获得相关的大盘信息
* SocketInitiator 链接 market_data

```
Enter symbol to subscribe: 
2020-11-13 23:50:20.758729 [INFO   ] (fromApp  ) Got message 8=FIX.4.29=12035=W34=7749=MARKET52=20201113-15:50:20.00000056=MDCLIENT155=test268=2269=0270=100271=100269=2270=200271=10010=088 for FIX.4.2:MDCLIENT1->MARKET.
8=FIX.4.2|9=120|35=W|34=77|49=MARKET|52=20201113-15:50:20.000000|56=MDCLIENT1|55=test|268=2|269=0|270=100|271=100|269=2|270=200|271=100|10=088|
Symbol: test
+------------------+--------------------+
| bid_prc, bid_qty |  ask_prc, ask_qty  |
+------------------+--------------------+
|  (100.0, 100.0)  | ('Empty', 'Empty') |
+------------------+--------------------+
Trade test, 100.0@200.0.
```

#### server
* 交易市场
* Client 链接 market_data
* SocketAcceptor 用于链接 client

#### client
* 交易客户
* SocketInitiator 链接 server
* 支持新增订单，删除订单，替换订单
```
Enter choice :- 
1. New order
2. Replace order
3. Delete order
> 
```

### doc
https://neerajkaushik1980.wordpress.com/2012/04/22/quickfix-connect-multiple-fix-sessions-with-fix-server/

### fix 4.4

https://github.com/quickfix/quickfix/blob/master/spec/FIX44.xml

### print fix message
```
cd pytradesim
python fixprinter.py --spec spec/FIX44.xml --f test.txt
```
```
./client.py configs/client1.cfg

./market_client.py configs/mdclient1.cfg -d

### market request
```
8=FIX.4.2|9=133|35=V|34=48|49=MDCLIENT1|52=20210115-12:44:55.000000|56=FEME|146=1|55=HEL-Apr21|262=TESTREQUEST1|263=1|264=10|267=3|269=0|269=1|269=2|10=182|
```
### market data response
```
8=FIX.4.2|9=112|35=W|34=131|49=FEME|52=20210115-13:35:09.354|56=MDCLIENT1|55=HEL-Apr211|262=TESTREQUEST1|268=1|269=0|270=123.45|10=029
```


### new order request
```
8=FIX.4.2|9=127|35=D|49=CLIENT6|56=FEME|11=CLIENT6HEL-Apr211|21=1|38=2|40=2|44=100|54=2|55=HEL-Apr21|58=2 HEL-Apr21 2@100|60=20210115-12:29:05|10=071|
```

### request and response
```
8=FIX.4.4|9=126|35=V|34=77|49=MDCLIENT1|52=20210126-14:25:03.000000|56=FEME|146=1|55=we|262=TESTREQUEST1|263=1|264=10|267=3|269=0|269=1|269=2|10=008|
```
```
8=FIX.4.4|9=163|35=W|34=19|43=Y|49=FEME|52=20210126-14:26:31.082|56=MDCLIENT1|122=20210126-14:26:30.805|55=we|262=TESTREQUEST1|268=2|269=0|270=123.45|271=1|269=0|270=123.45|271=1|10=054|
```
### instrument request
```
8=FIX.4.4|9=82|35=c|34=7|49=MDCLIENT1|52=20210130-03:15:07.000000|56=FEME|320=TESTREQUEST1|321=3|10=154|
```
