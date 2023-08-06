# -*- coding: utf-8 -*-
"""
Scrapbag censal file.
"""
import os
from .csvs import csv_tolist
from .strings import normalizer

import structlog

logger = structlog.getLogger(__name__)

DEFAULT_DATA_PATH = os.path.join(
    "/".join(os.path.abspath(__file__).split('/')[:-1]),
    'data-aux/18codmun.csv')


class IneCensal():

    index = {}

    def __init__(self, **kwargs):

        # load Ine file data
        lista = self.load_data(**kwargs)

        # generate the index
        self.index = self.make_index(lista)

    def load_data(self, path=DEFAULT_DATA_PATH, **kwargs):

        return csv_tolist(path, delimiter=';')

    def make_index(self, lista):

        ine_censo_index = {}

        # first row is headers
        for censo_data in lista[1:]:
            try:
                c_data = None

                # In ine file data, there are some rows with this pattern,
                # 'florida, La' and we want to change to 'La florida'

                if ',' in censo_data[4]:
                    c_data = " ".join(censo_data[4].split(', ')[::-1])
                else:
                    c_data = censo_data[4]

                ine_censo_index[normalizer(c_data)] = "".join(censo_data[1:3])

            except Exception as ex:
                logger.error('Fail to make index with parsed row data {} - {}'.format(censo_data, ex))

        return ine_censo_index

    def get_codigo_censal(self, localidad_name, without_codigo_censal=set()):

        # assert input name normalizer
        localidad_name = normalizer(localidad_name)

        codigo_censal = self.index.get(localidad_name, None)

        if not codigo_censal:
            result_key = None
            search_data = list(self.index.keys())

            if localidad_name not in without_codigo_censal:

                for name_word in localidad_name.split('-'):
                    logger.debug('*Searching {}'.format(localidad_name))

                    if len(search_data) == 1:

                        # same word lenght
                        if len(search_data[0].split('-')) == len(localidad_name.split('-')):
                            result_key = search_data[0]
                            logger.debug('*** Found codigo censal: {}'.format(result_key))

                        break

                    if not search_data:
                        break

                    for search_name in iter(search_data):
                        if name_word not in search_name:
                            search_data.remove(search_name)

            if result_key is None:
                without_codigo_censal.add(localidad_name)
                logger.error('* -- Fail Searching codigo_censal {}'.format(localidad_name))

        return codigo_censal
