from sqlalchemy import create_engine, text
import pandas as pd

# выгрузка заявок
def new_data():
    conn_str = "mssql+pyodbc://log:pas@localhost/db?driver=SQL+Server"
    engine = create_engine(conn_str)
    data = pd.read_sql_query("""select top(5)* from dms..Output_vector_ml with(nolock) order by created desc""", engine)
    #data1 = pd.read_sql_query("""select top(1)* from dms..Output_vector_ml with(nolock) where typeid=7 order by created desc """, engine)

    return data

# считаем пдн
def PDN_80():
    conn_str = "mssql+pyodbc://log:pas@localhost/db?driver=SQL+Server"
    engine = create_engine(conn_str)
    pdn80 = pd.read_sql_query("""select 
	cast((select sum([Сумма займа ЦБ]) sum_high_pdn 
from 
	RISK_REPORT.dbo.MPL_1q25 with(nolock)
where 
	cast(DATEADD(DD,-3,GETDATE()) as date) <= dtStart
    and pdn > 0.8 and flag_future_collateral = 0
)
/
(
select 
	sum([Сумма займа ЦБ]) sum_high_pdn 
from 
	RISK_REPORT.dbo.MPL_1q25 with(nolock)
where 
	cast(DATEADD(DD,-3,GETDATE() ) as date) <= dtStart
	) as real)
""", engine)
    pdn_80=pdn80.values[0][0]

    return round(pdn_80, 5).astype(float)

def PDN_50_80():
    conn_str = "mssql+pyodbc://log:pas@localhost/db?driver=SQL+Server"
    engine = create_engine(conn_str)
    pdn50 = pd.read_sql_query("""select 
cast(
(
select 
    sum([Сумма займа ЦБ]) sum_high_pdn 
from 
    RISK_REPORT.dbo.MPL_1q25 with(nolock)
where 
    cast(DATEADD(DD,-3,GETDATE()) as date) <= dtStart
    and pdn > 0.5 and pdn <= 0.8 and flag_future_collateral = 0
)
/
(
select 
    sum([Сумма займа ЦБ]) sum_high_pdn 
from 
    RISK_REPORT.dbo.MPL_1q25 with(nolock)
where 
    cast(DATEADD(DD,-3,GETDATE() ) as date) <= dtStart
) as real)
""", engine)
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
    tresh = [5.2, 16.4, 16.4, 17, 7.4, 6, 6, 5.4, 3.6, 3.4, 6.8, 9.4, 10.6, 15.8, 13, 1.4]
    dict_tresh = dict(zip(servis, tresh))

    df = pd.DataFrame.from_records([dict_tresh]).T
    df['ExternalService'] = df.index
    df['tresh'] = df[0].copy()
    df = df.reset_index()
    df1 = df[['ExternalService', 'tresh']].copy()
    return df1

