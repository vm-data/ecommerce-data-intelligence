{{
    config(
        materialized='table'
    )
}}

SELECT
    -- Seller key
    seller_id,

    -- Location
    seller_city,
    seller_state,
    seller_zip_code_prefix,

    -- Sales performance
    total_order_items,
    distinct_orders,
    distinct_products,
    total_sales_value,
    average_selling_price,

    -- Freight performance
    total_freight_value,
    average_freight_value

FROM {{ ref('int_sellers_enriched') }}
