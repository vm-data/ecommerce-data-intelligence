{{
    config(
        materialized='table'
    )
}}

SELECT
    customer_unique_id,

    -- Latest observed customer location
    latest_observed_city,
    latest_observed_state,
    latest_observed_zip_code_prefix,

    -- Purchase behaviour
    total_orders,
    first_order_date,
    last_order_date,
    purchasing_lifespan_days,
    is_repeat_customer,

    -- Item metrics
    total_items_purchased,

    -- Payment metrics
    orders_with_payment_records,
    lifetime_payment_value,
    average_order_payment_value,

    -- Review metrics
    total_review_records,
    total_review_score,
    average_review_score

FROM {{ ref('int_customers_enriched') }}
