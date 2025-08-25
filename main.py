"""
Main runner for Halloween Quest Bot + API
Runs both Telegram bot and FastAPI server
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import uvicorn

from config import config
from bot import main as bot_main
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_api_server():
    """Run FastAPI server"""
    config_uvicorn = uvicorn.Config(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()

async def main():
    """Main function to run both bot and API server"""
    logger.info("Starting Halloween Quest Bot + API Server")
    
    # Initialize database
    await db.init_db()
    logger.info("Database initialized")
    
    # Create tasks for bot and API server
    bot_task = asyncio.create_task(bot_main())
    api_task = asyncio.create_task(run_api_server())
    
    logger.info(f"Starting API server on {config.API_HOST}:{config.API_PORT}")
    logger.info("Starting Telegram bot...")
    
    # Run both concurrently
    try:
        await asyncio.gather(bot_task, api_task)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
