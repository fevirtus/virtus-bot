
import asyncio
from services.football_api import FootballApiService
from repositories.config import ConfigRepository

async def test_search():
    # Use the guild ID from the logs: 536422615649091595
    # We need the API Key. I can try to read it from DB or just rely on the existing modules.
    # The ConfigRepository can fetch it.
    
    config_repo = ConfigRepository()
    guild_id = 536422615649091595
    key = await config_repo.get(guild_id, "FOOTBALL_API_KEY", "")
    
    if not key:
        print("No API Key found for test.")
        return

    print(f"Using Key: {key[:5]}...")
    api = FootballApiService(key)
    
    queries = ["chelsea", "man utd", "köln", "ch"]
    
    for q in queries:
        print(f"\n--- Searching for: {q} ---")
        try:
            # We want to see the raw teams list, so let's check _get directly if possible, or modify search logic temporarily
            endpoint = f"/teams?name={q}"
            data = await api._get(endpoint, cache_ttl=0) 
            
            if not data:
                print("No Data")
                continue
                
            teams = data.get("teams", [])
            print(f"Count: {data.get('count')}")
            for t in teams:
                print(f" - [{t['id']}] {t['name']} (Short: {t.get('shortName')})")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
