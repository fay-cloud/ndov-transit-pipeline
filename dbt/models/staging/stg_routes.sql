{{ config(schema='STAGING') }}

with source as (
    select * from {{ source('raw', 'raw_routes') }}
),

renamed as (
    select
        route_id,
        agency_id,
        route_short_name,
        route_long_name,
        try_cast(route_type as integer) as route_type
    from source
    where route_id is not null
)

select * from renamed