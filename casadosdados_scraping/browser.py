from functools import cache
from time import sleep

import undetected_chromedriver as uc
from httpx import Client
from parsel import Selector
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Browser:
    def __init__(self, headless=False):
        self.driver = uc.Chrome(headless=headless, use_subprocess=False)

    def get_cnaes(self):
        url = 'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        if url != self.driver.current_url:
            self.driver.get(url)
        self.find_elements('.input.is-is-normal')[1].click()
        dropdown = self.find_elements('.dropdown-menu')[1]
        return self.get_dropdown_items(dropdown)

    def get_juridical_nature(self):
        url = 'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        if url != self.driver.current_url:
            self.driver.get(url)
        self.find_elements('.input.is-is-normal')[2].click()
        dropdown = self.find_elements('.dropdown-menu')[2]
        return self.get_dropdown_items(dropdown)

    def get_states(self):
        url = 'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        if url != self.driver.current_url:
            self.driver.get(url)
        self.find_elements('.input.is-is-normal')[3].click()
        dropdown = self.find_elements('.dropdown-menu')[3]
        return self.get_dropdown_items(dropdown)

    def select_state(self, state):
        index = self.get_states().index(state)
        dropdown = self.find_elements('.dropdown-menu')[3]
        self.find_elements('.dropdown-item', element=dropdown)[index].click()

    @cache
    def get_cities(self, state):
        self.select_state(state)
        self.find_element('.input.is-normal').click()
        dropdown = self.find_elements('.dropdown-menu')[4]
        return self.get_dropdown_items(dropdown)

    def get_dropdown_items(self, dropdown):
        while True:
            result = [
                item.text
                for item in self.find_elements(
                    '.dropdown-item', element=dropdown
                )
            ]
            if '' not in result:
                break
        return result

    def search(self, search_info):
        self.driver.get(
            'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        )
        self.check_options(search_info)
        self.fill_inputs(search_info)
        self.fill_inputs_with_dropdown(search_info)
        self.fill_date_inputs(search_info)
        self.click(self.find_element('.button.is-success'))
        urls = self.get_contacts_urls_of_page()
        return [self.get_contact_info(url) for url in urls]
    
    def check_options(self, search_info):
        options = [
            'includes_secondary_activity',
            'only_mei',
            'remove_mei',
            'only_matriz',
            'only_filial',
            'with_phone_number',
            'only_phone',
            'only_smartphone',
            'with_email',
        ]
        for e, option in enumerate(options):
            if search_info[option]:
                self.click(self.find_elements('.check')[e])

    def fill_inputs(self, search_info):
        self.find_element('.input.is-is-normal').send_keys(search_info['fantasy_name'])
        self.find_elements('.input.is-normal')[1].send_keys(search_info['neighborhood'])
        self.find_elements('.input.is-normal')[2].send_keys(search_info['cep'])
        self.find_elements('.input.is-normal')[3].send_keys(search_info['ddd'])
        self.find_element('.input.is-info').send_keys(search_info['from_share_capital'])
        self.find_elements('.input')[11].send_keys(search_info['to_share_capital'])

    def fill_inputs_with_dropdown(self, search_info):
        infos = [
            'cnae',
            'juridical_nature',
            'state'
        ]
        menus = self.find_elements('.dropdown-menu')
        for e, info in enumerate(infos):
            self.find_elements('.input.is-is-normal')[e + 1].send_keys(
                search_info[info]
            )
            self.click(self.find_element('.dropdown-item', element=menus[e + 1]))
        self.find_element('.input.is-normal').send_keys(search_info['city'])
        self.click(self.find_element('.dropdown-item', element=menus[4]))

    def fill_date_inputs(self, search_info):
        pass

    def get_contacts_urls_of_page(self):
        result = []
        try:
            while True:
                sleep(2)
                urls = [
                    e.get_attribute('href')
                    for e in self.find_elements('.box a')
                ]
                result.extend(urls)
                try:
                    self.find_element('.pagination-next.is-disabled', wait=5)
                except TimeoutException:
                    self.click(self.find_elements('.pagination-next')[1])
                    continue
                break
        except TimeoutException:
            return result
        return result

    def get_contact_info(self, url):
        with Client() as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
            }
            selector = Selector(client.get(url, headers=headers).text)
            result = {}
            for info in selector.css('.is-narrow'):
                try:
                    if info.css('a'):
                        result[info.css('p::text').get()] = info.css(
                            'a::text'
                        ).get()
                    else:
                        result[info.css('p::text').get()] = info.css(
                            'p::text'
                        )[1].get()
                except IndexError:
                    result[info.css('p::text').get()] = ''
            result['Nome Fantasia'] = result.get('Nome Fantasia', '')
            result['Telefone'] = result.get('Telefone', '')
            result['Quadro Societário'] = result.get('Quadro Societário', '')
            result['Atividades Secundárias'] = result.get(
                'Atividades Secundárias', ''
            )
            result['URL'] = url
            return result

    def find_element(self, selector, element=None, wait=20):
        element = element or self.driver
        return WebDriverWait(element, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def find_elements(self, selector, element=None, wait=20):
        element = element or self.driver
        return WebDriverWait(element, wait).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )

    def click(self, element):
        self.driver.execute_script('arguments[0].click();', element)
