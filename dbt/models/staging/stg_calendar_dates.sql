{{ config(schema='STAGING') }}

with source as (
    select * from {{ source('raw', 'raw_calendar_dates') }}
),

renamed as (
    select
        service_id,
        to_date(date, 'YYYYMMDD') as service_date,
        try_cast(exception_type as integer) as exception_type
    from source
    where service_id is not null
)

select * from renamed