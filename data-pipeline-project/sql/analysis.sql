--- Revenue per month
SELECT 
    DATE_TRUNC('month', "Order Date") AS month,
    SUM("Revenue") AS total_revenue
FROM sales_data
GROUP BY 1
ORDER BY 1;

--- Top Produk
SELECT 
    "Product Name",
    SUM("Revenue") AS total_revenue
FROM sales_data
GROUP BY 1
ORDER BY total_revenue DESC
LIMIT 5;

--- Revenue  per region
SELECT 
    "Region",
    SUM("Revenue") AS total_revenue
FROM sales_data
GROUP BY 1;


--- Total Revenue
SELECT 
    SUM("Revenue") AS total_revenue
FROM sales_data;

--- Total Customer 
SELECT 
    COUNT(DISTINCT "Customer ID") AS total_customer
FROM sales_data;

--- Total Order
SELECT 
    COUNT("Order ID") AS total_order
FROM sales_data;

-- The most active customers
SELECT 
    "Customer Name",
    COUNT(*) AS total_orders,
    SUM("Revenue") AS total_revenue
FROM sales_data
GROUP BY "Customer Name"
ORDER BY total_orders DESC
limit 5;