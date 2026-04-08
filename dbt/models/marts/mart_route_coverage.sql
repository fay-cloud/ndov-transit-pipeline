{{ config(
    materialized='table',
    schema='MARTS'
) }}

with routes as (
    select * from {{ ref('stg_routes') }}
),

agency as (
    select * from {{ ref('stg_agency') }}
),

route_counts as (
    select
        r.agency_id,
        a.agency_name,
        count(distinct r.route_id) as total_routes,
        count(distinct case when r.route_type = 2 then r.route_id end) as train_routes,
        count(distinct case when r.route_type = 3 then r.route_id end) as bus_routes,
        count(distinct case when r.route_type = 0 then r.route_id end) as tram_routes,
        count(distinct case when r.route_type = 4 then r.route_id end) as ferry_routes
    from routes r
    left join agency a on r.agency_id = a.agency_id
    group by r.agency_id, a.agency_name
)

select * from route_counts
order by total_routes desc