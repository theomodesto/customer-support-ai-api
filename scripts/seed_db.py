#!/usr/bin/env python3
"""
Database seeding script for customer support tickets.

This script loads the Hugging Face customer support dataset and populates
the database with realistic support ticket data.
"""

import sys
import os
import asyncio
from typing import List, Dict, Optional, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from datasets import load_dataset
from app.db.database import SessionLocal, engine
from app.db.database import Base
from app.models.support_ticket import SupportTicket
from app.repository.ai_classification_results_repo import AIClassificationResultRepo

def create_tables():
    """Create database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    
def load_huggingface_dataset(limit: int = 1000) -> List[Dict]:
    """
    Load the customer support dataset from Hugging Face.
    
    Args:
        limit: Maximum number of records to load (default: 1000)
    
    Returns:
        List of ticket dictionaries
    """
    print("Loading customer support dataset from Hugging Face...")
    
    try:
        # Load the dataset
        dataset = load_dataset("tobi-bueck/customer-support-tickets", split="train")
        
        # Filter for English language tickets only
        english_support_tickets: List[Dict] = [
            dict(record) for record in dataset 
            if isinstance(record, dict) and record.get('language', '').lower() == 'en'
        ]
        
        # Limit the number of records
        if len(english_support_tickets) > limit:
            english_support_tickets = english_support_tickets[:limit]
        
        print(f"Loaded {len(english_support_tickets)} English support tickets.")
        return english_support_tickets
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Falling back to sample data...")
        return get_sample_data()

def get_sample_data() -> List[Dict]:
    """
    Get sample support ticket data if Hugging Face dataset is not available.
    """
    return [
        {
            "subject": "Server crashed due to insufficient RAM",
            "body": "Our main application server went down this morning around 9 AM. Error logs show out of memory errors. Please help us resolve this critical issue as we have customers unable to access our services.",
            "queue": "Technical Support",
            "priority": "Critical",
            "language": "en",
            "type": "incident",
            "answer": "Increased server memory allocation to 16GB and optimized application memory usage. Server is now stable and monitoring has been enhanced.",
            "tag_1": "server",
            "tag_2": "memory",
            "tag_3": "critical"
        },
        {
            "subject": "Overcharged on last invoice",
            "body": "I noticed that my last invoice shows charges for the premium plan, but I'm only subscribed to the basic plan. Can you please review and correct this billing error?",
            "queue": "Billing and Payments",
            "priority": "Medium",
            "language": "en",
            "type": "billing_inquiry",
            "answer": "Reviewed account and confirmed billing error. Refund of $50 processed and future billing has been corrected to basic plan rate.",
            "tag_1": "billing",
            "tag_2": "overcharge",
            "tag_3": "refund"
        },
        {
            "subject": "Information about digital marketing services",
            "body": "Hi, I'm interested in learning more about your digital marketing services. Could you provide me with information about pricing, features, and how to get started?",
            "queue": "Customer Service",
            "priority": "Low",
            "language": "en",
            "type": "information_request",
            "answer": "Our digital marketing services include SEO, social media management, and PPC advertising. Pricing starts at $299/month. I'll send you a detailed brochure.",
            "tag_1": "marketing",
            "tag_2": "pricing",
            "tag_3": "information"
        },
        {
            "subject": "API authentication error",
            "body": "We're getting 401 authentication errors when trying to connect to your API. Our API key was working fine last week but now it's not being accepted. Please help us resolve this integration issue.",
            "queue": "IT Support",
            "priority": "Critical",
            "language": "en",
            "type": "technical_issue",
            "answer": "API key had expired. Generated new key and updated documentation. Also implemented better error messages for expired keys.",
            "tag_1": "api",
            "tag_2": "authentication",
            "tag_3": "integration"
        },
        {
            "subject": "Payment failed - credit card issue",
            "body": "My payment failed this month and I received a notice that my account might be suspended. My credit card is valid and has sufficient funds. Can you help process the payment manually?",
            "queue": "Billing and Payments",
            "priority": "Medium",
            "language": "en",
            "type": "payment_issue",
            "answer": "Payment processor had temporary issues. Manual payment processed and account reactivated. Set up backup payment method for future reliability.",
            "tag_1": "payment",
            "tag_2": "credit_card",
            "tag_3": "manual_processing"
        }
    ]

def map_queue_to_category(queue: Optional[str]) -> str:
    """Map dataset queue field to our category system."""
    queue_category_mapping = {
        "Technical Support": "technical",
        "IT Support": "technical",
        "Billing and Payments": "billing",
        "Customer Service": "general",
        "Product Support": "general",
        "General Inquiry": "general",
        "Sales": "general"
    }
    if not queue:
        return "general"
    
    # Direct mapping
    if queue in queue_category_mapping:
        return queue_category_mapping[queue]
    
    # Fuzzy matching
    queue_lower = queue.lower()
    if any(keyword in queue_lower for keyword in ['technical', 'it', 'tech']):
        return "technical"
    elif any(keyword in queue_lower for keyword in ['billing', 'payment', 'invoice']):
        return "billing"
    else:
        return "general"

def map_priority_to_confidence(priority: Optional[str]) -> float:
    """Map dataset priority to confidence score."""
    confidence_mapping = {
        "high": 0.9,
        "critical": 0.9,
        "medium": 0.7,
        "low": 0.5
    }
  
    if not priority:
        return 0.6
    
    priority_lower = priority.lower()
    return confidence_mapping.get(priority_lower, 0.6)

async def seed_database(tickets_data: List[Dict], db: Session, classify: bool = False):
    """
    Seed the database with support ticket data.
    
    Args:
        tickets_data: List of ticket dictionaries
        db: Database session
    """
    print("Seeding database with support tickets...")
    
    successful_inserts = 0
    failed_inserts = 0
    
    for i, ticket_data in enumerate(tickets_data):
        try:
            # Prepare the text fields
            subject = ticket_data.get('subject', '')
            body = ticket_data.get('body', '')
            
            # Skip if no body content
            if not body:
                print(f"Skipping ticket {i+1}: No text content")
                failed_inserts += 1
                continue
            
            # Generate fallback subject if missing
            if not subject:
                # Try to extract first sentence or first 50 characters as subject
                first_sentence = body.split('.')[0].strip()
                if len(first_sentence) <= 100:
                    subject = first_sentence
                else:
                    subject = body[:50].strip() + "..."
                print(f"Generated fallback subject for ticket {i+1}: '{subject}'")
            
            # Ensure subject is not empty after all processing
            if not subject:
                subject = "Support Request"

            # Clean original dataset fields
            queue = ticket_data.get('queue')
            priority = ticket_data.get('priority')
            language = ticket_data.get('language')
            
            # Map to our system fields
            category = map_queue_to_category(queue)
            confidence_score = map_priority_to_confidence(priority)

            
            # Create ticket with all fields properly handled
            ticket = SupportTicket(
                subject=subject,
                body=body,
                queue=queue,           # Preserve original queue field
                priority=priority,     # Preserve original priority field  
                language=language,     # Preserve original language field
                category=category,     # Our mapped category
                confidence_score=confidence_score,  # Our mapped confidence score
                tag_1=ticket_data.get('tag_1'),
                tag_2=ticket_data.get('tag_2'),
                tag_3=ticket_data.get('tag_3'),
                tag_4=ticket_data.get('tag_4'),
                tag_5=ticket_data.get('tag_5'),
                tag_6=ticket_data.get('tag_6'),
                tag_7=ticket_data.get('tag_7'),
                tag_8=ticket_data.get('tag_8')
            )
            
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            
            # Create AI classification (this may fail if AI classifier is not configured)
            if classify:
                print(f"Classifying ticket {i+1}...")
                try:
                    await AIClassificationResultRepo.create_ai_classification(db, ticket)
                except Exception as ai_error:
                    print(f"Warning: AI classification failed for ticket {i+1}: {ai_error}")
                
            successful_inserts += 1
            
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1} tickets...")
                
        except Exception as e:
            print(f"Error inserting ticket {i+1}: {e}")
            failed_inserts += 1
            db.rollback()
            continue
    
    print(f"Seeding completed!")
    print(f"Successful inserts: {successful_inserts}")
    print(f"Failed inserts: {failed_inserts}")

async def main():
    """Main seeding function."""
    print("Starting database seeding process...")
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if database is already seeded
        existing_count = db.query(SupportTicket).count()
        
        if existing_count > 0:
            print(f"Database already contains {existing_count} tickets.")
            response = input("Do you want to add more tickets? (y/N): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
        
        # Load dataset
        classify_bool = False
        limit = int(input("How many tickets to load? (default: 1000): ") or "1000")
        classify = input("Do you want to classify the tickets? (y/N): ")
        if classify.lower() == 'y':
            classify_bool = True
        support_tickets_data = load_huggingface_dataset(limit=limit)
        
        if not support_tickets_data:
            print("No data to seed. Exiting.")
            return
        
        # Seed database
        await seed_database(support_tickets_data, db, classify_bool)
        
        print("Database seeding completed successfully!")
        
    except KeyboardInterrupt:
        print("\nSeeding interrupted by user.")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main()) 