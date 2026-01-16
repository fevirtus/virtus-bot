import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

class FootballApiService:
    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-Auth-Token": api_key}
        self._cache = {}
        
    async def _get(self, endpoint: str, cache_ttl: int = 60) -> Optional[Dict]:
        """Generic GET with caching"""
        if not self.api_key:
            print("Football API Key missing!")
            return None

        now = datetime.now()
        if endpoint in self._cache:
            data, timestamp = self._cache[endpoint]
            if (now - timestamp).total_seconds() < cache_ttl:
                return data

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.BASE_URL}{endpoint}", headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self._cache[endpoint] = (data, now)
                        return data
                    elif resp.status == 429:
                        print("Football API Rate Limit Hit")
                        return None
                    else:
                        print(f"Football API Error {resp.status}: {await resp.text()}")
                        return None
        except Exception as e:
            print(f"Football API Request Failed: {e}")
            return None

    async def get_matches_today(self) -> List[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        # Filters: from today to tomorrow to catch late games or timezone diffs coverage
        # But API supports 'dateFrom' and 'dateTo'. Let's just use /matches for today.
        endpoint = f"/matches?dateFrom={today}&dateTo={today}"
        data = await self._get(endpoint, cache_ttl=120) # Cache for 2 mins
        return data.get("matches", []) if data else []

    async def get_matches_range(self, date_from: str, date_to: str) -> List[Dict]:
        """Get matches within a date range"""
        endpoint = f"/matches?dateFrom={date_from}&dateTo={date_to}"
        data = await self._get(endpoint, cache_ttl=300) # Cache for 5 mins
        return data.get("matches", []) if data else []

    async def get_standings(self, league_code: str) -> Optional[Dict]:
        """Get standings for a specific league"""
        endpoint = f"/competitions/{league_code}/standings"
        data = await self._get(endpoint, cache_ttl=1800) # Cache for 30 mins
        return data

    async def get_team_matches(self, team_id: int) -> List[Dict]:
        """Get scheduled matches for a specific team"""
        endpoint = f"/teams/{team_id}/matches?status=SCHEDULED&limit=5"
        data = await self._get(endpoint, cache_ttl=300)
        return data.get("matches", []) if data else []

    async def get_team_history(self, team_id: int, season: Optional[int] = None) -> List[Dict]:
        """Get finished matches for a specific team, optionally for a full season"""
        limit = 50 if season else 5
        endpoint = f"/teams/{team_id}/matches?status=FINISHED&limit={limit}"
        if season:
            endpoint += f"&season={season}"
            
        data = await self._get(endpoint, cache_ttl=300)
        return data.get("matches", []) if data else []
        
    async def get_all_teams_from_leagues(self) -> List[Dict]:
        """Fetch all teams from major leagues to build a search index"""
        leagues = ["PL", "PD", "BL1", "SA", "FL1", "CL"]
        all_teams = []
        
        # Check if we have a "ALL_TEAMS" cache
        if "ALL_TEAMS" in self._cache:
            data, timestamp = self._cache["ALL_TEAMS"]
            if (datetime.now() - timestamp).total_seconds() < 86400: # 24h cache
                return data

        # Fetch concurrently
        tasks = []
        for l in leagues:
            tasks.append(self._get(f"/competitions/{l}/teams", cache_ttl=86400))
            
        results = await asyncio.gather(*tasks)
        
        seen_ids = set()
        for res in results:
            if not res or 'teams' not in res: continue
            for t in res['teams']:
                if t['id'] not in seen_ids:
                    all_teams.append(t)
                    seen_ids.add(t['id'])
        
        self._cache["ALL_TEAMS"] = (all_teams, datetime.now())
        return all_teams

    async def search_team(self, team_name: str) -> Optional[Dict]:
        """Search for a team ID by name (Local Search in Cached Leagues)"""
        # 1. Ensure we have the index
        teams = await self.get_all_teams_from_leagues()
        
        query = team_name.lower().strip()
        
        # 2. Exact/Close Match
        best_match = None
        
        # Clean helper (internal mini-version or just simple)
        def clean(n): return n.lower().replace(" fc", "").replace(" afc", "").strip()
        
        matches = []
        for t in teams:
            t_name = t['name'].lower()
            t_short = (t.get('shortName') or "").lower()
            
            # Exact Match
            if query == t_name or query == t_short:
                return t
                
            # Clean Match
            if query == clean(t_name):
                return t
            
            # Contains
            if query in t_name or query in t_short:
                matches.append(t)
                
        # Return first "contains" match if any (or improve logic to find shortest match?)
        # Example: "Man" -> Matches "Man Utd", "Man City". 
        # "Chelsea" -> Matches "Chelsea FC".
        if matches:
            # Sort by length difference to find "closest" match
            matches.sort(key=lambda x: len(x['name']))
            return matches[0]
            
        return None
