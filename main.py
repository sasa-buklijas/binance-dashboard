from urllib.request import urlopen
import json
import sys
import datetime
import piesparrow as ps


class BinanceExchangeInfo:
    
    def __init__(self):
        # https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information
        url = "https://data.binance.com/api/v3/exchangeInfo"
        response = urlopen(url)
        data_json = json.loads(response.read())
        #print(data_json)

        self._data_from = data_json['timezone']
        
        maybe_trading_assets = set()
        maybe_break_assets = set()

        trading_pairs = set()
        non_trading_pairs = set()
        len_trading_pairs = 0
        len_non_trading_pairs = 0
        len_pairs = 0
        for symbol in data_json['symbols']:
            len_pairs += 1
            #print(set(symbol['status']))
            
            match symbol['status']:
                case 'TRADING':
                    len_trading_pairs += 1
                    trading_pairs.add(symbol['symbol'])
                    maybe_trading_assets.add(symbol['baseAsset'])
                    maybe_trading_assets.add(symbol['quoteAsset'])
                case 'BREAK':
                    len_non_trading_pairs += 1
                    non_trading_pairs.add(symbol['symbol'])
                    maybe_break_assets.add(symbol['baseAsset'])
                    maybe_break_assets.add(symbol['quoteAsset'])

        assert len_pairs == len_trading_pairs+len_non_trading_pairs\
            ,'status other than TRADING or BREAK'
        self._len_trading_pairs = len_trading_pairs
        self._len_non_trading_pairs = len_non_trading_pairs
        self._len_pairs = len_pairs
        self._trading_pairs = trading_pairs
        self._non_trading_pairs = non_trading_pairs

        non_trading_assets = maybe_break_assets - maybe_trading_assets
        len_non_trading_assets = len(non_trading_assets)
        trading_assets = maybe_trading_assets - non_trading_assets
        len_trading_assets = len(trading_assets)
        len_assets = len(maybe_trading_assets.union(maybe_break_assets))
        assert len_non_trading_assets + len_trading_assets == len_assets\
            ,'Number of trading and non_trading assets wrong'
        self._trading_assets = trading_assets
        self._non_trading_assets = non_trading_assets
        self._len_assets = len_assets
        self._len_non_trading_assets = len_non_trading_assets
        self._len_trading_assets = len_trading_assets

def main():
    bei = BinanceExchangeInfo()

    output_file = 'index'
    if len(sys.argv) == 2 :
        output_file = sys.argv[1]
    #print(output_file, sys.argv)

    ps.init(filename = output_file, title = 'Binance Dashboard')

    time_zone = datetime.datetime.now().astimezone().tzname()
    header = f'Binance Dashboard from {datetime.datetime.now()} {time_zone}'
    ps.row(
        ps.colxl(align='center', type='box', content=ps.h1(header))
    )

    ps.row(
        ps.colxs(align='center', type='card', content=ps.h2('Assets:'))
    +   ps.colxs(align='center', type='card', content=ps.h4(bei._len_assets))
    +   ps.colxs(align='center', type='box', content=ps.h2(''))
    +   ps.colxs(align='center', type='card', content=ps.h2('Pairs:'))
    +   ps.colxs(align='center', type='card', content=ps.h4(bei._len_pairs))
    )

    content1 = f'{bei._len_trading_assets} or \
        {bei._len_trading_assets/bei._len_assets*100:.0f}%'
    content2 = f'{bei._len_trading_pairs} or \
        {bei._len_trading_pairs/bei._len_pairs*100:.0f}%'
    ps.row(
        ps.colxs(align='center', type='card', content=ps.h2('Trading:'))
    +   ps.colxs(align='center', type='card', content=ps.h2(content1))
    +   ps.colxs(align='center', type='box', content=ps.h2(''))
    +   ps.colxs(align='center', type='card', content=ps.h2('Trading:'))
    +   ps.colxs(align='center', type='card', content=ps.h2(content2))
    )

    content1 = f'{bei._len_non_trading_assets} or \
        {bei._len_non_trading_assets/bei._len_assets*100:.0f}%'
    content2 = f'{bei._len_non_trading_pairs} or \
        {bei._len_non_trading_pairs/bei._len_pairs*100:.0f}%'
    ps.row(
        ps.colxs(align='center', type='card', content=ps.h2('Delisted:'))
    +   ps.colxs(align='center', type='card', content=ps.h4(content1))
    +   ps.colxs(align='center', type='box', content=ps.h2(''))
    +   ps.colxs(align='center', type='card', content=ps.h2('Delisted:'))
    +   ps.colxs(align='center', type='card', content=ps.h4(content2))
    )

    ps.row(
        ps.colxl(align='center', type='box', content=ps.link('https://github.com/sasa-buklijas/binance-dashboard/tree/main',
                                                            'Code available on GitHub'))
    )

    ps.row(
        ps.colxl(align='center', type='card', content=ps.p(f'Delisted assets: \
            {sorted(bei._non_trading_assets)}'))
    )

    ps.row(
        ps.colxl(align='center', type='card', content=ps.p(f'Delisted pairs: \
            {sorted(bei._non_trading_pairs)}'))
    )

if __name__ == "__main__":
    main()
