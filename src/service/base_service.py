from typing import Dict, Any


from src.utils.logger import Logger


logger = Logger.setup()


class BaseService:
    def __init__(self):
        pass

    async def initialize(self):
        pass

    async def start(self):
        pass

    async def close(self):
        pass


    async def process_message(self, message_data: Dict[str, Any]):
        """Process the received message from converted-text-topic-test-v1"""
        try:
            logger.info(f"Processing message: {message_data}")
            
            # Extract message fields if available
            agent_id = message_data.get('agent_id', 'unknown')
            filename = message_data.get('filename', 'unknown')
            timestamp = message_data.get('timestamp', 'unknown')
            text_content = message_data.get('text_content', '')
            
            logger.info(f"Processing text content for agent_id: {agent_id}, filename: {filename}")
            
            # Add your text processing logic here
            # For example: sentiment analysis, acoustic analysis etc.
            
        except Exception as e:
            logger.error(f"Error processing message data: {e}", exc_info=True)

    