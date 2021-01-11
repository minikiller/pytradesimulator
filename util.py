str = "8=FIX.4.2^A9=107^A35=5^A34=1^A49=FEME^A52=20210110-12:46:46.537^A56=N2N^A58=Invalid Logon message: Invalid tag number, field=1603^A10=002^A"
# str="8=FIX.4.29=8835=86=011=CLIENT6hek114=017=020=037=CLIENT6hek138=139=054=255=hek150=0151=110=124"
print(str.replace('^A', '|'))
