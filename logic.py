from sqlalchemy import create_engine, text
import pandas as pd
import re
import subprocess
from dotenv import load_dotenv
import os
load_dotenv()
host = os.getenv("db_host")
psw = os.getenv("db_pass")
log = os.getenv("db_log")

#мои модельки
def crash_process():
    r = subprocess.getoutput('wmic process where "name like "python%"" get processid,commandline')
    target_dirs = [
        'console',
        'console_all',
        'console_crimea',
        'console_nerez',
        'console_antifraud'
    ]
    lines = [line for line in r.split('\n') if line.strip()]

    # Пропускаем заголовки (первые две строки)
    processed_lines = []
    for line in lines:
        # Ищем числовой ProcessId в конце строки
        match = re.search(r'(\d+)\s*$', line)
        if match:
            pid = match.group(1)
            # Извлекаем CommandLine (всё до начала ProcessId, убирая пробелы в конце)
            cmd_line = line[:match.start()].rstrip()
            processed_lines.append([cmd_line, int(pid)])

    df = pd.DataFrame(processed_lines, columns=['CommandLine', 'ProcessId'])

    # Создаем регулярное выражение для поиска
    pattern = r"console_test\\(?:" + "|".join(target_dirs) + r")\\"

    # Фильтруем строки, содержащие нужные поддиректории
    filtered_df = df[df['CommandLine'].str.contains(pattern, regex=True)].copy()

    # Извлекаем названия поддиректорий
    filtered_df['SubDir'] = filtered_df['CommandLine'].str.extract(
        r"console_test\\([^\\]+)",
        expand=False
    )

    # Получаем список уникальных поддиректорий
    subdir_list = filtered_df['SubDir'].unique().tolist()
    missing_dirs = [dir for dir in target_dirs if dir not in subdir_list]
    return missing_dirs

# выгрузка заявок
def new_data():
    conn_str = f"mssql+pyodbc://{log}:{psw}@{host}/Billing?driver=SQL+Server"
    engine = create_engine(conn_str)
    data = pd.read_sql_query("""select top(5)* from dms..Output_vector_ml with(nolock) order by created desc""", engine)
    return data

# выгружаем ошибки по звонкам
def collector_calls():
    conn_str = f"mssql+pyodbc://{log}:{psw}@{host}/Billing?driver=SQL+Server"
    engine = create_engine(conn_str)
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(q1, conn)

    except Exception as e:
        print("\nAn error occurred: {0}.".format(str(e)))
    finally:
        conn.close()
    return df

# считаем пдн
def PDN_80():
    conn_str = f"mssql+pyodbc://{log}:{psw}@{host}/Billing?driver=SQL+Server"
    engine = create_engine(conn_str)
    pdn80 = pd.read_sql_query(q4, engine)
    pdn_80=pdn80.values[0][0]

    return round(pdn_80, 5).astype(float)

def PDN_50_80():
    conn_str = f"mssql+pyodbc://{log}:{psw}@{host}/Billing?driver=SQL+Server"
    engine = create_engine(conn_str)
    pdn50 = pd.read_sql_query(q0, engine)
    pdn_50=pdn50.values[0][0]
    return round(pdn_50, 5).astype(float)

def PDN():
    cutoff=0.031
    pdn50=PDN_50_80()
    pdn80=PDN_80()
    return pdn50.astype(float)

def cutoff_services():
    servis = ['BankruptService', 'Equifax', 'Facecloud', 'Juicy', 'LazyScore', 'MailRu', 'Megafon', 'MLModel',
              'MLModelAll', 'MLModelCrimea', 'MLModelRepeated', 'MTS', 'NalogRu', 'NBKI', 'PassportReader', 'SMEV']
    tresh = [2.6, 8.2, 8.2, 8.5, 3.7, 3, 3, 2.7, 1.8, 1.7, 3.4, 4.7, 5.3, 7.9, 6.5, 0.7]

    dict_tresh = dict(zip(servis, tresh))

    df = pd.DataFrame.from_records([dict_tresh]).T
    df['ExternalService'] = df.index
    df['tresh'] = df[0].copy()
    df = df.reset_index()
    df1 = df[['ExternalService', 'tresh']].copy()
    return df1

#сервисы
def services():

    conn_str = f"mssql+pyodbc://{log}:{psw}@{host}/Billing?driver=SQL+Server"
    engine = create_engine(conn_str)
    try:
        with engine.connect() as conn:
            data_OK = pd.read_sql_query(query1, conn)
            data_time = pd.read_sql_query(query12, conn)
    except Exception as e:
        print("\nAn error occurred: {0}.".format(str(e)))

    finally:
        conn.close()
    return data_OK, data_time



def pdn_for_report():
    cutoff=0.03
    cutoff1=0.15

    pdn50 = PDN_50_80()
    pdn80 = PDN_80()
    diff50=round(pdn50-cutoff1, 5)
    diff80=round(pdn80-cutoff, 5)

    if (pdn50>cutoff1)|(pdn50==cutoff1):
        text0 ="PDN50-80 ="+str(round(pdn50*100, 2))+ "% .Превышение на "+str(round(diff50*100, 2))+ " за последние 3 дня"
    else:
        text0 ="PDN50-80 = "+str(round(pdn50*100, 2))+"% . В норме за последние 3 дня"
    if (pdn80>cutoff)|(pdn80==cutoff):
        text ="PDN80+ = "+str(round(pdn80*100, 2))+"% .Превышение на "+str(round(diff80*100, 2))+" за последние 3 дня"
    else:
        text ="PDN80+ = "+str(round(pdn80*100, 2))+"% . В норме за последние 3 дня"
    return text0, text



