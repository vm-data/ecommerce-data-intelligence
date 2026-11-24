{{
    config(
        materialized='table'
    )
}}

WITH seller_metrics AS (

    SELECT
        s.*,

        SUM(s.total_sales_value) OVER ()
            AS overall_gmv

    FROM {{ ref('dim_sellers') }} AS s

),

ranked_sellers AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY total_sales_value DESC
        ) AS seller_gmv_rank,

        DENSE_RANK() OVER (
            ORDER BY distinct_orders DESC
        ) AS seller_order_rank,

        DENSE_RANK() OVER (
            ORDER BY total_order_items DESC
        ) AS seller_item_volume_rank

    FROM seller_metrics

)

SELECT
    seller_id,

    seller_city,
    seller_state,
    seller_zip_code_prefix,

    total_order_items,
    distinct_orders,
    distinct_products,

    ROUND(total_sales_value::numeric, 2)
        AS seller_gmv,

    average_selling_price,

    ROUND(total_freight_value::numeric, 2)
        AS total_freight_value,

    average_freight_value,

    ROUND(
        (
            total_sales_value
            / NULLIF(overall_gmv, 0)
        )::numeric * 100,
        2
    ) AS overall_gmv_contribution_percentage,

    seller_gmv_rank,
    seller_order_rank,
    seller_item_volume_rank

FROM ranked_sellers
