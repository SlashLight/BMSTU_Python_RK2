import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Используем данные Отдела баз данных
BASE_URL = "http://193.233.171.205:5000"
LOGIN = "analyst_db"
CODE = "PqR67zAb89St"


def main():
    print(f"Получение данных для {LOGIN}...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/timeline",
            params={"login": LOGIN, "code": CODE, "days": 30}
        )
        response.raise_for_status()
        data_list = response.json().get('data', [])
    except Exception as e:
        print(f"Ошибка: {e}")
        return

    if not data_list:
        print("Данные пустые.")
        return

    df = pd.DataFrame(data_list)
    df['date'] = pd.to_datetime(df['date'])

    df = df.sort_values('date')

    df['daily_change'] = df['tickets_created'] - df['tickets_resolved']

    df['total_active_tickets'] = df['daily_change'].cumsum()

    print("\nПример рассчитанных данных:")
    print(df[['date', 'tickets_created', 'tickets_resolved', 'total_active_tickets',
              'satisfaction_rate']].head(30).to_string())

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    # Ось X: Общее количество активных тикетов (накопленное)
    # Ось Y: Удовлетворенность
    sns.regplot(
        data=df,
        x='total_active_tickets',
        y='satisfaction_rate',
        scatter_kws={'s': 80, 'alpha': 0.6, 'color': 'blue'},
        line_kws={'color': 'red', 'linewidth': 2},
        ci=95
    )

    plt.title('Влияние общего количества активных тикетов на удовлетворенность')
    plt.xlabel('Накопленный объем нерешенных тикетов (относительно начала периода)')
    plt.ylabel('Удовлетворенность (%)')

    # Вычисляем коэффициент корреляции
    corr = df['total_active_tickets'].corr(df['satisfaction_rate'])
    plt.legend([f'Линия тренда', f'Корреляция: {corr:.2f}'])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()