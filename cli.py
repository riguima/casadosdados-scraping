from trends_contacts.use_cases import to_excel, search, create_driver
from trends_contacts.domain import SearchInfo


if __name__ == '__main__':
    cnaes = input('CNAES: ')
    state = input('Estado: ')
    city = input('Cidade: ')
    all_contacts = []
    for cnae in cnaes.split():
        search_info = SearchInfo(cnae, state, city)
        all_contacts.extend(search(create_driver(visible=True), search_info))
    to_excel('result.xlsx', all_contacts)
