
# Olist Dataset — Data Understanding

## 1. Dataset Overview

**Dataset name:** Brazilian E-Commerce Public Dataset by Olist

**Source:** Kaggle — `olistbr/brazilian-ecommerce`

**Format:** CSV

**Number of files:** 9

**Raw data location:** `data/raw/olist/`

**Purpose:**
This dataset contains Brazilian e-commerce transaction data, including customers, orders, products, sellers, payments, reviews, and geographic information.

### Dataset Inventory

| Dataset | Rows | Columns |
|---|---:|---:|
| Customers | 99,441 | 5 |
| Geolocation | 1,000,163 | 5 |
| Order Items | 112,650 | 7 |
| Order Payments | 103,886 | 5 |
| Order Reviews | 99,224 | 7 |
| Orders | 99,441 | 8 |
| Products | 32,951 | 9 |
| Sellers | 3,095 | 4 |
| Product Category Translation | 71 | 2 |
| **Total** | **1,650,852** | **52** |

### Raw Data Preservation

- Original CSV files are preserved without modification.
- Raw data is excluded from Git version control.
- Missing values and source-data anomalies are retained for investigation.
- Data cleaning and transformation will happen in later processing stages.


## 2. Data Quality Observations

### 2.1 Missing Values

The following datasets contain missing values:

| Dataset | Column | Missing Rows |
|---|---|---:|
| Order Reviews | review_comment_title | 87,656 |
| Order Reviews | review_comment_message | 58,247 |
| Orders | order_approved_at | 160 |
| Orders | order_delivered_carrier_date | 1,783 |
| Orders | order_delivered_customer_date | 2,965 |
| Products | product_category_name | 610 |
| Products | product_name_lenght | 610 |
| Products | product_description_lenght | 610 |
| Products | product_photos_qty | 610 |
| Products | product_weight_g | 2 |
| Products | product_length_cm | 2 |
| Products | product_height_cm | 2 |
| Products | product_width_cm | 2 |

All other columns were observed to have zero missing values during initial profiling.

### 2.2 Duplicate Records

| Dataset | Exact Duplicate Rows |
|---|---:|
| Customers | 0 |
| Geolocation | 261,831 |
| Order Items | 0 |
| Order Payments | 0 |
| Order Reviews | 0 |
| Orders | 0 |
| Products | 0 |
| Sellers | 0 |
| Product Category Translation | 0 |

Geolocation contains approximately 26.18% exact duplicate rows.

Repeated postal-code prefixes and coordinate combinations require further consideration before any deduplication.

### 2.3 Order Lifecycle Observations

The order status distribution is:

| Status | Orders |
|---|---:|
| Delivered | 96,478 |
| Shipped | 1,107 |
| Canceled | 625 |
| Unavailable | 609 |
| Invoiced | 314 |
| Processing | 301 |
| Created | 5 |
| Approved | 2 |

Eight orders have status `delivered` but no customer delivery timestamp.

These records are retained as source-data exceptions. Delivery timestamps must not be fabricated.


## 3. Primary Keys and Composite Keys

Candidate keys were evaluated using uniqueness and missing-value checks.

### 3.1 Single-Column Primary Key Candidates

| Dataset | Candidate Key | Unique | Result |
|---|---|---|---|
| Customers | customer_id | 99,441 | Valid |
| Orders | order_id | 99,441 | Valid |
| Products | product_id | 32,951 | Valid |
| Sellers | seller_id | 3,095 | Valid |
| Product Category Translation | product_category_name | 71 | Valid |

All listed candidate keys contain no missing values or duplicate values.

### 3.2 Composite Primary Key Candidates

| Dataset | Candidate Composite Key | Rows | Duplicate Combinations |
|---|---|---:|---:|
| Order Items | order_id, order_item_id | 112,650 | 0 |
| Order Payments | order_id, payment_sequential | 103,886 | 0 |
| Order Reviews | review_id, order_id | 99,224 | 0 |

All three composite key candidates were verified as unique.

### 3.3 Important Identifier Observations

- `customer_unique_id` is not unique in the customers dataset.
- The customers dataset contains 96,096 distinct real-world customer identifiers across 99,441 records.
- `order_id` repeats in order items, payments, and reviews because these datasets can contain multiple records associated with one order.
- `geolocation_zip_code_prefix` is not unique and must not be treated as a primary key.
- Postal-code prefixes are identifiers and should be treated as strings in downstream processing.


## 4. Relationships and Referential Integrity

