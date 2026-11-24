{{
    config(
        materialized='table'
    )
}}

WITH product_metrics AS (

    SELECT
        p.*,

        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Uncategorized'
        ) AS reporting_category,

        SUM(p.total_product_sales_value) OVER (
            PARTITION BY COALESCE(
                p.product_category_name_english,
                p.product_category_name,
                'Uncategorized'
            )
        ) AS category_gmv,

        SUM(p.total_product_sales_value) OVER ()
            AS overall_gmv

    FROM {{ ref('dim_products') }} AS p

),

ranked_products AS (

    SELECT
        *,

        DENSE_RANK() OVER (
            PARTITION BY reporting_category
            ORDER BY total_product_sales_value DESC
        ) AS product_rank_in_category,

        DENSE_RANK() OVER (
            ORDER BY total_product_sales_value DESC
        ) AS overall_product_rank

    FROM product_metrics

)

SELECT
    product_id,

    product_category_name,
    product_category_name_english,
    reporting_category,

    product_name_length,
    product_description_length,
    product_photos_qty,

    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,

    total_order_items,
    distinct_orders,
    distinct_sellers,

    ROUND(total_product_sales_value::numeric, 2)
        AS product_gmv,

    average_selling_price,

    ROUND(total_freight_value::numeric, 2)
        AS total_freight_value,

    average_freight_value,

    ROUND(category_gmv::numeric, 2)
        AS category_gmv,

    ROUND(
        (
            total_product_sales_value
            / NULLIF(category_gmv, 0)
        )::numeric * 100,
        2
    ) AS category_gmv_contribution_percentage,

    ROUND(
        (
            total_product_sales_value
            / NULLIF(overall_gmv, 0)
        )::numeric * 100,
        2
    ) AS overall_gmv_contribution_percentage,

    product_rank_in_category,
    overall_product_rank

FROM ranked_products
