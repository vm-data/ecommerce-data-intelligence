{{
    config(
        materialized='table'
    )
}}

SELECT
    -- Fact grain / identifiers
    order_id,
    order_item_id,

    -- Dimension keys
    customer_id,
    product_id,
    seller_id,

    -- Order attributes
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,

    -- Item attributes
    shipping_limit_date,
    price AS item_gmv,
    freight_value AS item_freight_value,

    COALESCE(price, 0)
        + COALESCE(freight_value, 0) AS item_total_value,

    -- Product attributes
    product_category_name,
    product_category_name_english,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,

    -- Seller attributes
    seller_zip_code_prefix,
    seller_city,
    seller_state

FROM {{ ref('int_order_items_enriched') }}
