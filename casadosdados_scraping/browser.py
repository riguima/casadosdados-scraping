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
        self.driver.get(
            'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        )
        self.find_elements('.input.is-is-normal')[1].click()
        dropdown_menu = self.find_elements('.dropdown-menu')[1]
        while True:
            result = [
                item.text
                for item in self.find_elements(
                    '.dropdown-item', element=dropdown_menu
                )
            ]
            if '' not in result:
                break
        return result

    def get_states(self):
        self.driver.get(
            'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        )
        self.find_elements('.input.is-is-normal')[3].click()
        dropdown_menu = self.find_elements('.dropdown-menu')[3]
        while True:
            result = [
                item.text
                for item in self.find_elements(
                    '.dropdown-item', element=dropdown_menu
                )
            ]
            if '' not in result:
                break
        return result

    @cache
    def get_cities(self, state):
        index = self.get_states().index(state)
        dropdown_menu = self.find_elements('.dropdown-menu')[3]
        self.find_elements('.dropdown-item', element=dropdown_menu)[
            index
        ].click()
        self.find_element('.input.is-normal').click()
        dropdown_menu = self.find_elements('.dropdown-menu')[4]
        while True:
            result = [
                item.text.title()
                for item in self.find_elements(
                    '.dropdown-item', element=dropdown_menu
                )
            ]
            if '' not in result:
                break
        return result

    def search(self, search_info):
        self.driver.get(
            'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        )
        menus = self.find_elements('.dropdown-menu')
        self.find_elements('.input.is-is-normal')[1].send_keys(
            search_info['cnae']
        )
        self.click(self.find_element('.dropdown-item', element=menus[1]))
        self.find_elements('.input.is-is-normal')[3].send_keys(
            search_info['state']
        )
        self.click(self.find_element('.dropdown-item', element=menus[3]))
        self.find_element('.input.is-normal').send_keys(search_info['city'])
        self.click(self.find_element('.dropdown-item', element=menus[4]))
        self.click(self.find_element('.button.is-success'))
        urls = self.get_contacts_urls_of_page()
        return [self.get_contact_info(url) for url in urls]

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
                    print(info.css('p::text').get(), info.css('a::text').get())
                    if info.css('a'):
                        result[info.css('p::text').get()] = info.css('a::text').get()
                    else:
                        result[info.css('p::text').get()] = info.css('p::text')[1].get()
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
