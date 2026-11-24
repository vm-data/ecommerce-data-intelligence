{{
    config(
        materialized='view'
    )
}}

WITH seller_sales_aggregated AS (

    SELECT
        seller_id,

        COUNT(*) AS total_order_items,

        COUNT(DISTINCT order_id) AS distinct_orders,

        COUNT(DISTINCT product_id) AS distinct_products,

        SUM(price) AS total_sales_value,

        AVG(price) AS average_selling_price,

        SUM(freight_value) AS total_freight_value,

        AVG(freight_value) AS average_freight_value

    FROM {{ ref('int_order_items_enriched') }}

    GROUP BY seller_id

)

SELECT
    s.seller_id,

    s.seller_city,
    s.seller_state,
    s.seller_zip_code_prefix,

    COALESCE(a.total_order_items, 0)
        AS total_order_items,

    COALESCE(a.distinct_orders, 0)
        AS distinct_orders,

    COALESCE(a.distinct_products, 0)
        AS distinct_products,

    COALESCE(a.total_sales_value, 0)
        AS total_sales_value,

    ROUND(
        a.average_selling_price::numeric,
        2
    ) AS average_selling_price,

    COALESCE(a.total_freight_value, 0)
        AS total_freight_value,

    ROUND(
        a.average_freight_value::numeric,
        2
    ) AS average_freight_value

FROM {{ ref('stg_sellers') }} AS s

LEFT JOIN seller_sales_aggregated AS a
    ON s.seller_id = a.seller_id
