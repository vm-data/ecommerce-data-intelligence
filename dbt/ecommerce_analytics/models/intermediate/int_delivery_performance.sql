{{
    config(
        materialized='view'
    )
}}

WITH delivery_base AS (

    SELECT
        order_id,
        customer_id,
        order_status,

        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date

    FROM {{ ref('int_orders_enriched') }}

),

delivery_metrics AS (

    SELECT
        *,

        -- Timestamp quality flags

        (
            order_approved_at IS NOT NULL
            AND order_approved_at < order_purchase_timestamp
        ) AS has_approval_before_purchase,

        (
            order_approved_at IS NOT NULL
            AND order_delivered_carrier_date IS NOT NULL
            AND order_delivered_carrier_date < order_approved_at
        ) AS has_carrier_before_approval,

        (
            order_delivered_carrier_date IS NOT NULL
            AND order_delivered_customer_date IS NOT NULL
            AND order_delivered_customer_date
                < order_delivered_carrier_date
        ) AS has_delivery_before_carrier,

        (
            order_delivered_customer_date IS NOT NULL
            AND order_delivered_customer_date
                < order_purchase_timestamp
        ) AS has_delivery_before_purchase,

        (
            (order_status = 'delivered'
                AND order_delivered_customer_date IS NULL)
            OR
            (order_status <> 'delivered'
                AND order_delivered_customer_date IS NOT NULL)
        ) AS has_delivery_timestamp_status_mismatch

    FROM delivery_base

),

delivery_classification AS (

    SELECT
        *,

        (
            order_status = 'delivered'
            AND order_delivered_customer_date IS NOT NULL
            AND order_delivered_customer_date >= order_purchase_timestamp
        ) AS is_valid_delivered_order

    FROM delivery_metrics

)

SELECT
    order_id,
    customer_id,
    order_status,

    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,

    -- Purchase to approval: hours

    CASE
        WHEN order_approved_at >= order_purchase_timestamp
        THEN ROUND(
            (
                EXTRACT(
                    EPOCH FROM (
                        order_approved_at - order_purchase_timestamp
                    )
                ) / 3600
            )::numeric,
            2
        )
    END AS purchase_to_approval_hours,

    -- Approval to carrier: hours

    CASE
        WHEN order_approved_at IS NOT NULL
         AND order_delivered_carrier_date IS NOT NULL
         AND order_delivered_carrier_date >= order_approved_at
        THEN ROUND(
            (
                EXTRACT(
                    EPOCH FROM (
                        order_delivered_carrier_date - order_approved_at
                    )
                ) / 3600
            )::numeric,
            2
        )
    END AS approval_to_carrier_hours,

    -- Carrier to customer: hours

    CASE
        WHEN order_delivered_carrier_date IS NOT NULL
         AND order_delivered_customer_date IS NOT NULL
         AND order_delivered_customer_date >= order_delivered_carrier_date
        THEN ROUND(
            (
                EXTRACT(
                    EPOCH FROM (
                        order_delivered_customer_date
                        - order_delivered_carrier_date
                    )
                ) / 3600
            )::numeric,
            2
        )
    END AS carrier_to_delivery_hours,

    -- Actual end-to-end delivery duration: days

    CASE
        WHEN is_valid_delivered_order
        THEN ROUND(
            (
                EXTRACT(
                    EPOCH FROM (
                        order_delivered_customer_date
                        - order_purchase_timestamp
                    )
                ) / 86400
            )::numeric,
            2
        )
    END AS actual_delivery_days,

    -- Estimated delivery duration: calendar days

    (
        order_estimated_delivery_date::date
        - order_purchase_timestamp::date
    ) AS estimated_delivery_days,

    -- Difference between actual and estimated delivery dates.
    -- Positive = late, negative = early, zero = on time.

    CASE
        WHEN is_valid_delivered_order
        THEN (
            order_delivered_customer_date::date
            - order_estimated_delivery_date::date
        )
    END AS delivery_difference_days,

    -- Delivery classifications

    CASE
        WHEN is_valid_delivered_order
        THEN order_delivered_customer_date::date
             > order_estimated_delivery_date::date
    END AS is_delivered_late,

    CASE
        WHEN is_valid_delivered_order
        THEN order_delivered_customer_date::date
             < order_estimated_delivery_date::date
    END AS is_delivered_early,

    CASE
        WHEN is_valid_delivered_order
        THEN order_delivered_customer_date::date
             = order_estimated_delivery_date::date
    END AS is_delivered_on_time,

    CASE
        WHEN order_status <> 'delivered'
            THEN 'not_delivered'

        WHEN order_delivered_customer_date IS NULL
            THEN 'missing_delivery_timestamp'

        WHEN order_delivered_customer_date
             < order_purchase_timestamp
            THEN 'invalid_purchase_delivery_sequence'

        WHEN order_delivered_customer_date::date
             > order_estimated_delivery_date::date
            THEN 'late'

        WHEN order_delivered_customer_date::date
             < order_estimated_delivery_date::date
            THEN 'early'

        ELSE 'on_time'
    END AS delivery_status_category,

    -- Data-quality flags

    (order_approved_at IS NULL)
        AS has_missing_approval_timestamp,

    (order_delivered_carrier_date IS NULL)
        AS has_missing_carrier_timestamp,

    (order_delivered_customer_date IS NULL)
        AS has_missing_delivery_timestamp,

    has_approval_before_purchase,
    has_carrier_before_approval,
    has_delivery_before_carrier,
    has_delivery_before_purchase,
    has_delivery_timestamp_status_mismatch

FROM delivery_classification
