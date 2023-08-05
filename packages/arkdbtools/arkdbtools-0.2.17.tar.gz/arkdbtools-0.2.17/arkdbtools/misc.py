import arkdbtools.dbtools

delegate_address = 'AJRZHsHjqED3E3h55Ai9H6DtuoWUiBjLo7'

host = 'localhost'
dbuser = 'postgres'
password = 'Dwl1ml12_3#'
database = 'ark_mainnet'

arkdbtools.dbtools.set_delegate(
            address=delegate_address,
            pubkey='02bd17dc29faabdf5eddd4e5679c3540d73adac765c73555be7cfd43e11bb51abb'
        )

arkdbtools.dbtools.set_connection(
            host=host,
            database=database,
            user=dbuser,
            password=password
        )

payouts = arkdbtools.dbtools.Delegate.trueshare()[0]

for i in payouts:
    print(i, payouts[i]['share'], payouts[i]['balance'])