#сервисы
def services():
    conn_str = "mssql+pyodbc://log:pas@localhost/db?driver=SQL+Server"
    engine = create_engine(conn_str)
    try:
        with engine.connect() as conn:
            conn.execute(text('''

if object_id('tempdb..#res') is not null drop table #res
select
    *
into #res
from (
select 
    f_l.[dtInsert] first_log_dt, 
    case when f.[dt принятия решения] > log.dtinsert then log.dtinsert else isnull(f.[dt принятия решения], log.dtinsert) end min_dt_end_paylater,
    datediff(second, f_l.[dtInsert], (case when f.[dt принятия решения] > log.dtinsert then log.dtinsert else isnull(f.[dt принятия решения], log.dtinsert) end)) as sec_decision, -- сколько секунд принималось решение (включая пэйлейтер с его сервисами)
    p_s.*,
    ROW_NUMBER () over (partition by p_s.OrderId order by p_s.approved desc ) Appr_num,
    ROW_NUMBER () over (partition by p_s.OrderId order by p_s.funded desc ) Fundr_num,
    case when p_s.dt_month='20231031' and p_s.Checks='AutoApprove' and p_s.channel='Аэрофлот' and ExternalService='Juicy' then 1 else 0 end ind,
    case when p_s.ExternalService='NBKI' and p_s.dt_month='20231031'  and p_s.AvgSeconds>10 then 5 
            when      p_s.ExternalService='NalogRu' and p_s.dt_month='20231031'  and AvgSeconds>10 then 5 
            when      p_s.ExternalService='BankruptService' and p_s.dt_month='20231031'  and p_s.AvgSeconds>10 then 2 
            when      p_s.ExternalService='Facecloud' and p_s.dt_month='20231031'  and p_s.AvgSeconds>10 then 2 
    else AvgSeconds end AvgSeconds1
From 
    [Risk_report].dbo.proccesing_service   p_s with(nolock)
    left join pl_int.[scr].[SolutionQueue] pl  with(nolock) on pl.OrderId = p_s.OrderId
    left join db..Applications        a   with(nolock) on a.id = pl.OrderId 
    left join (
            select
                AppId
                ,ClientId
                ,min(dtInsert) [dt принятия решения]
            from 
                db..LogAction log with(nolock)
            where 
                StatusId in (4,5,6)
            -- 5 отказ
            -- 6 предодобрение
            -- 4 одобрение
            -- хз где sprav
            group by 
                AppId, ClientId)                      f on f.AppId = a.id 
    left join (select
                    log.AppId
                    ,log.ClientId
                    ,min(log.dtInsert) [dtInsert]
                from 
                    db..LogAction log with(nolock)
                    left join db..Applications ap on ap.id = log.AppId
                where 
                    cast(log.dtInsert as date) = cast(ap.dtInput as date)
                group by 
                    log.AppId, log.ClientId)                   f_l  on f_l.AppId = a.id 
    left join dbService..ServiceApplication       s_ap with(nolock) on s_ap.db_AppId = a.id
    left join dbService.[dbo].[LogService]        log with(nolock) on log.Service_AppId = s_ap.id and log.StatusId = 7 
where 
    dt>='20230101' and (case when dt_month='20231031' and Checks='AutoApprove' and channel='Аэрофлот' and ExternalService='Juicy' then 1 else 0 end )=0
) res'''))
            data = pd.read_sql_query(text("""
declare @requests_number int = 10
;with good_services as (
    select que.ExternalService, max(n_req) req_day -- количество запросов за прошлый день
    from (
        select *, row_number() over (partition by r.ExternalService order by orderid desc) n_req
        from #res r
        where dt = cast(DATEADD(DD,-1,GETDATE() ) as date)
    ) que 
    group by que.ExternalService
    having max(n_req) >= @requests_number -- запросы от сервисов были за прошлый день и количество запросов за день >= 10
)

--if value >= value.threshold then alert "{value} avg seconds is high in last 10 requests yesterday!"
select ExternalService, round(avg(AvgSeconds1), 3) avg_sec -- средняя длительность выполнения сервисов за вчерашний день  при условии что сервис совершил минимум 10 запросов
from (
    select *, row_number() over (partition by r.ExternalService order by orderid desc) n_req
    from #res r
    where ExternalService in (select ExternalService from good_services)
) que 
where dt = cast(DATEADD(DD,-1,GETDATE() ) as date)
group by ExternalService
            """), conn)

    except Exception as e:
        print("\nAn error occurred: {0}.".format(str(e)))

    finally:
        conn.close()
    cutt = cutoff_services()
    req = data.merge(cutt, how='inner', on='ExternalService')
    req['flg'] = req['avg_sec'].ge(req['tresh'])
    req['diff'] = round(req['avg_sec']/req['tresh'], 3)

    return req


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

def services_for_report():
    data=services()
    if len(data.loc[data.flg.eq(True)])==0:
        text1 = "Нет задержек по сервисам"
        return text1
    else:
        for i in data.loc[data.flg.eq(True)].iterrows():
            text1 = "Задержка ответа по сервису:  " + str(data.loc[i[0], 'ExternalService'])+ " Максимальное допустимое значение: " + \
                    str(data.loc[i[0], 'tresh'])
            return text1

