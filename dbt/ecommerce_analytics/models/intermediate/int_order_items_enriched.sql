{{
    config(
        materialized='view'
    )
}}

SELECT
    -- Order item details
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.shipping_limit_date,
    oi.price,
    oi.freight_value,

    -- Order details
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Product details
    p.product_category_name,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,

    -- English category
    cat.product_category_name_english,

    -- Seller details
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state

FROM {{ ref('stg_order_items') }} AS oi

LEFT JOIN {{ ref('stg_orders') }} AS o
    ON oi.order_id = o.order_id

LEFT JOIN {{ ref('stg_products') }} AS p
    ON oi.product_id = p.product_id

LEFT JOIN {{ ref('stg_sellers') }} AS s
    ON oi.seller_id = s.seller_id

LEFT JOIN {{ ref('stg_product_category_name_translation') }} AS cat
    ON p.product_category_name = cat.product_category_name
