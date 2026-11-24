{{
    config(
        materialized='view'
    )
}}

WITH product_sales_aggregated AS (

    SELECT
        product_id,

        COUNT(*) AS total_order_items,

        COUNT(DISTINCT order_id) AS distinct_orders,

        COUNT(DISTINCT seller_id) AS distinct_sellers,

        SUM(price) AS total_product_sales_value,

        AVG(price) AS average_selling_price,

        SUM(freight_value) AS total_freight_value,

        AVG(freight_value) AS average_freight_value

    FROM {{ ref('int_order_items_enriched') }}

    GROUP BY product_id

)

SELECT
    p.product_id,

    p.product_category_name,
    t.product_category_name_english,

    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,

    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,

    COALESCE(s.total_order_items, 0)
        AS total_order_items,

    COALESCE(s.distinct_orders, 0)
        AS distinct_orders,

    COALESCE(s.distinct_sellers, 0)
        AS distinct_sellers,

    COALESCE(s.total_product_sales_value, 0)
        AS total_product_sales_value,

    ROUND(
        s.average_selling_price::numeric,
        2
    ) AS average_selling_price,

    COALESCE(s.total_freight_value, 0)
        AS total_freight_value,

    ROUND(
        s.average_freight_value::numeric,
        2
    ) AS average_freight_value

FROM {{ ref('stg_products') }} AS p

LEFT JOIN {{ ref('stg_product_category_name_translation') }} AS t
    ON p.product_category_name = t.product_category_name

LEFT JOIN product_sales_aggregated AS s
    ON p.product_id = s.product_id
