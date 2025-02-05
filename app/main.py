from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'retail_db')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/initdb")
async def init_db():
    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor()
            
            with open('sql/init.sql', 'r') as file:
                init_script = file.read()
            
            # Drop existing tables if they exist
            cursor.execute("DROP TABLE IF EXISTS order_items")
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS customers")
            connection.commit()
            
            # Split and execute statements
            statements = [stmt.strip() for stmt in init_script.split(';') if stmt.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Error as e:
                    print(f"Error executing statement: {statement[:100]}...")
                    print(f"Error message: {str(e)}")
                    return {"error": f"Error during initialization: {str(e)}"}
            
            # Verify data was inserted
            tables = ['customers', 'products', 'orders', 'order_items']
            counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                counts[table] = count
                if count == 0:
                    return {"error": f"Table {table} is empty after initialization"}
            
            return {
                "message": "Database initialized successfully",
                "table_counts": counts
            }
            
    except Error as e:
        print(f"Database error during initialization: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error during initialization: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@app.get("/table/{table_name}")
async def get_table_data(table_name: str):
    valid_tables = {
        'customers': "SELECT * FROM customers LIMIT 50",
        'orders': "SELECT * FROM orders LIMIT 50",
        'products': "SELECT * FROM products LIMIT 50",
        'orderItems': "SELECT * FROM order_items LIMIT 50"
    }
    
    if table_name not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(valid_tables[table_name])
            results = cursor.fetchall()
            return {"data": results}
            
    except Error as e:
        return {"error": f"Database error: {str(e)}"}

# Template routes for lab
@app.get("/assignment1")
async def assignment1():
    # Basic JOIN query
    query = """
        SELECT 
            customers.name AS customer_name,
            customers.email AS customer_email,
            SUM(orders.total_amount) AS total_amount_spent
        FROM customers
        JOIN orders USING (customer_id)
        GROUP BY customers.customer_id
        ORDER BY total_amount_spent DESC
        LIMIT 10;
    """

    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return {"data": results}

    except Error as e:
        return {"error": f"Database error: {str(e)}"}

@app.get("/assignment2")
async def assignment2():
    # GROUP BY query
    query = """
        SELECT 
            products.category AS category_name,
            COUNT(DISTINCT orders.order_id) AS total_orders,
            ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS total_revenue,
            ROUND(AVG(order_items.quantity * order_items.unit_price), 2) AS average_order_value
        FROM products
        JOIN order_items USING (product_id)
        JOIN orders USING (order_id)
        GROUP BY products.category
        ORDER BY total_revenue DESC;
    """

    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return {"data": results}

    except Error as e:
        return {"error": f"Database error: {str(e)}"}

@app.get("/assignment3")
async def assignment3():
    # Complex JOIN with GROUP BY
    query = """
        SELECT 
            membership_level,
            city,
            COUNT(order_id) AS total_orders,
            ROUND(AVG(total_amount), 2) AS average_order_value,
            COUNT(DISTINCT customers.customer_id) AS number_of_customers,
            ROUND(COUNT(order_id)*1.0 / COUNT(DISTINCT customers.customer_id), 2) AS orders_per_customer
        FROM customers
        LEFT JOIN orders USING (customer_id)
        GROUP BY membership_level, city;
    """

    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return {"data": results}

    except Error as e:
        return {"error": f"Database error: {str(e)}"}
    
@app.get("/assignment4")
async def assignment4():
    # Subquery
    query = """
        SELECT 
            p.name AS product_name,
            p.category,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_sales,
            ROUND(avg_sales, 2) AS category_average,
            ROUND((SUM(oi.quantity * oi.unit_price) - avg_sales) / avg_sales * 100, 2) AS percentage_above
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN (
            SELECT 
                category,
                AVG(oi.quantity * oi.unit_price) AS avg_sales
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY category
        ) AS category_avg ON p.category = category_avg.category
        GROUP BY p.product_id, p.category, avg_sales
        HAVING SUM(oi.quantity * oi.unit_price) > avg_sales
        ORDER BY percentage_above DESC;
    """

    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            return {"data": results}

    except Error as e:
        return {"error": f"Database error: {str(e)}"}