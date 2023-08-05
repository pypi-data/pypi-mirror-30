from mavapi.exceptions import MAVAPIError
import aiohttp
import asyncio
import re

__version__ = '2.2.1'

class Constructor:
    def __init__(self,server=None, access_token=None):
        """

        MAV (Minecraft Account Verification) - Уникальная база привязки Minecraft аккаунта к любым
        социальным сетям или отдельным системам ID, которая создана
        для подтверждения принадлежности того или иного MC аккаунта
        той или иной странице в социальной сети.

        Моя библиотека направлена на работу с MAV API, имеет некоторые
        преимущества и удобства, особенно говоря о легком доступе к API

        :param server: - Сервер MAV API
        :param access_token: - Access Token юзера в MAV API
        """
        self.server = server
        self.access_token = access_token or None

    async def getRequest(self,server=None,params=None, data=None):
        """

        AsyncIO функция, предназначенная для создания единых запросов
        на MAV Server

        :param server: - Сервер MAV API
        :param params: - Желаемый метод
        :param data: - Данные для метода
        :return: - Вернет тело ответа (content)
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(server, params=params, data=data) as request:

                print(request.url)
                request = await request.text()
                request = re.sub('true','1',request)
                request = re.sub('false', '0', request)
                request = re.sub('null', 'None', request)
                request = eval(request)

                return request['content']

    def getData(self,datas):
        """

        Небольшая обвязка данных

        :param datas: - Необходимые данные для обвязки с токеном
        :return: - Вернет готовые обвязанные данные
        """
        data = {'access_token': self.access_token}
        for param in datas.keys():
            if datas[param] != None:
                data[param] = datas[param]
        return data

    def getResponse(self,method=None,**kwargs):
        """

        Основная функция для отправки запросов

        :param method: - Желаемый метод
        :param kwargs: - Данные для метода
        :return: - Вернет тело ответа
        """
        data = self.getData(kwargs)
        loop = asyncio.new_event_loop()
        request = loop.run_until_complete(self.getRequest(self.server,params=method,data=data))
        if request['status'] == 'error':
            raise MAVAPIError(request)
        else:
            return request

class API(Constructor):
    def __getattr__(self, method):
        """

        Класс-экземпляр, который нужен для некоторых махинаций
        с getattr и call

        :param method: - искомый метод, получить можно так:
                        -> self.method(**data)
        :return: - Что-то внизу вернет
        """
        return CallableObject(object=self, method=method)

class CallableObject():
    def __init__(self, object, method):
        self.api = object
        self.method = method

    def __call__(self, **data):
        return self.api.getResponse(method=self.method, **data)