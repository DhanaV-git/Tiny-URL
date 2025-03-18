import json
import hashlib
import base64
import pymysql
import os

# MySQL Connection Details
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def generate_short_code(url):
    hash_object = hashlib.sha256(url.encode())
    return base64.urlsafe_b64encode(hash_object.digest())[:8].decode()

def lambda_handler(event, context):
    body = json.loads(event['body'])
    original_url = body['original_url']
    short_code = generate_short_code(original_url)
    
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO urls (short_code, original_url) VALUES (%s, %s) ON DUPLICATE KEY UPDATE original_url=%s", (short_code, original_url, original_url))
        conn.commit()
    
    return {
        "statusCode": 200,
        "body": json.dumps({"short_url": f"https://tinyurl.com/{short_code}"})
    }
