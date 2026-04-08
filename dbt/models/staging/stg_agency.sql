{{ config(schema='STAGING') }}
with source as (
    select * from {{ source('raw', 'raw_agency') }}
),

renamed as (
    select
        agency_id,
        agency_name,
        agency_url,
        agency_timezone,
        agency_phone
    from source
    where agency_id is not null
)

select * from renamed