from pyhmy import account, cli

class HmyClient:

    _hmyBinaryDir = '/home/satish/hmydir/hmy'
    _networkUrl = 'https://api.s0.b.hmny.io' #'https://api.s0.t.hmny.io'
    _oneAmountDenominator = 1000000000000000000

    @classmethod
    def regiterNewUser(self, telegram_user_id):
        cli.set_binary(HmyClient._hmyBinaryDir)
        return cli.single_call(f'hmy keys add {telegram_user_id}')
    
    @classmethod
    def transfer(self, from_address, to_address, amount, from_shard=0, to_shard=0):
        cli.set_binary(HmyClient._hmyBinaryDir)
        return cli.single_call(f'hmy transfer --node={HmyClient._networkUrl} --from {from_address} --to {to_address} --from-shard {from_shard} --to-shard {to_shard} --amount {amount}')
    
    @classmethod
    def getBalace(self, one_address):
        return account.get_balance(one_address, endpoint=HmyClient._networkUrl) / HmyClient._oneAmountDenominator
    
    @classmethod
    def validateONEAdress(self, one_address):
        return account.is_valid_address(one_address) 

    
    @classmethod
    def getTransactionHistory(self, one_address):
        transactions = account.get_transaction_history(one_address, endpoint=HmyClient._networkUrl, include_full_tx=True) 
        print(transactions)
        return transactions