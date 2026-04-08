{{ config(schema='STAGING') }}

with source as (
    select * from {{ source('raw', 'raw_trips') }}
),

renamed as (
    select
        trip_id,
        route_id,
        service_id,
        trip_headsign,
        direction_id
    from source
    where trip_id is not null
)

select * from renamed