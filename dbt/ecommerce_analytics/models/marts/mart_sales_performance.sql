{{
    config(
        materialized='table'
    )
}}

WITH order_sales AS (

    SELECT
        DATE_TRUNC(
            'month',
            f.order_purchase_timestamp
        )::date AS purchase_month,

        COALESCE(c.customer_state, 'Unknown') AS customer_state,

        f.order_id,
        f.order_status,
        f.item_count,
        f.total_item_value,
        f.total_freight_value,
        f.total_order_value,
        f.total_payment_value

    FROM {{ ref('fct_orders') }} AS f

    LEFT JOIN {{ ref('stg_customers') }} AS c
        ON f.customer_id = c.customer_id

),

monthly_sales AS (

    SELECT
        purchase_month,
        customer_state,

        COUNT(DISTINCT order_id) AS total_orders,

        COUNT(DISTINCT order_id) FILTER (
            WHERE order_status = 'delivered'
        ) AS delivered_orders,

        COUNT(DISTINCT order_id) FILTER (
            WHERE order_status = 'canceled'
        ) AS cancelled_orders,

        SUM(item_count) AS total_order_items,

        COALESCE(SUM(total_item_value), 0)
            AS gross_merchandise_value,

        COALESCE(SUM(total_freight_value), 0)
            AS total_freight_value,

        COALESCE(SUM(total_order_value), 0)
            AS total_order_value,

        COALESCE(SUM(total_payment_value), 0)
            AS total_payment_value,

        AVG(total_order_value)
            AS average_order_value,

        AVG(total_payment_value) FILTER (
            WHERE total_payment_value > 0
        ) AS average_payment_value

    FROM order_sales

    GROUP BY
        purchase_month,
        customer_state

),

sales_with_growth AS (

    SELECT
        *,

        LAG(gross_merchandise_value) OVER (
            PARTITION BY customer_state
            ORDER BY purchase_month
        ) AS previous_month_gmv

    FROM monthly_sales

)

SELECT
    purchase_month,
    customer_state,

    total_orders,
    delivered_orders,
    cancelled_orders,
    total_order_items,

    ROUND(gross_merchandise_value::numeric, 2)
        AS gross_merchandise_value,

    ROUND(total_freight_value::numeric, 2)
        AS total_freight_value,

    ROUND(total_order_value::numeric, 2)
        AS total_order_value,

    ROUND(total_payment_value::numeric, 2)
        AS total_payment_value,

    ROUND(average_order_value::numeric, 2)
        AS average_order_value,

    ROUND(average_payment_value::numeric, 2)
        AS average_payment_value,

    ROUND(previous_month_gmv::numeric, 2)
        AS previous_month_gmv,

    ROUND(
        (
            (gross_merchandise_value - previous_month_gmv)
            / NULLIF(previous_month_gmv, 0)
        )::numeric * 100,
        2
    ) AS gmv_growth_percentage

FROM sales_with_growth
