import pandas as pd
from collections import Counter

from mainStatistics.models import Profession

def main():
    df = pd.read_csv('pupa.csv',  low_memory=False)

    keywords = [
        'web develop', 'веб разработчик', 'web разработчик', 'web programmer',
        'web программист', 'веб программист', 'битрикс разработчик',
        'bitrix разработчик', 'drupal разработчик', 'cms разработчик',
        'wordpress разработчик', 'wp разработчик', 'joomla разработчик',
        'drupal developer', 'cms developer', 'wordpress developer',
        'wp developer', 'joomla developer'
    ]
    pattern = '|'.join(keywords)

    # Фильтруем DataFrame
    filtered_df = df[df['name'].str.contains(pattern, case=False, na=False)]
    filtered_df = filtered_df.dropna()
    objects = [Profession(**row) for index, row in filtered_df.iterrows()]

    # Сохранение объектов в базе данных
    Profession.objects.bulk_create(objects)