# приклад вводу: py exchange.py - виведе сьогоднішні дані (за замовчуванням USD та EUR)
# py exchange.py 3 - за останні 3 дні (за замовчуванням USD та EUR)
# py exchange.py 3 USD EUR - за останні 3 дні з валютами USD та EUR
# (або іншу вказану валюту яка йде після кількості днів через пробіл)


import aiohttp
import asyncio
from datetime import datetime, timedelta
import sys
import platform
import pprint

privat_url = "https://api.privatbank.ua/p24api/exchange_rates?date="

async def get_json(url:str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()                     
                else:
                    raise Exception
        except Exception:
            return None

async def filter_data(data:dict, *args):
    result = {}
    if args:
        for item in data["exchangeRate"]:
            if item["currency"] in args:
                result[item["currency"]] = {"sale":item["saleRateNB"], "purchase":item["purchaseRateNB"]}
    else:
        for item in data["exchangeRate"]:
            if item["currency"] in ("USD", "EUR"):
                result[item["currency"]] = {"sale":item["saleRateNB"], "purchase":item["purchaseRateNB"]}
    return result
    
    
async def exchange(parameters:list):
    today = datetime.today()
    str_today = datetime.strftime(today, "%d.%m.%Y")
    lenght = len(parameters)
    result = []
    if lenght==1:    
        result.append({str_today : await filter_data(await get_json(privat_url+str_today))})
    else:
        if int(parameters[1]) > 10:
            parameters[1] = 10
        args = parameters[2:]
        data = []
        for i in range(int(parameters[1])):
            day = datetime.strftime(today - timedelta(days=i), "%d.%m.%Y")
            data.append(get_json(privat_url+day))
        data = await asyncio.gather(*data)
        for item in data:
            result.append({item["date"]:await filter_data(item, *args)})
    return result
            
async def main():
    pprint.pp(await exchange(sys.argv)) 
            
        

if __name__=="__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    