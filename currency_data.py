import requests
import pandas as pd


END_POINT_SIMBOL = 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/Moedas?$top=1000&$format=json'

class CurrencyData:
    def __init__(self, url):
        self.url = url

    def getAll(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            if 'value' in data:
                return data['value']
            else:
                print('Não foi possivel pegar os valores da API')
        else:
            print('Erro ao solicitar os dados da API', response.status_code)

currency_data = CurrencyData(END_POINT_SIMBOL)

class CurrencyTable:
    def __init__(self, currency_data):
        self.currency_data = currency_data

    def table_currency(self):
        if self.currency_data:
            table = pd.DataFrame(self.currency_data)
            return table
        else:
            print('Não há dados disponiveis para criar a tabela.')

currency_table = CurrencyTable(currency_data.getAll())
table = currency_table.table_currency()

# Irá retornar 'True' se o objeto pandas estiver vazio e 'Falso' caso contrário.
#if not table.empty:
#    print(table)
#else:
#    print('Erro ao formar a tabela.')

position_table = 4
currency = table['simbolo'][position_table]
date_initial = '01-01-2022'
date_end = '04-30-2023'

URL_COTATION = f'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda=%27{currency}%27&@dataInicial=%27{date_initial}%27&@dataFinalCotacao=%27{date_end}%27&$top=100&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao,tipoBoletim'

class CurrencyCotation:
    def __init__(self, url, currency, date_initial, date_end):
        self.url = url
        self.currency = currency
        self.date_initial = date_initial
        self.date_end = date_end

    def cotation_currency(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            if 'value' in data:
                return data['value']
            else:
                print('Não foi possivel pegar os dados do Banco Central')
        else:
            print('Não foi possivel fazer a conexão com a API do Banco Central')

cotation = CurrencyCotation(URL_COTATION, currency, date_initial, date_end)

cotation_table = CurrencyTable(cotation.cotation_currency())


from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])

def api_cotation():

    currency_data = CurrencyData(END_POINT_SIMBOL)
    currency_table = CurrencyTable(currency_data.getAll())
    cotation = CurrencyCotation(URL_COTATION, currency, date_initial, date_end)
    
    # Obtém os dados da cotação da moeda
    cotation_data = cotation_table.table_currency().to_dict('records')
    
    # Retorna os dados em formato JSON
    return jsonify(cotation_data)


if __name__ == '__main__':
    app.run(debug=True)