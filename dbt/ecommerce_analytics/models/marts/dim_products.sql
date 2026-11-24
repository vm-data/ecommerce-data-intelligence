{{
    config(
        materialized='table'
    )
}}

SELECT
    -- Product key
    product_id,

    -- Category
    product_category_name,
    product_category_name_english,

    -- Catalogue attributes
    product_name_length,
    product_description_length,
    product_photos_qty,

    -- Physical attributes
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,

    -- Sales performance
    total_order_items,
    distinct_orders,
    distinct_sellers,
    total_product_sales_value,
    average_selling_price,

    -- Freight performance
    total_freight_value,
    average_freight_value

FROM {{ ref('int_products_enriched') }}
