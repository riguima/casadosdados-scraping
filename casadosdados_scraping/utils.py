import pandas as pd


def to_excel(path, contacts):
    headers = [
        'CNPJ',
        'Razão Social',
        'Nome Fantasia',
        'Tipo',
        'Data Abertura',
        'Situação Cadastral',
        'Data da Situação Cadastral',
        'Capital Social',
        'Natureza Jurídica',
        'Empresa MEI',
        'Logradouro',
        'Número',
        'Complemento',
        'CEP',
        'Bairro',
        'Município',
        'UF',
        'Telefone',
        'E-MAIL',
        'Quadro Societário',
        'Atividade Principal',
        'Atividades Secundárias',
        'Data da Consulta',
        'URL',
    ]
    df = pd.DataFrame(columns=headers)
    for contact in contacts:
        df.loc[len(df)] = {header: contact[header] for header in headers}
    df.to_excel(path, index=False)
    return df
