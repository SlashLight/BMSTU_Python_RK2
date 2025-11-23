import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    # Подготовка данных
    df = pd.DataFrame(data_list)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    df['daily_change'] = df['tickets_created'] - df['tickets_resolved']
    df['total_active_tickets'] = df['daily_change'].cumsum()

    print("\nПример рассчитанных данных (последние 5 дней):")
    print(df[['date', 'tickets_created', 'tickets_resolved', 'total_active_tickets',
              'satisfaction_rate']].tail(30).to_string())

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle(f'Анализ нагрузки и качества работы отдела ({LOGIN})', fontsize=16)

    # --- ГРАФИК 1: Рост нагрузки на отдел ---
    sns.lineplot(
        data=df,
        x='date',
        y='total_active_tickets',
        marker='o',
        linewidth=2.5,
        color='tab:red',
        ax=axes[0]
    )

    axes[0].bar(df['date'], df['tickets_created'], color='gray', alpha=0.3, label='Новые заявки (шт)')

    axes[0].set_title('Динамика нагрузки на отдел (Backlog)')
    axes[0].set_xlabel('Дата')
    axes[0].set_ylabel('Количество активных (нерешенных) тикетов')
    axes[0].legend(['Накопленный долг', 'Новые заявки за день'])
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, linestyle='--')

    # --- ГРАФИК 2: Корреляция ---
    sns.regplot(
        data=df,
        x='total_active_tickets',
        y='satisfaction_rate',
        scatter_kws={'s': 80, 'alpha': 0.6, 'color': 'blue'},
        line_kws={'color': 'darkred', 'linewidth': 2},
        ci=95,
        ax=axes[1]
    )

    corr = df['total_active_tickets'].corr(df['satisfaction_rate'])

    axes[1].set_title(f'Влияние нагрузки на удовлетворенность (Корреляция: {corr:.2f})')
    axes[1].set_xlabel('Накопленный объем нерешенных тикетов')
    axes[1].set_ylabel('Удовлетворенность (%)')
    axes[1].legend([f'Данные', 'Линия тренда'])
    axes[1].grid(True, linestyle='--')

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()