"""
Schedule automatic sync of tools
Run this to sync tools periodically
"""
import asyncio
import schedule
import time
from datetime import datetime
from sync_tools import sync_tools

# Configuration
SYNC_INTERVAL_HOURS = 24  # Sync every 24 hours
SYNC_TIME = "02:00"  # Run at 2 AM daily

async def run_sync_job():
    """Run sync job"""
    print(f"\n⏰ Scheduled sync triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await sync_tools()

def schedule_sync_job():
    """Schedule the sync job"""
    schedule.every(SYNC_INTERVAL_HOURS).hours.do(lambda: asyncio.run(run_sync_job()))
    # Or schedule at specific time:
    # schedule.every().day.at(SYNC_TIME).do(lambda: asyncio.run(run_sync_job()))

def main():
    """Main scheduler loop"""
    print("="*60)
    print("🕐 AI Tools Sync Scheduler Started")
    print(f"⏰ Sync interval: Every {SYNC_INTERVAL_HOURS} hours")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Schedule the job
    schedule_sync_job()
    
    # Run once immediately
    print("\n▶️  Running initial sync...")
    asyncio.run(run_sync_job())
    
    print("\n⏳ Waiting for next scheduled run...")
    print("💡 Press Ctrl+C to stop\n")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped")

if __name__ == "__main__":
    main()
