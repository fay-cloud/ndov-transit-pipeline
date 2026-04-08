{{ config(schema='STAGING') }}

with source as (
    select * from {{ source('raw', 'raw_stop_times') }}
),

renamed as (
    select
        trip_id,
        stop_id,
        arrival_time,
        departure_time,
        try_cast(stop_sequence as integer) as stop_sequence,
        try_cast(
            split_part(departure_time, ':', 1) as integer
        ) as departure_hour
    from source
    where trip_id is not null
    and departure_time is not null
)

select * from renamed