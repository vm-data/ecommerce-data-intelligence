
{{
    config(
        materialized='view'
    )
}}

WITH order_items_aggregated AS (

    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS total_item_value,
        SUM(freight_value) AS total_freight_value

    FROM {{ ref('int_order_items_enriched') }}

    GROUP BY order_id

),

payments_aggregated AS (

    SELECT
        order_id,
        COUNT(*) AS payment_record_count,
        SUM(payment_value) AS total_payment_value,
        COUNT(DISTINCT payment_type) AS distinct_payment_type_count,
        STRING_AGG(
            DISTINCT payment_type,
            ', ' ORDER BY payment_type
        ) AS payment_types

    FROM {{ ref('stg_order_payments') }}

    GROUP BY order_id

),

reviews_aggregated AS (

    SELECT
        order_id,
        COUNT(*) AS review_count,
        SUM(review_score) AS total_review_score,
        ROUND(AVG(review_score)::numeric, 2)
            AS average_review_score,
        MIN(review_score) AS min_review_score,
        MAX(review_score) AS max_review_score

    FROM {{ ref('stg_order_reviews') }}

    GROUP BY order_id

)

SELECT
    -- Order details
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Item metrics
    COALESCE(oi.item_count, 0) AS item_count,
    oi.total_item_value,
    oi.total_freight_value,

    -- Payment metrics
    COALESCE(p.payment_record_count, 0) AS payment_record_count,
    p.total_payment_value,
    COALESCE(p.distinct_payment_type_count, 0)
        AS distinct_payment_type_count,
    p.payment_types,

    -- Review metrics
    COALESCE(r.review_count, 0) AS review_count,
    r.total_review_score,
    r.average_review_score,
    r.min_review_score,
    r.max_review_score

FROM {{ ref('stg_orders') }} AS o

LEFT JOIN order_items_aggregated AS oi
    ON o.order_id = oi.order_id

LEFT JOIN payments_aggregated AS p
    ON o.order_id = p.order_id

LEFT JOIN reviews_aggregated AS r
    ON o.order_id = r.order_id
