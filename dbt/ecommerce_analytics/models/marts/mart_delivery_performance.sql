{{
    config(
        materialized='table'
    )
}}

WITH monthly_delivery AS (

    SELECT
        DATE_TRUNC(
            'month',
            order_purchase_timestamp
        )::date AS purchase_month,

        delivery_status_category,

        COUNT(*) AS total_orders,

        COUNT(*) FILTER (
            WHERE delivery_status_category IN (
                'early',
                'on_time',
                'late'
            )
        ) AS delivered_orders,

        COUNT(*) FILTER (
            WHERE delivery_status_category = 'early'
        ) AS early_orders,

        COUNT(*) FILTER (
            WHERE delivery_status_category = 'on_time'
        ) AS on_time_orders,

        COUNT(*) FILTER (
            WHERE delivery_status_category = 'late'
        ) AS late_orders,

        COUNT(*) FILTER (
            WHERE delivery_status_category = 'not_delivered'
        ) AS not_delivered_orders,

        COUNT(*) FILTER (
            WHERE delivery_status_category = 'missing_delivery_timestamp'
        ) AS missing_delivery_timestamp_orders,

        AVG(actual_delivery_days)
            AS average_actual_delivery_days,

        AVG(estimated_delivery_days)
            AS average_estimated_delivery_days,

        AVG(delivery_difference_days)
            AS average_delivery_difference_days

    FROM {{ ref('fct_orders') }}

    GROUP BY
        DATE_TRUNC(
            'month',
            order_purchase_timestamp
        )::date,

        delivery_status_category

),

delivery_with_month_totals AS (

    SELECT
        *,

        SUM(total_orders) OVER (
            PARTITION BY purchase_month
        ) AS monthly_total_orders

    FROM monthly_delivery

)

SELECT
    purchase_month,
    delivery_status_category,

    total_orders,
    monthly_total_orders,

    delivered_orders,
    early_orders,
    on_time_orders,
    late_orders,
    not_delivered_orders,
    missing_delivery_timestamp_orders,

    ROUND(
        (
            total_orders::numeric
            / NULLIF(monthly_total_orders, 0)
        ) * 100,
        2
    ) AS percentage_of_monthly_orders,

    ROUND(average_actual_delivery_days::numeric, 2)
        AS average_actual_delivery_days,

    ROUND(average_estimated_delivery_days::numeric, 2)
        AS average_estimated_delivery_days,

    ROUND(average_delivery_difference_days::numeric, 2)
        AS average_delivery_difference_days

FROM delivery_with_month_totals
