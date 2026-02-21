"""
Load Testing Dataset Generator
Generates realistic transaction datasets for performance testing
"""
import csv
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
import argparse

class TransactionGenerator:
    """Generate realistic financial transactions for testing"""
    
    COUNTRIES = [
        "USA", "UK", "Canada", "Germany", "France", "Japan", "Australia",
        "Singapore", "Switzerland", "Netherlands", "Hong Kong", "UAE"
    ]
    
    HIGH_RISK_COUNTRIES = ["Iran", "North Korea", "Syria", "Cuba", "Sudan"]
    
    TRANSACTION_TYPES = [
        "wire_transfer", "ach", "check", "cash_deposit", "cash_withdrawal",
        "international_wire", "domestic_transfer", "atm_withdrawal"
    ]
    
    CUSTOMER_TYPES = ["individual", "business", "corporate", "government"]
    
    def __init__(self, count: int, output_file: str):
        self.count = count
        self.output_file = output_file
        self.start_date = datetime.now() - timedelta(days=365)
        
    def generate_amount(self) -> float:
        """Generate realistic transaction amount"""
        # 70% small transactions (< $1000)
        # 20% medium transactions ($1000 - $10000)
        # 8% large transactions ($10000 - $100000)
        # 2% very large transactions (> $100000)
        
        rand = random.random()
        if rand < 0.70:
            return round(random.uniform(10, 1000), 2)
        elif rand < 0.90:
            return round(random.uniform(1000, 10000), 2)
        elif rand < 0.98:
            return round(random.uniform(10000, 100000), 2)
        else:
            return round(random.uniform(100000, 1000000), 2)
            
    def generate_customer_id(self) -> str:
        """Generate customer ID"""
        return f"CUST{random.randint(10000, 99999)}"
        
    def generate_account_number(self) -> str:
        """Generate account number"""
        return f"{random.randint(1000000000, 9999999999)}"
        
    def generate_timestamp(self) -> str:
        """Generate random timestamp within last year"""
        days_ago = random.randint(0, 365)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = self.start_date + timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )
        return timestamp.isoformat()
        
    def generate_transaction(self) -> Dict:
        """Generate single transaction"""
        # Occasionally generate suspicious patterns
        is_suspicious = random.random() < 0.05  # 5% suspicious
        
        amount = self.generate_amount()
        
        # Make suspicious transactions more likely to be large
        if is_suspicious:
            amount = round(random.uniform(10000, 500000), 2)
            
        country = random.choice(self.COUNTRIES)
        
        # Suspicious transactions more likely to high-risk countries
        if is_suspicious and random.random() < 0.3:
            country = random.choice(self.HIGH_RISK_COUNTRIES)
            
        return {
            "transaction_id": str(uuid.uuid4()),
            "customer_id": self.generate_customer_id(),
            "account_number": self.generate_account_number(),
            "amount": amount,
            "currency": "USD",
            "transaction_type": random.choice(self.TRANSACTION_TYPES),
            "timestamp": self.generate_timestamp(),
            "source_country": country,
            "destination_country": random.choice(self.COUNTRIES),
            "customer_type": random.choice(self.CUSTOMER_TYPES),
            "risk_score": round(random.uniform(0, 1), 3) if is_suspicious else round(random.uniform(0, 0.5), 3),
            "is_flagged": "true" if is_suspicious else "false"
        }
        
    def generate_dataset(self):
        """Generate complete dataset"""
        print(f"Generating {self.count:,} transactions...")
        
        fieldnames = [
            "transaction_id", "customer_id", "account_number", "amount",
            "currency", "transaction_type", "timestamp", "source_country",
            "destination_country", "customer_type", "risk_score", "is_flagged"
        ]
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            batch_size = 10000
            for i in range(0, self.count, batch_size):
                batch_count = min(batch_size, self.count - i)
                transactions = [self.generate_transaction() for _ in range(batch_count)]
                writer.writerows(transactions)
                
                progress = ((i + batch_count) / self.count) * 100
                print(f"Progress: {progress:.1f}% ({i + batch_count:,}/{self.count:,})")
                
        print(f"✓ Dataset generated: {self.output_file}")
        print(f"  Total transactions: {self.count:,}")
        print(f"  File size: {self._get_file_size()} MB")
        
    def _get_file_size(self) -> float:
        """Get file size in MB"""
        import os
        size_bytes = os.path.getsize(self.output_file)
        return round(size_bytes / (1024 * 1024), 2)


def main():
    parser = argparse.ArgumentParser(description='Generate transaction datasets for load testing')
    parser.add_argument(
        'count',
        type=int,
        choices=[100000, 500000, 1000000],
        help='Number of transactions to generate (100k, 500k, or 1M)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: transactions_{count}.csv)'
    )
    
    args = parser.parse_args()
    
    output_file = args.output or f"transactions_{args.count}.csv"
    
    generator = TransactionGenerator(args.count, output_file)
    generator.generate_dataset()


if __name__ == "__main__":
    main()
