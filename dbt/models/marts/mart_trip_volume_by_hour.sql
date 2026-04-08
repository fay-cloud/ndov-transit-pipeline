{{ config(
    materialized='table',
    schema='MARTS'
) }}

with stop_times as (
    select * from {{ ref('stg_stop_times') }}
),

trips as (
    select * from {{ ref('stg_trips') }}
),

calendar as (
    select * from {{ ref('stg_calendar_dates') }}
),

trip_hours as (
    select
        st.departure_hour,
        dayofweek(c.service_date) as day_of_week,
        dayname(c.service_date) as day_name,
        count(distinct st.trip_id) as total_trips
    from stop_times st
    inner join trips t on st.trip_id = t.trip_id
    inner join calendar c on t.service_id = c.service_id
    where st.departure_hour between 0 and 23
    and c.exception_type = 1
    group by st.departure_hour, dayofweek(c.service_date), dayname(c.service_date)
)

select * from trip_hours
order by day_of_week, departure_hour