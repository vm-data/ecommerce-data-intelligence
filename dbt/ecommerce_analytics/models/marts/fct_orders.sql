{{
    config(
        materialized='table'
    )
}}

SELECT
    -- Order identifiers and status
    o.order_id,
    o.customer_id,
    o.order_status,

    -- Order timestamps
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Item and financial metrics
    o.item_count,
    o.total_item_value,
    o.total_freight_value,

    COALESCE(o.total_item_value, 0)
        + COALESCE(o.total_freight_value, 0)
        AS total_order_value,

    -- Payment metrics
    o.payment_record_count,
    o.total_payment_value,
    o.distinct_payment_type_count,
    o.payment_types,

    -- Review metrics
    o.review_count,
    o.total_review_score,
    o.average_review_score,
    o.min_review_score,
    o.max_review_score,

    -- Delivery duration metrics
    d.purchase_to_approval_hours,
    d.approval_to_carrier_hours,
    d.carrier_to_delivery_hours,
    d.actual_delivery_days,
    d.estimated_delivery_days,
    d.delivery_difference_days,

    -- Delivery classifications
    d.is_delivered_late,
    d.is_delivered_early,
    d.is_delivered_on_time,
    d.delivery_status_category,

    -- Data quality flags
    d.has_missing_approval_timestamp,
    d.has_missing_carrier_timestamp,
    d.has_missing_delivery_timestamp,
    d.has_approval_before_purchase,
    d.has_carrier_before_approval,
    d.has_delivery_before_carrier,
    d.has_delivery_before_purchase,
    d.has_delivery_timestamp_status_mismatch

FROM {{ ref('int_orders_enriched') }} AS o

LEFT JOIN {{ ref('int_delivery_performance') }} AS d
    ON o.order_id = d.order_id
