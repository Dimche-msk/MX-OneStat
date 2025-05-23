import pandas as pd
import pyarrow
import glob
import os
import io  # Необходим для StringIO
import csv  # Необходим для csv.QUOTE_NONE


def load_all_dat_from_folder(folder_path):
    """
    Загружает все DAT-файлы (в формате CSV) из указанной папки в один pandas DataFrame,
    учитывая специфическую структуру заголовков, комментариев и специальных символов,
    и преобразует столбцы времени UTC в datetime объекты.
    Args:
        folder_path (str): Путь к папке с DAT-файлами.
    Returns:
        pandas.DataFrame: Объединенный DataFrame со всеми данными из DAT-файлов.
                          Возвращает пустой DataFrame, если файлы не найдены, папка не существует,
                          или не удалось обработать заголовки/данные.
    """
    if not os.path.isdir(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не найдена.")
        return pd.DataFrame()

    dat_pattern = os.path.join(folder_path, "*.dat")
    dat_files = glob.glob(dat_pattern)

    if not dat_files:
        print(f"В папке '{folder_path}' не найдено DAT-файлов.")
        return pd.DataFrame()

    list_of_dataframes = []
    column_names = None
    date_columns = ['start time UTC', 'stop time UTC', 'start time local', 'stop time local'] # Столбцы для преобразования в datetime

    # Извлечение имен столбцов из первого файла
    try:
        first_file_path = dat_files[0]
        with open(first_file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 6:  # 7-я строка файла (0-индексированная)
                    header_line = line.strip()
                    if header_line.startswith('#'):
                        header_line = header_line[1:].strip()
                    column_names = [col.strip() for col in header_line.split(',')]
                    break
        if column_names is None:
            print(f"Не удалось извлечь имена столбцов из первого файла: {first_file_path}. Проверьте структуру файла.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Ошибка при чтении заголовков из первого файла '{os.path.basename(dat_files[0])}': {e}")
        return pd.DataFrame()

    print(f"Найдены следующие DAT-файлы для загрузки (используются заголовки из {os.path.basename(dat_files[0])}):")
    for file_path in dat_files:
        print(f" - Чтение файла: {os.path.basename(file_path)}")
        try:
            processed_lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for _ in range(8): # Пропускаем первые 8 строк
                    try:
                        next(f)
                    except StopIteration:
                        break
                for line in f:
                    processed_line = line.replace('&amp;', '&')
                    processed_line = processed_line.replace('&comma;', ',') # Заменяем &comma; на обычную запятую
                    processed_lines.append(processed_line)

            if not processed_lines:
                print(f"   - Файл {os.path.basename(file_path)} не содержит данных после заголовка.")
                continue

            csv_data_string = "".join(processed_lines)

            df = pd.read_csv(
                io.StringIO(csv_data_string),
                sep=',',
                header=None,
                names=column_names,
                engine='python',
                quoting=csv.QUOTE_NONE,
                parse_dates=date_columns, # Преобразование столбцов в datetime
                on_bad_lines='warn'
            )
            df['duration'] = pd.to_timedelta(df['duration'], errors='coerce')
            df['calling number'] = pd.to_numeric(df['calling number'], errors='coerce')
            df['connected number'] = pd.to_numeric(df['connected number'], errors='coerce')
            df['charged number'] = pd.to_numeric(df['charged number'], errors='coerce')
            list_of_dataframes.append(df)
        except Exception as e:
            print(f"Ошибка при чтении или обработке файла '{os.path.basename(file_path)}': {e}")

    if not list_of_dataframes:
        print("Не удалось загрузить данные ни из одного файла.")
        return pd.DataFrame()

    combined_df = pd.concat(list_of_dataframes, ignore_index=True)

    # Проверка типов данных для столбцов времени UTC
    for col in date_columns:
        if col in combined_df.columns and not pd.api.types.is_datetime64_any_dtype(combined_df[col]):
            print(f"Предупреждение: Столбец '{col}' не был успешно преобразован в datetime. Текущий тип: {combined_df[col].dtype}")
            # Попытка принудительного преобразования, если parse_dates не справился (например, из-за смешанных форматов или ошибок)
            # combined_df[col] = pd.to_datetime(combined_df[col], errors='coerce')


    print(f"\nВсего загружено {len(list_of_dataframes)} DAT-файлов.")
    print(f"Итоговый DataFrame содержит {combined_df.shape[0]} строк и {combined_df.shape[1]} столбцов.")
    if all(col in combined_df.columns for col in date_columns):
        print("Типы данных для столбцов времени UTC после загрузки:")
        print(combined_df[date_columns].dtypes)

        # Гарантируем, что рабочие колонки/индекс имеют тип datetime
        # Если 'start time UTC' уже индекс:
        if combined_df.index.name == 'start time UTC':
            if not pd.api.types.is_datetime64_any_dtype(combined_df.index):
                print(f"Предупреждение: индекс 'start time UTC' не datetime. Попытка преобразования...")
                try:
                    combined_df.index = pd.to_datetime(combined_df.index, errors='coerce')
                except Exception as e:
                    print(f"Не удалось преобразовать индекс в datetime: {e}. Сброс индекса.")
                    combined_df.reset_index(inplace=True)
                    # Далее 'start time UTC' будет обработан как колонка

    # Обработка колонок

    required_cols = ['start time UTC', 'stop time UTC']
    for col in required_cols:
        if col in combined_df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                print(
                    f"Предупреждение в calculate_active_calls_per_minute: столбец '{col}' не datetime. Попытка преобразования...")
                combined_df[col] = pd.to_datetime(combined_df[col], errors='coerce')
        elif col == 'start time UTC' and combined_df.index.name == 'start time UTC':  # Уже обработан как индекс
            pass
        else:  # Колонка отсутствует и не является ожидаемым индексом
            print(f"Критическая ошибка: столбец '{col}' отсутствует и не является индексом.")
            return pd.DataFrame()


    # Проверяем колонки
    cols_to_check_for_na = [col for col in required_cols if col in combined_df.columns]
    if cols_to_check_for_na:
        combined_df.dropna(subset=cols_to_check_for_na, inplace=True)

    if combined_df.empty:
        print("Нет валидных данных о времени начала/окончания UTC звонков после проверки/преобразования.")
        return pd.DataFrame()


    return combined_df

def calculate_active_calls_per_minute(df):
    """
    Определяет количество активных звонков для каждой минуты на основе CDR данных.

    Args:
        df (pd.DataFrame): DataFrame с данными о звонках.
                           Обязательно должны присутствовать столбцы 'start time local' и 'stop time local'.

    Returns:
        pd.DataFrame: DataFrame с колонками 'Дата/Время' и 'Активные звонки'.
                      Возвращает пустой DataFrame в случае ошибки или отсутствия данных.
    """
    if df.empty:
        print("Входной DataFrame пуст.")
        return pd.DataFrame()

    required_cols = ['start time local', 'stop time local', 'start time UTC', 'stop time UTC']
    if not all(col in df.columns for col in required_cols):
        print(f"Ошибка: В DataFrame отсутствуют необходимые столбцы: {required_cols}")
        return pd.DataFrame()

    # 2. Создание полного временного диапазона
    min_overall_time = pd.to_datetime(df['start time UTC'].min())
    max_overall_time = pd.to_datetime(df['start time UTC'].max())

    if pd.isna(min_overall_time) or pd.isna(max_overall_time):
        print("Не удалось определить общий временной диапазон.")
        return pd.DataFrame()

    # Создаем временной ряд для каждого дня в диапазоне
    full_day_range = pd.date_range(start=min_overall_time, end=max_overall_time, freq='D')

    daily_call_counts_list = []
    for day_snapshot in full_day_range:
        df_for_day = df[df['start time UTC'].dt.date == day_snapshot.date()].copy()  # Используем .copy() для избежания SettingWithCopyWarning
        min_time = day_snapshot.replace(hour=0, minute=0, second=0)
        max_time = day_snapshot.replace(hour=23, minute=59, second=59)
        try:
            full_time_range = pd.date_range(start=min_time, end=max_time, freq='30min')
            print(f"\nАнализ активных звонков в диапазоне с {min_time} по {max_time}...")
            print(f"Количество минут для анализа: {len(full_time_range)}")
            max_count=0
            max_count_time = None
            for minute_snapshot in full_time_range:
                # Звонок активен, если: время начала звонка <= текущая минута < время окончания звонка
                # (время окончания > текущей минуты означает, что звонок еще не завершился к началу этой минуты)
                count = df[
                    (df['start time UTC'] <= minute_snapshot) &
                    (df['stop time UTC'] > minute_snapshot)
                    ].shape[0]
                if count > max_count:
                    max_count = count
                    max_count_time = minute_snapshot

            day_count = df_for_day.shape[0]
            total_duration_for_day = pd.NaT  # Значение по умолчанию

            # Рассчитываем сумму длительности, только если колонка 'duration' валидна и есть данные за день
            if 'duration' in df_for_day.columns and pd.api.types.is_timedelta64_dtype(
                    df_for_day['duration']) and not df_for_day.empty:
                # pd.to_timedelta уже должен был обработать ошибки, заменив их на NaT.
                # .sum() для Timedelta корректно обработает NaT (проигнорирует их, если есть другие значения,
                # или вернет NaT, если все значения NaT).
                # Если df_for_day['duration'] пуст, sum() вернет Timedelta('0 days')
                total_duration_for_day = df_for_day['duration'].sum()
                if pd.isna(total_duration_for_day) and not df_for_day['duration'].isnull().all():  # Если сумма NaT, но не все значения были NaT
                    total_duration_for_day = pd.Timedelta(0)  # или другое значение по умолчанию
                elif df_for_day.empty:  # Если за день не было звонков
                    total_duration_for_day = pd.Timedelta(0)

            daily_call_counts_list.append({
                'Дата': day_snapshot.date(),
                'Количество звонков за день': day_count,
                'Общая длительность за день (мин=*24*60)': total_duration_for_day,
                'Макс. одновременных звонков в ЧНН':max_count,
                'Время ЧНН (UTC)':max_count_time
            })
            print({
                'Дата': day_snapshot.date(),
                'Количество звонков за день': day_count,
                'Общая длительность за день': total_duration_for_day,
                'Макс. одновременных звонков в ЧНН':max_count,
                'Время ЧНН':max_count_time
            })
        except Exception as e:
            print (f'{day_snapshot} execution error: {e}')
    daily_summary_df = pd.DataFrame(daily_call_counts_list)

    if not daily_summary_df.empty:
        # Преобразуем столбец 'Дата' в datetime для единообразия
        daily_summary_df['Дата'] = pd.to_datetime(daily_summary_df['Дата'])
        daily_summary_df['Время ЧНН (UTC)'] = pd.to_datetime(daily_summary_df['Время ЧНН (UTC)'])
        print("\nСводка по количеству звонков за день:")
        print(daily_summary_df.head())
    else:
        print("\nНе удалось сформировать сводку по дням (возможно, full_day_range был пуст или исходный df).")
    print("Подсчет активных звонков завершен.")
    return  daily_summary_df


if __name__ == "__main__":
    folder_with_dat = "CDR/PY"  # Замените на ваш путь
    cache_file_path=f'{folder_with_dat}/all_data_cache.parquet'
    if os.path.exists(cache_file_path):
        print("Загрузка данных из кэш", cache_file_path)
        all_data = pd.read_parquet(cache_file_path, engine='pyarrow')
    else:

        all_data = load_all_dat_from_folder(folder_with_dat)
        print("Сохранение данных в кэш", cache_file_path)
        all_data.to_parquet(cache_file_path, engine='pyarrow')
    if all_data.empty:
        print("\nДанные не загружены.. Ошибка (Пустой датафрейм)")
        quit(0)
    active_calls_df = calculate_active_calls_per_minute(all_data)

    if not active_calls_df.empty:
        print("\nПервые 5 строк DataFrame с количеством активных звонков по минутам:")
        print(active_calls_df.head())
        print(f"\nВсего записей в результирующем DataFrame: {active_calls_df.shape[0]}")

        # Сохранение в Excel
        excel_output_path = os.path.join(folder_with_dat, "active_calls_per_minute.xlsx")
        try:
            # Для сохранения в Excel может потребоваться установить openpyxl: pip install openpyxl
            active_calls_df.to_excel(excel_output_path, index=False, engine='openpyxl')
            print(f"\nРезультат успешно сохранен в Excel файл: {excel_output_path}")
        except Exception as e:
            print(f"\nОшибка при сохранении в Excel: {e}")
            print("Убедитесь, что у вас установлена библиотека 'openpyxl': pip install openpyxl")
    else:
        print("\nНе удалось сформировать DataFrame с активными звонками.")
