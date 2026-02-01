import sqlite3
from sqlite3 import Error
import os
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('grameenconnect.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Initialize the database with required tables if they don't exist"""
    connection = None
    try:
        connection = get_db_connection()
        
        # Create users table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                fullname TEXT,
                village TEXT,
                contact TEXT NOT NULL,
                joined_date TIMESTAMP NOT NULL,
                profile_image TEXT,
                banner_image TEXT
            )
        ''')
        
        # Create jobs table (don't drop it)
        connection.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                contact TEXT NOT NULL,
                category TEXT,
                eligibility TEXT,
                salary TEXT,
                deadline TEXT,
                user_id INTEGER NOT NULL,
                posted_date TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create government schemes table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                eligibility TEXT,
                how_to_apply TEXT,
                deadline TEXT,
                agency TEXT,
                contact TEXT,
                website TEXT,
                posted_date TIMESTAMP NOT NULL
            )
        ''')
        
        # Create infrastructure issues table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT,
                image TEXT,
                user_id INTEGER NOT NULL,
                reported_date TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create marketplace products table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price TEXT NOT NULL,
                location TEXT,
                contact TEXT NOT NULL,
                category TEXT,
                image TEXT,
                user_id INTEGER NOT NULL,
                posted_date TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create job applications table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                experience TEXT,
                message TEXT,
                application_date TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert sample government schemes if table is empty
        if not connection.execute('SELECT COUNT(*) FROM schemes').fetchone()[0]:
            sample_schemes = [
                ('Pradhan Mantri Kisan Samman Nidhi', 
                 'Financial support of Rs. 6000 per year to eligible farmer families.',
                 'Small and marginal farmers with combined landholding up to 2 hectares.',
                 '1. Register online at pmkisan.gov.in or visit local agriculture office.\n2. Submit land records and bank details.',
                 'Ongoing',
                 'Ministry of Agriculture & Farmers Welfare',
                 '1800-115-526',
                 'https://pmkisan.gov.in/',
                 datetime.now()),
                
                ('Pradhan Mantri Fasal Bima Yojana',
                 'Crop insurance scheme providing financial support to farmers in case of crop failure.',
                 'All farmers including sharecroppers and tenant farmers.',
                 '1. Apply through nearest bank branch, CSC center or online.\n2. Submit land records and pay premium amount.',
                 'Seasonal (Varies by crop)',
                 'Ministry of Agriculture & Farmers Welfare',
                 '1800-110-144',
                 'https://pmfby.gov.in/',
                 datetime.now()),
                
                ('Pradhan Mantri Awas Yojana - Gramin',
                 'Housing scheme to provide financial assistance for construction of pucca houses in rural areas.',
                 'Houseless rural families and those living in dilapidated houses.',
                 '1. Apply through Gram Panchayat.\n2. Submit income proof and land documents.',
                 'Ongoing',
                 'Ministry of Rural Development',
                 '1800-11-6446',
                 'https://pmayg.nic.in/',
                 datetime.now())
            ]
            
            connection.executemany('''
                INSERT INTO schemes (title, description, eligibility, how_to_apply, deadline, agency, contact, website, posted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_schemes)
        
        connection.commit()
        
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if connection:
            connection.close() 