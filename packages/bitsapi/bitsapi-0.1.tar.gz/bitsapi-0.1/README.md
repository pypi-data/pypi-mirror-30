Add a address 'n44f5J2B2AfBizzo4HxRpB3jnp1QGHKp7t' to watch :

from btcapi import TxWatcher
w = TxWatcher('n44f5J2B2AfBizzo4HxRpB3jnp1QGHKp7t')
def tx_printer(tx):
         print(tx)
w.on_tx += tx_printer
w.run_forever()



To import all addresses from list.csv :

from btcapi import TxWatcher
import pandas as pd
df = pd.read_csv('small.csv')
useraddr = df['address'].tolist()
w = TxWatcher(useraddr)
def tx_printer(tx):
         print(tx)

w.on_tx += tx_printer
w.run_forever()