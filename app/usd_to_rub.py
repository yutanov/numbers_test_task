from pycbrf import ExchangeRates


def convert(price):
    '''
    Получение курса ЦБ РФ на текущий день
    Перевод суммы в долларах США в рубли РФ
    '''
    rates = ExchangeRates()
    rub = float(price) * float(rates['USD'].value)
    return round(rub, 2)
