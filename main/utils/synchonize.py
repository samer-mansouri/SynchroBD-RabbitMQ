##SYNC DATABASES
from .database import DatabaseManager
import datetime
from .producer import RabbitMQProducer

class Synchronizer:

    def __init__(self, config1, branch_office):
        self.branch_office_db = DatabaseManager(config1)
        self.last_sync_file = f'last_sync_{branch_office}.txt'
        
        
    def get_last_sync_time(self):
        """
        Reads the last sync time from a file.
        """
        try:
            with open(self.last_sync_file, 'r') as f:
                last_sync_time = f.read().strip()
            # Convert the stored string back to a datetime object
            return datetime.datetime.fromisoformat(last_sync_time)
        except FileNotFoundError:
            # If the file does not exist, assume a default old date
            return datetime.datetime.min

    def update_last_sync_time(self):
        """
        Updates the last sync time to the current time.
        """
        with open(self.last_sync_file, 'w') as f:
            # Store the current time in ISO format
            f.write(datetime.datetime.now().isoformat())

    def get_updates_from_branch_office(self):
        """
        Fetches sales data from the branch office database where created_at or updated_at is greater than the last sync time.
        """
        last_sync_time = self.get_last_sync_time()
        
        query = """
        SELECT date, region, product, qty, cost, amt, tax, total, created_at, updated_at, id
        FROM sales
        WHERE created_at > %s OR updated_at > %s
        ORDER BY created_at ASC, updated_at ASC;
        """
        
        # Fetch the records that were created or updated after the last sync time
        records = self.branch_office_db.execute(query, (last_sync_time, last_sync_time), fetch=True)
        
        # Process the records (e.g., insert them into the head office database)
        
        # After processing the records, update the last sync time
        self.update_last_sync_time()
        
        return records
    
    def publish_to_message_queue(self, records):
        """
        Publishes the records to the RabbitMQ message queue.
        """
        producer = RabbitMQProducer()
        
        for record in records:
            action = 'update' if record['updated_at'] > record['created_at'] else 'create'
            message = {
                'action': action,
                'data': record
            }
            producer.publish_message(action, message)
            
    def synchronize(self):
        """
        Synchronizes the branch office database with the head office database.
        """
        records = self.get_updates_from_branch_office()
        self.publish_to_message_queue(records)