{{
    config(
        materialized='view'
    )
}}

WITH customer_order_metrics AS (

    SELECT
        c.customer_unique_id,

        -- Purchase frequency
        COUNT(DISTINCT o.order_id) AS total_orders,

        MIN(o.order_purchase_timestamp) AS first_order_date,

        MAX(o.order_purchase_timestamp) AS last_order_date,

        -- Item metrics
        SUM(o.item_count) AS total_items_purchased,

        -- Payment metrics
        COUNT(*) FILTER (
            WHERE o.payment_record_count > 0
        ) AS orders_with_payment_records,

        COALESCE(
            SUM(o.total_payment_value),
            0
        ) AS lifetime_payment_value,

        AVG(o.total_payment_value) FILTER (
            WHERE o.payment_record_count > 0
        ) AS average_order_payment_value,

        -- Review metrics
        COALESCE(
            SUM(o.review_count),
            0
        ) AS total_review_records,

        SUM(o.total_review_score) AS total_review_score,

        ROUND(
            SUM(o.total_review_score)::numeric
            / NULLIF(SUM(o.review_count), 0),
            2
        ) AS average_review_score

    FROM {{ ref('int_orders_enriched') }} AS o

    INNER JOIN {{ ref('stg_customers') }} AS c
        ON o.customer_id = c.customer_id

    GROUP BY c.customer_unique_id

),

customer_profile_ranked AS (

    SELECT
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        c.customer_zip_code_prefix,

        ROW_NUMBER() OVER (
            PARTITION BY c.customer_unique_id
            ORDER BY
                o.order_purchase_timestamp DESC,
                o.order_id DESC,
                c.customer_id DESC
        ) AS location_rank

    FROM {{ ref('stg_customers') }} AS c

    INNER JOIN {{ ref('stg_orders') }} AS o
        ON c.customer_id = o.customer_id

),

latest_customer_profile AS (

    SELECT
        customer_unique_id,
        customer_city,
        customer_state,
        customer_zip_code_prefix

    FROM customer_profile_ranked

    WHERE location_rank = 1

)

SELECT
    -- Customer identity
    m.customer_unique_id,

    -- Latest observed customer location
    p.customer_city AS latest_observed_city,
    p.customer_state AS latest_observed_state,
    p.customer_zip_code_prefix AS latest_observed_zip_code_prefix,

    -- Purchase behaviour
    m.total_orders,
    m.first_order_date,
    m.last_order_date,

    (
        m.last_order_date::date
        - m.first_order_date::date
    ) AS purchasing_lifespan_days,

    (m.total_orders > 1) AS is_repeat_customer,

    -- Item metrics
    m.total_items_purchased,

    -- Financial metrics
    m.orders_with_payment_records,
    m.lifetime_payment_value,
    ROUND(
        m.average_order_payment_value,
        2
    ) AS average_order_payment_value,

    -- Review metrics
    m.total_review_records,
    m.total_review_score,
    m.average_review_score

FROM customer_order_metrics AS m

LEFT JOIN latest_customer_profile AS p
    ON m.customer_unique_id = p.customer_unique_id
