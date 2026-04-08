{{ config(schema='STAGING') }}

with source as (
    select * from {{ source('raw', 'raw_stops') }}
),

renamed as (
    select
        stop_id,
        stop_name,
        try_cast(stop_lat as float) as stop_lat,
        try_cast(stop_lon as float) as stop_lon,
        location_type,
        parent_station
    from source
    where stop_id is not null
)

select * from renamed