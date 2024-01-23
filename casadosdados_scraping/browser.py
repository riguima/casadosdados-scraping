import re
from time import sleep

from httpx import Client
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    def __init__(self, headless=False):
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
        self.driver = Chrome(
            options=options, service=Service(ChromeDriverManager().install())
        )

    def get_states(self):
        return []

    def search(self, search_info):
        self.driver.get(
            'https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada'
        )
        menus = self.find_elements('.dropdown-menu')
        self.find_element('.is-4 .input.is-normal').send_keys(
            search_info['cnae']
        )
        self.click(self.find_element('.dropdown-item', element=menus[1]))
        self.find_element('.is-2 .input.is-normal').send_keys(
            search_info['state']
        )
        self.click(self.find_element('.dropdown-item', element=menus[3]))
        self.find_elements('.is-2 .input.is-normal')[1].send_keys(
            search_info['city']
        )
        self.click(self.find_element('.dropdown-item', element=menus[4]))
        self.find_element('input[placeholder="A partir de"]').send_keys(
            '01/01/2019'
        )
        self.click(self.find_element('.check.is-default'))
        self.click(self.find_element('.button'))
        urls = []
        while True:
            sleep(2)
            new_urls = [
                e.get_attribute('href') for e in self.find_elements('.box a')
            ]
            urls.extend(new_urls)
            disabled = self.find_elements('.pagination-next')[2].get_attribute(
                'disabled'
            )
            if disabled is not None:
                break
            self.click(self.find_elements('.pagination-next')[2])
        result = []
        for url in urls:
            print(url)
            with Client() as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
                }
                content = str(client.get(url, headers=headers).content)
            name_pattern = re.compile(r'razao_social:"(.+?)"', re.DOTALL)
            phone_number_pattern = re.compile(
                r'contato_telefonico:\[\{.+ddd:"(\d{2})",numero:"(\d+?)"',
                re.DOTALL,
            )
            if not phone_number_pattern.findall(content):
                phone_number_pattern = re.compile(
                    r'contato_telefonico:\[\{.+completo:"(\d{2})-(\d+)"',
                    re.DOTALL,
                )
            try:
                ddd, number = phone_number_pattern.findall(content)[0]
                name = name_pattern.findall(content)[0]
            except IndexError:
                continue
            phone_number = int(f'{ddd}{number}')
            result.append(
                {
                    'name': name,
                    'phone_number': phone_number,
                    'location': f'{search_info["city"]} - {search_info["state"]}',
                    'cnae': search_info['cnae'],
                }
            )
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
