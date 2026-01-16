from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

from repositories.guild import GuildRepository
from repositories.feature_toggle import FeatureToggleRepository
from repositories.config import ConfigRepository

app = FastAPI(title="Virtus Bot Admin")
config_repo = ConfigRepository()
guild_repo = GuildRepository()
feature_repo = FeatureToggleRepository()

class ConfigItem(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    guild_id: Optional[str] = "0"  # Changed to str

class FeatureItem(BaseModel):
    feature_name: str
    is_enabled: bool

class GuildItem(BaseModel):
    id: str  # Changed to str
    name: str

# --- Guilds ---
@app.get("/api/guilds", response_model=List[GuildItem])
async def get_guilds():
    guilds = await guild_repo.get_all()
    # Only return actual guilds
    return [GuildItem(id=str(g.id), name=g.name) for g in guilds]

# --- Configs (Per Guild) ---
@app.get("/api/guilds/{guild_id}/config", response_model=List[ConfigItem])
async def get_guild_configs(guild_id: int):
    configs = await config_repo.get_all(guild_id)
    return [
        ConfigItem(key=c.key, value=c.value, description=c.description, guild_id=str(c.guild_id))
        for c in configs
    ]

@app.post("/api/guilds/{guild_id}/config", response_model=ConfigItem)
async def set_guild_config(guild_id: int, item: ConfigItem):
    config = await config_repo.set(guild_id, item.key, item.value, item.description)
    if not config:
        raise HTTPException(status_code=500, detail="Failed to save config")
    return ConfigItem(key=config.key, value=config.value, description=config.description, guild_id=str(config.guild_id))

@app.delete("/api/guilds/{guild_id}/config/{key}")
async def delete_guild_config(guild_id: int, key: str):
    success = await config_repo.delete(guild_id, key)
    if not success:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"status": "success"}

# --- Validation ---
@app.get("/api/guilds/{guild_id}/members/{user_id}")
async def check_member_exists(guild_id: int, user_id: int, request: Request):
    bot = request.app.state.bot
    guild = bot.get_guild(guild_id)
    if not guild:
         raise HTTPException(status_code=404, detail="Guild not found in Bot cache")
    
    member = guild.get_member(user_id)
    if not member:
         raise HTTPException(status_code=404, detail="Member not found")
    
    return {"status": "exists", "name": member.name, "display_name": member.display_name}

@app.get("/api/guilds/{guild_id}/details")
async def get_guild_details(guild_id: int, request: Request):
    bot = request.app.state.bot
    guild = bot.get_guild(guild_id)
    if not guild:
        return {"id": str(guild_id), "found": False}
    
    return {
        "id": str(guild.id),
        "name": guild.name,
        "member_count": guild.member_count,
        "owner": str(guild.owner),
        "icon_url": str(guild.icon.url) if guild.icon else None,
        "found": True
    }

@app.get("/api/guilds/{guild_id}/channels/{channel_id}")
async def check_channel_exists(guild_id: int, channel_id: int, request: Request):
    bot = request.app.state.bot
    guild = bot.get_guild(guild_id)
    if not guild:
         raise HTTPException(status_code=404, detail="Guild not found in Bot cache")
    
    channel = guild.get_channel(channel_id)
    if not channel:
         raise HTTPException(status_code=404, detail="Channel not found")
    
    return {"status": "exists", "name": channel.name, "type": str(channel.type)}

@app.get("/api/guilds/{guild_id}/football/teams")
async def search_football_teams(guild_id: int, query: str, request: Request):
    bot = request.app.state.bot
    cog = bot.get_cog("FootballCog")
    if not cog:
        raise HTTPException(status_code=503, detail="Football service not available")
    
    # Use internal helper which checks config Key
    api = await cog._get_api(guild_id)
    if not api:
        raise HTTPException(status_code=400, detail="Football API Key not configured")
        
    team = await api.search_team(query)
    if not team:
        return []
    
    # API wrapper currently returns single match OR None.
    # We should ideally return a list.
    # If safe, let's wrap it in a list.
    return [team]

# --- Features (Per Guild) ---
@app.get("/api/guilds/{guild_id}/features", response_model=List[FeatureItem])
async def get_guild_features(guild_id: int):
    # List of known features
    # List of known features
    known_features = ["home_debt", "score", "noi_tu", "football"]
    result = []
    
    # Get all active features from DB
    db_features = await feature_repo.get_all_for_guild(guild_id)
    db_map = {f.feature_name: f.is_enabled for f in db_features}

    for fname in known_features:
        result.append(FeatureItem(feature_name=fname, is_enabled=db_map.get(fname, False)))
    
    return result

@app.post("/api/guilds/{guild_id}/features", response_model=FeatureItem)
async def set_guild_feature(guild_id: int, item: FeatureItem):
    toggle = await feature_repo.set(guild_id, item.feature_name, item.is_enabled)
    if not toggle:
        raise HTTPException(status_code=500, detail="Failed to save feature")
    return FeatureItem(feature_name=toggle.feature_name, is_enabled=toggle.is_enabled)

# --- Backward Compatibility (Redirect to Guild 0) ---
@app.get("/api/config", response_model=List[ConfigItem])
async def get_configs_legacy():
    return await get_guild_configs(0)

@app.post("/api/config", response_model=ConfigItem)
async def set_config_legacy(item: ConfigItem):
    return await set_guild_config(0, item)

@app.delete("/api/config/{key}")
async def delete_config_legacy(key: str):
    return await delete_guild_config(0, key)

# Mount static files
app.mount("/", StaticFiles(directory="web/static", html=True), name="static")

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8000)
