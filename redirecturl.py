import json
import pymysql
import redis
import os

# MySQL Connection Details
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Redis Connection
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def lambda_handler(event, context):
    short_code = event['pathParameters']['short_code']
    
    # Check Redis Cache
    long_url = redis_client.get(short_code)
    if long_url:
        return {
            "statusCode": 302,
            "headers": {"Location": long_url}
        }
    
    # Query Database
    with conn.cursor() as cursor:
        cursor.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
        result = cursor.fetchone()
        
    if result:
        original_url = result[0]
        redis_client.setex(short_code, 86400, original_url)  # Store in Redis for 24 hours
        return {
            "statusCode": 302,
            "headers": {"Location": original_url}
        }
    
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Short URL not found"})
    }