Foreign-key relationships were evaluated by checking whether child-table values exist in their corresponding parent tables.

### 4.1 Verified Relationships

| Child Dataset | Foreign Key | Parent Dataset | Parent Key | Orphan Rows |
|---|---|---|---|---:|
| Orders | customer_id | Customers | customer_id | 0 |
| Order Items | order_id | Orders | order_id | 0 |
| Order Items | product_id | Products | product_id | 0 |
| Order Items | seller_id | Sellers | seller_id | 0 |
| Order Payments | order_id | Orders | order_id | 0 |
| Order Reviews | order_id | Orders | order_id | 0 |

All non-null foreign-key values in these six relationships have matching parent records.

### 4.2 Relationships with Unmatched References

| Child Dataset | Foreign Key | Parent Dataset | Orphan Rows |
|---|---|---|---:|
| Products | product_category_name | Category Translation | 13 |
| Customers | customer_zip_code_prefix | Geolocation | 278 |
| Sellers | seller_zip_code_prefix | Geolocation | 7 |

Additional observations:

- 610 product records have a missing `product_category_name`.
- Two distinct category values are absent from the translation table:
  - `portateis_cozinha_e_preparadores_de_alimentos` — 10 records
  - `pc_gamer` — 3 records
- Customer geolocation references contain 157 distinct unmatched postal-code prefixes.
- Seller geolocation references contain 7 distinct unmatched postal-code prefixes.

### 4.3 Referential Integrity Decisions

- Unmatched product categories will be retained as source values.
- Missing product categories will remain null in the raw layer.
- Customers and sellers with unmatched geolocation references will be retained.
- No geographic coordinates will be fabricated.
- Unmatched references will be documented and monitored during data validation.



## 5. Geolocation Analysis and Engineering Considerations

### 5.1 Geolocation Dataset Cardinality

| Metric | Value |
|---|---:|
| Total rows | 1,000,163 |
| Unique postal-code prefixes | 19,015 |
| Exact duplicate rows | 261,831 |
| Prefixes with multiple records | 17,972 |
| Prefixes with multiple distinct coordinate pairs | 17,781 |
| Maximum records for one prefix | 1,146 |
| Maximum distinct coordinate pairs for one prefix | 746 |

The geolocation dataset contains multiple records and coordinate pairs for many postal-code prefixes.

### 5.2 Join Fan-Out Risk

Joining customers or sellers directly to geolocation using postal-code prefixes can produce multiple output rows for a single customer or seller.

This can inflate record counts and distort downstream aggregations.

### 5.3 Engineering Decisions

1. Preserve the original geolocation CSV without modification.
2. Do not assume postal-code prefixes uniquely identify coordinate records.
3. Do not arbitrarily select the first coordinate for a postal-code prefix.
4. Any future geographic lookup or aggregation must use an explicit, documented strategy.
5. Validate row counts and join cardinality after geographic joins.
6. Treat postal-code prefixes as string identifiers in downstream processing.

### 5.4 Overall Data Preservation Policy

The raw layer will remain an immutable representation of the acquired source datasets.

- No source rows will be deleted during ingestion.
- No missing values will be filled during ingestion.
- No duplicate records will be silently removed.
- Data-quality issues will be recorded and surfaced through validation.
- Transformations and business rules will be applied in later processing layers.

## Raw Data Storage and Integrity

### Source archive

The project uses the Brazilian E-Commerce Public Dataset by Olist.

- Original archive: `brazilian-ecommerce.zip`
- Storage location: `data/raw/olist/`
- Archive size: approximately 43 MB
- Extracted files: 9 CSV datasets
- Raw data is excluded from Git version control through `.gitignore`.

### Integrity Verification

The original ZIP archive was checked using `unzip -t` and all nine entries passed the archive integrity test.

Its SHA-256 checksum is:

```text
967e41e04fc306fe604e2a693f488995a8b41e5047418f8a5c8e4abd6deca784
```

To verify the archive has not changed:

```bash
sha256sum data/raw/olist/brazilian-ecommerce.zip
```

Compare the output with the checksum recorded above.

### Storage Principles

- Preserve the original ZIP archive as the source artifact.
- Keep extracted CSV files unchanged in `data/raw/olist/`.
- Do not modify, clean, deduplicate, or impute raw source data.
- Exclude raw datasets from Git to avoid committing large data files.
- Perform data cleaning and business-rule transformations in downstream pipeline stages.
- Store generated ingestion metadata separately under `data/metadata/ingestion/`.