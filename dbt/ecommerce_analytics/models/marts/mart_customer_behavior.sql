{{
    config(
        materialized='table'
    )
}}

WITH dataset_reference AS (

    SELECT
        MAX(order_purchase_timestamp)::date
            AS dataset_latest_purchase_date

    FROM {{ ref('fct_orders') }}

),

customer_metrics AS (

    SELECT
        c.*,

        r.dataset_latest_purchase_date,

        (
            r.dataset_latest_purchase_date
            - c.last_order_date::date
        ) AS recency_days,

        DATE_TRUNC(
            'month',
            c.first_order_date
        )::date AS customer_cohort_month

    FROM {{ ref('dim_customers') }} AS c

    CROSS JOIN dataset_reference AS r

),

customer_segments AS (

    SELECT
        *,

        CASE
            WHEN total_orders = 1 THEN 'one_time'
            WHEN total_orders BETWEEN 2 AND 3 THEN 'occasional'
            WHEN total_orders BETWEEN 4 AND 6 THEN 'frequent'
            ELSE 'loyal'
        END AS purchase_frequency_segment,

        CASE
            WHEN lifetime_payment_value < 100 THEN 'low_value'
            WHEN lifetime_payment_value < 500 THEN 'mid_value'
            ELSE 'high_value'
        END AS monetary_value_segment,

        CASE
            WHEN recency_days <= 90 THEN 'active'
            WHEN recency_days <= 180 THEN 'recently_inactive'
            ELSE 'inactive'
        END AS recency_segment

    FROM customer_metrics

)

SELECT
    customer_unique_id,

    latest_observed_city,
    latest_observed_state,
    latest_observed_zip_code_prefix,

    total_orders,
    first_order_date,
    last_order_date,
    purchasing_lifespan_days,

    customer_cohort_month,
    dataset_latest_purchase_date,
    recency_days,

    is_repeat_customer,
    purchase_frequency_segment,
    monetary_value_segment,
    recency_segment,

    total_items_purchased,
    orders_with_payment_records,

    ROUND(lifetime_payment_value::numeric, 2)
        AS lifetime_payment_value,

    average_order_payment_value,

    total_review_records,
    total_review_score,
    average_review_score

FROM customer_segments
