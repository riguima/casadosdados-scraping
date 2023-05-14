from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
from time import sleep
import re

from trends_contacts.domain import SearchInfo, Contact


def create_driver(visible: bool = False) -> Chrome:
    options = Options()
    if not visible:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
    return Chrome(
        options=options, service=Service(ChromeDriverManager().install()))


def search(driver: Chrome, search_info: SearchInfo) -> list[Contact]:
    driver.get('https://casadosdados.com.br/solucao/cnpj/pesquisa-avancada')
    menus = find_elements(driver, '.dropdown-menu')
    find_element(driver, '.is-4 .input.is-normal').send_keys(search_info.cnae)
    click(driver, menus[1].find_element(By.CSS_SELECTOR, '.dropdown-item'))
    find_element(driver, '.is-2 .input.is-normal').send_keys(search_info.state)
    click(driver, menus[3].find_element(By.CSS_SELECTOR, '.dropdown-item'))
    find_elements(driver, '.is-2 .input.is-normal')[1].send_keys(
        search_info.city)
    click(driver, menus[4].find_element(By.CSS_SELECTOR, '.dropdown-item'))
    find_element(driver, 'input[placeholder="A partir de"]').send_keys(
        '01/01/2019')
    click(driver, find_element(driver, '.check.is-default'))
    click(driver, find_element(driver, '.button'))
    urls = []
    while True:
        sleep(2)
        new_urls = [
            e.get_attribute('href') for e in find_elements(driver, '.box a')
        ]
        urls.extend(new_urls)
        disabled = find_elements(driver, '.pagination-next')[2].get_attribute(
            'disabled')
        if disabled is not None:
            break
        click(driver, find_elements(driver, '.pagination-next')[2])
    result = []
    for url in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        content = str(requests.get(url, headers=headers).content)
        name_pattern = re.compile(r'razao_social:"(.+?)"', re.DOTALL)
        phone_number_pattern = re.compile(
            r'contato_telefonico:\[\{.+ddd:"(\d{2})",numero:"(\d+?)"',
            re.DOTALL
        )
        if not phone_number_pattern.findall(content):
            phone_number_pattern = re.compile(
                r'contato_telefonico:\[\{.+completo:"(\d{2})-(\d+)"',
                re.DOTALL
            )
        try:
            ddd, number = phone_number_pattern.findall(content)[0]
            name = name_pattern.findall(content)[0]
        except IndexError:
            continue
        phone_number = int(f'{ddd}{number}')
        result.append(
            Contact(name, phone_number,
                    f'{search_info.city} - {search_info.state}',
                    search_info.cnae)
        )
    return result


def to_excel(path: str, contacts: list[Contact]) -> pd.DataFrame:
    df = pd.DataFrame(columns=['Nome', 'Contato', 'Localização', 'CNAE'])
    for contact in contacts:
        df.loc[len(df)] = [
            contact.name, contact.phone_number, contact.location, contact.cnae
        ]
    df.to_excel(path, index=False)
    return df


def find_element(driver: Chrome, selector: str, wait: int = 20):
    return WebDriverWait(driver, wait).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def find_elements(driver: Chrome, selector: str, wait: int = 20):
    return WebDriverWait(driver, wait).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )


def click(driver: Chrome, element) -> None:
    driver.execute_script('arguments[0].click();', element)
