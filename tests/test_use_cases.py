import pytest
from selenium.webdriver import Chrome
import pandas as pd

from trends_contacts.domain import SearchInfo, Contact
from trends_contacts.use_cases import search, create_driver, to_excel


@pytest.fixture(scope='module')
def driver() -> Chrome:
    return create_driver(visible=True)


@pytest.fixture(scope='module')
def contacts(driver) -> list[Contact]:
    search_info = SearchInfo('4923001', 'São Paulo', 'Itupeva')
    return search(driver, search_info)


def test_search(contacts) -> None:
    expected = [
        Contact('MARIA BENEDITA DOS SANTOS CARNEIRO', 1195827126,
                'Itupeva - São Paulo'),
        Contact('42.647.389 LOURIVAL APARECIDO MONTOVANI', 1199929985,
                'Itupeva - São Paulo'),
    ]
    assert contacts == expected


def test_search_with_multiples_pages(driver) -> None:
    search_info = SearchInfo('3101200', 'Mato Grosso', 'Cuiaba')
    assert len(search(driver, search_info)) > 50


def test_to_excel(contacts) -> None:
    df = to_excel('tests/result.xlsx', contacts)
    assert df.equals(pd.read_excel('tests/expected.xlsx'))
