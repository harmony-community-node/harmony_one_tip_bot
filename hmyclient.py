from pyhmy import account, cli

class HmyClient:

    _mainnetUrl = 'https://api.s0.t.hmny.io'
    _oneAmountDenominator = 1000000000000000000

    @classmethod
    def regiterNewUser(self, telegram_user_id):
        cli.set_binary('/home/satish/hmydir/hmy')
        return cli.single_call(f'hmy keys add {telegram_user_id}')
    
    @classmethod
    def getBalace(self, one_address):
        return account.get_balance(one_address, endpoint=HmyClient._mainnetUrl) / HmyClient._oneAmountDenominator
    
    @classmethod
    def getTransactionHistory(self, one_address):
        transactions = account.get_transaction_history(one_address, endpoint=HmyClient._mainnetUrl, include_full_tx=True) 
        print(transactions)
        return transactions