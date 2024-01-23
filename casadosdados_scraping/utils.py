import pandas as pd


def to_excel(path, contacts):
    df = pd.DataFrame(columns=['Nome', 'Contato', 'Localização', 'CNAE'])
    for contact in contacts:
        df.loc[len(df)] = [
            contact['name'],
            contact['phone_number'],
            contact['location'],
            contact['cnae'],
        ]
    df.to_excel(path, index=False)
    return df
