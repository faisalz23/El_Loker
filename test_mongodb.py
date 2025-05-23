from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Setup koneksi MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    logger.info("Connected to MongoDB")
    
    db = client['job_db']
    collection = db['job_postings']
    
    # Insert test data
    test_job = {
        'title': 'Test Job Position',
        'company': 'Test Company',
        'location': 'Remote'
    }
    
    result = collection.insert_one(test_job)
    logger.info(f"Test data inserted with ID: {result.inserted_id}")
    
    # Verify data was inserted
    found_job = collection.find_one({'_id': result.inserted_id})
    if found_job:
        logger.info(f"Successfully retrieved test data: {found_job}")
    else:
        logger.error("Could not retrieve test data")
        
except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
finally:
    if 'client' in locals():
        client.close()
        logger.info("MongoDB connection closed") 