import boto3
import os
import time
import uuid

class DynamoPersistence:
    def __init__(self):
        # Automatically picks up AWS credentials from Env Vars or EC2 IAM Role
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.table_name = "AGI1_TaskEvents"
        self.table = self.dynamodb.Table(self.table_name)

    def add_event(self, role, task_input, status, score, latency, winner):
        try:
            item = {
                'event_id': str(uuid.uuid4()),
                'timestamp': int(time.time()),
                'role': role,
                'task_input': task_input,
                'status': status,
                'kpi_score': str(score),
                'latency': str(latency),
                'arbitration_winner': winner
            }
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            # Fallback to local log if DynamoDB is unreachable
            print(f"⚠️ Cloud Persistence Error: {e}")
            return False

# Global Instance
DB_CLOUD = DynamoPersistence()
