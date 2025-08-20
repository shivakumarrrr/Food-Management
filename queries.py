import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

def get_connection():
    engine = create_engine(st.secrets["DB_URL"])
    return engine.connect()

def run_query(sql):
    with get_connection() as conn:
        return pd.read_sql(sql, conn)

# ------------------ QUERY DICTIONARY ------------------
queries = {
    "Total Claims per Provider": """
        SELECT p.name AS provider_name, COUNT(c.claim_id) AS total_claims
        FROM claims c
        JOIN food_listings f ON c.food_id = f.food_id
        JOIN providers p ON f.provider_id = p.provider_id
        GROUP BY p.name
        ORDER BY total_claims DESC;
    """,
    "Top 10 Providers by Food Quantity": """
        SELECT p.name AS provider_name, SUM(f.quantity) AS total_quantity
        FROM food_listings f
        JOIN providers p ON f.provider_id = p.provider_id
        GROUP BY p.name
        ORDER BY total_quantity DESC
        LIMIT 10;
    """,
    "Claims by Status": """
        SELECT status, COUNT(*) AS total
        FROM claims
        GROUP BY status;
    """,
    "Food Listings by Type": """
        SELECT food_type, COUNT(*) AS total
        FROM food_listings
        GROUP BY food_type;
    """,
    "Meal Type Distribution": """
        SELECT meal_type, COUNT(*) AS total
        FROM food_listings
        GROUP BY meal_type;
    """,
    "Expired Food Listings": """
        SELECT f.food_name, f.expiry_date, p.name AS provider_name
        FROM food_listings f
        JOIN providers p ON f.provider_id = p.provider_id
        WHERE f.expiry_date < CURDATE();
    """,
    "Active Food Listings": """
        SELECT f.food_name, f.expiry_date, p.name AS provider_name
        FROM food_listings f
        JOIN providers p ON f.provider_id = p.provider_id
        WHERE f.expiry_date >= CURDATE();
    """,
    "Top Cities by Providers": """
        SELECT city, COUNT(*) AS provider_count
        FROM providers
        GROUP BY city
        ORDER BY provider_count DESC;
    """,
    "Top Cities by Receivers": """
        SELECT city, COUNT(*) AS receiver_count
        FROM receivers
        GROUP BY city
        ORDER BY receiver_count DESC;
    """,
    "Receivers with Most Claims": """
        SELECT r.name AS receiver_name, COUNT(c.claim_id) AS total_claims
        FROM claims c
        JOIN receivers r ON c.receiver_id = r.receiver_id
        GROUP BY r.name
        ORDER BY total_claims DESC;
    """,
    "Food Listings Per Provider Type": """
        SELECT provider_type, COUNT(*) AS total_listings
        FROM food_listings
        GROUP BY provider_type;
    """,
    "Average Quantity per Food Type": """
        SELECT food_type, AVG(quantity) AS avg_quantity
        FROM food_listings
        GROUP BY food_type;
    """,
    "Claims per Food Type": """
        SELECT f.food_type, COUNT(c.claim_id) AS total_claims
        FROM claims c
        JOIN food_listings f ON c.food_id = f.food_id
        GROUP BY f.food_type;
    """,
    "Providers Without Listings": """
        SELECT p.name, p.city
        FROM providers p
        LEFT JOIN food_listings f ON p.provider_id = f.provider_id
        WHERE f.food_id IS NULL;
    """,
    "Receivers Without Claims": """
        SELECT r.name, r.city
        FROM receivers r
        LEFT JOIN claims c ON r.receiver_id = c.receiver_id
        WHERE c.claim_id IS NULL;
    """
}
