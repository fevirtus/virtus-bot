import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional
from datetime import datetime, timedelta
import asyncio

from repositories.football import FootballRepository
from repositories.config import ConfigRepository
from services.football_api import FootballApiService

class FootballCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = FootballRepository()
        self.config_repo = ConfigRepository()
        self.api_service = None # Init lazily
        self._notified_upcoming = set() 
        self._notified_result = set()
        self.check_matches.start()

    async def _get_api(self, guild_id: int):
        key = await self.config_repo.get(guild_id, "FOOTBALL_API_KEY", "")
        if not key:
            return None
        return FootballApiService(key)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if service is enabled (handled by main bot logic usually, but here specifically for this Cog)
        # Check channel restriction
        allowed_str = await self.config_repo.get(interaction.guild_id, "CHANNEL_FOOTBALL_IDS", "")
        if not allowed_str:
            return True # No restriction
            
        allowed_ids = [int(x.strip()) for x in allowed_str.split(',') if x.strip().isdigit()]
        if not allowed_ids:
            return True # Empty or invalid config implies no restriction
            
        if interaction.channel_id not in allowed_ids:
            await interaction.response.send_message(f"⚠️ commands are only allowed in: {', '.join(f'<#{cid}>' for cid in allowed_ids)}", ephemeral=True)
            return False
            
        return True

    # --- Slash Commands Group ---
    fb_group = app_commands.Group(name="fb", description="Football services commands")



    @fb_group.command(name="history", description="View team match history")
    @app_commands.describe(team="Team name", season="Year (e.g. 2023). Default: current season matches")
    async def history_slash(self, interaction: discord.Interaction, team: str, season: Optional[int] = None):
        await interaction.response.defer()
        
        api = await self._get_api(interaction.guild_id)
        if not api: return await interaction.followup.send("Missing API Key.")
        
        team_data = await api.search_team(team)
        if not team_data: return await interaction.followup.send("Team not found.")
        
        matches = await api.get_team_history(team_data['id'], season=season)
        if not matches: return await interaction.followup.send("No history found.")

        # Summary Stats
        wins = draws = losses = 0
        target_id = team_data['id']
        
        history_text = []
        for m in matches[:15]: # Show last 15
            home = m['homeTeam']
            away = m['awayTeam']
            score_h = m['score']['fullTime']['home']
            score_a = m['score']['fullTime']['away']
            
            # Outcome
            is_home = (home['id'] == target_id)
            goals_for = score_h if is_home else score_a
            goals_against = score_a if is_home else score_h
            
            result = "➖"
            if goals_for > goals_against: 
                result = "✅"
                wins += 1
            elif goals_for < goals_against: 
                result = "❌"
                losses += 1
            else:
                draws += 1
                
            opponent = away['name'] if is_home else home['name']
            date_str = m['utcDate'][:10]
            
            history_text.append(f"{result} vs **{opponent}** ({goals_for}-{goals_against}) ` {date_str} `")
            
        embed = discord.Embed(title=f"📜 History: {team_data['name']}", color=discord.Color.blue())
        if season: embed.description = f"**Season {season}**"
        
        embed.add_field(name="Form (Last 15)", value="\n".join(history_text) if history_text else "No matches", inline=False)
        embed.add_field(name="Summary (This Set)", value=f"Win: {wins} | Draw: {draws} | Loss: {losses}", inline=False)
        
        await interaction.followup.send(embed=embed)

    class StandingsView(discord.ui.View):
        def __init__(self, cog, guild_id: int):
            super().__init__(timeout=180)
            self.cog = cog
            self.guild_id = guild_id
            self.add_item(self.LeagueSelect(cog, guild_id))

        class LeagueSelect(discord.ui.Select):
            def __init__(self, cog, guild_id):
                self.cog = cog
                self.guild_id = guild_id
                
                # Common Leagues Options
                options = [
                    discord.SelectOption(label="Premier League", value="PL", description="England", emoji="🏴󠁧󠁢󠁥󠁮󠁧󠁿"),
                    discord.SelectOption(label="La Liga", value="PD", description="Spain", emoji="🇪🇸"),
                    discord.SelectOption(label="Bundesliga", value="BL1", description="Germany", emoji="🇩🇪"),
                    discord.SelectOption(label="Serie A", value="SA", description="Italy", emoji="🇮🇹"),
                    discord.SelectOption(label="Ligue 1", value="FL1", description="France", emoji="🇫🇷"),
                    discord.SelectOption(label="Champions League", value="CL", description="Europe", emoji="🇪🇺"),
                ]
                super().__init__(placeholder="Select a league...", min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                league_code = self.values[0]
                embed = await self.cog.build_standings_embed(self.guild_id, league_code)
                if embed:
                    await interaction.edit_original_response(embed=embed, view=self.view)
                else:
                    await interaction.followup.send(f"Could not load data for {league_code}", ephemeral=True)

    def _clean_name(self, name: str) -> str:
        import re
        # Remove common prefixes like "1. ", "1 " 
        # Remove common suffixes like " FC", " AFC", etc. (case insensitive)
        
        # 1. Remove numbering prefix (e.g. "1. FC Koln" -> "FC Koln")
        name = re.sub(r'^\d+[\.\s]+', '', name)
        
        # 2. Remove common suffixes
        # \b ensures whole word match
        suffixes = [
            "FC", "AFC", "CF", "SC", "BV", "NV", "AC", "AS", "Hotspur"
        ]
        pattern = r'\b(' + '|'.join(suffixes) + r')\b'
        clean = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # 3. Cleanup extra spaces and special chars
        clean = clean.replace("&", "")
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean

    def _is_interested(self, team_name: str, interested_list: list) -> bool:
        if not interested_list: return False
        
        # Normalize Data Name
        # e.g. "1. FC Köln" -> "Köln"
        raw_clean = self._clean_name(team_name).lower()
        
        # Aliases Map (Normalized keys)
        aliases = {
            "man utd": ["manchester united"],
            "man use": ["manchester united"],
            "man city": ["manchester city"],
            "psg": ["paris saint-germain"],
            "spurs": ["tottenham"],
            "wolves": ["wolverhampton wanderers"],
            "brighton": ["brighton hove albion"],
            "leverkusen": ["bayer leverkusen"],
            "dortmund": ["borussia dortmund"],
            "bayern": ["bayern munich", "bayern munchen"],
            "inter": ["inter milano", "internazionale"],
            "milan": ["ac milan"],
            "real": ["real madrid"],
            "atletico": ["atletico madrid", "my atletico"],
            "barca": ["fc barcelona"],
            "koln": ["1. fc koln", "fc koln"]
        }
        
        for interested in interested_list:
            # Normalize Configured Name
            # e.g. "1. FC Köln" -> "koln"
            user_clean = self._clean_name(interested).lower()
            
            # 1. Direct Comparison (Clean vs Clean)
            # "koln" == "koln"
            if user_clean == raw_clean: return True
            if user_clean in raw_clean: return True # "chelsea" in "chelsea"
            
            # 2. Check Aliases (Bidirectional check)
            # If user saved "Man Utd", check if matches "Manchester United"
            # If user saved "Manchester United", check if matches "Man Utd"
            
            for alias, targets in aliases.items():
                alias_clean = self._clean_name(alias).lower()
                
                # Check if 'interested' is an alias
                if user_clean == alias_clean: 
                    # Does the real team name match any target?
                    for t in targets:
                         if self._clean_name(t).lower() == raw_clean: return True
                         
                # Check if current team 'raw_clean' is effectively one of the targets
                # And user has the alias
                # (Complex, sticking to simple match first)
                pass 
                
            # 3. Fallback: Raw substring
            if interested.lower() in team_name.lower(): return True
                    
        return False

    async def build_standings_embed(self, guild_id: int, league_code: str) -> Optional[discord.Embed]:
        api = await self._get_api(guild_id)
        if not api: return None
        
        data = await api.get_standings(league_code)
        if not data or 'standings' not in data: return None
            
        table = None
        for s in data['standings']:
            if s['type'] == 'TOTAL':
                table = s['table']
                break
        if not table: return None
        
        comp_name = data.get('competition', {}).get('name', league_code)
        
        # Interested Teams
        interested_config = await self.config_repo.get(guild_id, "FOOTBALL_TEAMS", "")
        interested_teams = [t.strip().lower() for t in interested_config.split(',')] if interested_config else []

        # ANSI Table Construction
        lines = []
        # Header: Hạng(3) CLB(15) Tr(2) T-H-B(7) HS(3) Đ(3)
        header = f"\u001b[1;37m{'Hạng':<4} {'CLB':<16} {'Tr':<2} {'T-H-B':<7} {'HS':<3} {'Đ':<3}\u001b[0m"
        lines.append(header)
        lines.append("\u001b[0;30m" + "-" * 42 + "\u001b[0m") 
        
        for team in table[:25]:
            pos = str(team['position'])
            name = team['team']['name']
            
            # Use Clean Name for display (Shorter)
            display_name = self._clean_name(name)
            
            # Smart Truncate
            if len(display_name) > 15:
                 display_name = display_name[:14] + "…"
            
            played = str(team['playedGames'])
            won = str(team['won'])
            draw = str(team['draw'])
            lost = str(team['lost'])
            pts = str(team['points'])
            gd = str(team['goalDifference'])
            
            wdl = f"{won}-{draw}-{lost}"
            
            # Default Coloring
            style = "\u001b[0;37m"
            suffix = "\u001b[0m"
            
            is_interested = self._is_interested(name, interested_teams)
            
            if is_interested:
                # Blue Background to simulate highlight
                style = "\u001b[0;37;44m" 
            elif int(pos) <= 4:
                style = "\u001b[0;32m" # Green Text
            elif int(pos) >= 18:
                style = "\u001b[0;31m" # Red Text
            
            line = f"{style}{pos:<4} {display_name:<16} {played:<2} {wdl:<7} {gd:<3} {pts:<3}{suffix}"
            lines.append(line)

        embed = discord.Embed(title=f"🏆 {comp_name}", color=discord.Color.from_rgb(44, 47, 51))
        embed.description = f"```ansi\n{chr(10).join(lines)}\n```" 
        embed.set_footer(text="Xanh Dương: Đội của bạn | Xanh Lá: Top 4 | Đỏ: Nhóm xuống hạng")
        
        return embed

    @fb_group.command(name="standings", description="View league standings")
    @app_commands.describe(league_code="League Code (e.g. PL, PD, SA, BL1, FL1, CL)")
    async def standings_slash(self, interaction: discord.Interaction, league_code: str = "PL"):
        await interaction.response.defer()
        
        embed = await self.build_standings_embed(interaction.guild_id, league_code)
        if not embed:
             return await interaction.followup.send(f"Could not load standings for `{league_code}`. Check API Key or Code.")
        
        view = self.StandingsView(self, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view)

    @fb_group.command(name="schedule", description="View upcoming match schedule")
    @app_commands.describe(league="Filter by league code (e.g. PL, PD)")
    async def schedule_slash(self, interaction: discord.Interaction, league: Optional[str] = None):
        # Default to 10 days to fit within typical API limits while showing "upcoming" context
        days = 10 
        await interaction.response.defer()
        
        api = await self._get_api(interaction.guild_id)
        if not api:
            return await interaction.followup.send("⚠️ API Key missing. Configure in Dashboard.")

        today = datetime.now()
        end_date = today + timedelta(days=days)
        
        matches = await api.get_matches_range(
            today.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        if not matches:
            return await interaction.followup.send("Không tìm thấy trận đấu nào.")

        # Filter Logic (Leagues)
        config_leagues = await self.config_repo.get(interaction.guild_id, "FOOTBALL_LEAGUES", "")
        target_leagues = set()
        
        if config_leagues:
            target_leagues.update([l.strip().lower() for l in config_leagues.split(',') if l.strip()])
        if league: target_leagues.add(league.lower())

        filtered = []
        if target_leagues:
            for m in matches:
                comp_name = m.get('competition', {}).get('name', '').lower()
                comp_code = m.get('competition', {}).get('code', '').lower()
                if any(t in comp_name or t == comp_code for t in target_leagues):
                    filtered.append(m)
        else:
            filtered = matches # No filter = All matches (might be too many, but API usually limits free tier anyway)
            
        if not filtered:
             return await interaction.followup.send("Không có trận đấu nào trong các giải đã chọn.")

        # Sort by time
        filtered.sort(key=lambda x: x['utcDate'])

        # Grid Layout using Embed Fields
        # Title: Lịch Thi Đấu
        embed = discord.Embed(title=f"📅 Lịch Thi Đấu ({len(filtered)} trận)", color=discord.Color.blue())
        
        count = 0
        for m in filtered[:18]: # Limit 18 matches (Discord limit 25 fields, let's keep it safe)
            home = m['homeTeam']['name']
            away = m['awayTeam']['name']
            
            # Parse Time
            dt = datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00'))
            # Format: 22:00 22/01
            time_str = dt.strftime('%H:%M %d/%m')
            status = m['status']
            
            # Icon/State
            state_text = f"🕐 {time_str}"
            score_text = "vs"
            
            if status in ['FINISHED', 'IN_PLAY', 'PAUSED']:
                s_home = m['score']['fullTime']['home']
                s_away = m['score']['fullTime']['away']
                score_text = f"{s_home} - {s_away}"
                if status == 'FINISHED':
                    state_text = f"✅ KT {dt.strftime('%d/%m')}"
                else:
                    state_text = f"🔴 Phút {m.get('minute', '?')}"
            
            # Highlight Interested Teams
            interested_config = await self.config_repo.get(interaction.guild_id, "FOOTBALL_TEAMS", "")
            interested_teams = [t.strip().lower() for t in interested_config.split(',')] if interested_config else []
            
            is_interested = any(it in home.lower() for it in interested_teams) or \
                            any(it in away.lower() for it in interested_teams)
            
            # Card Title
            # Use Icons if possible, else Bold
            # 🏠 Man Utd vs 🚌 Man City
            # If interested, add Star
            prefix = "⭐ " if is_interested else ""
            
            field_name = f"{prefix}{home} {score_text} {away}"
            field_val = f"{state_text}\n🏆 {m['competition']['code']}"
            
            embed.add_field(name=field_name, value=field_val, inline=True)
            count += 1
            
        if len(filtered) > 18:
            embed.set_footer(text=f"Còn {len(filtered) - 18} trận đấu khác...")
            
        await interaction.followup.send(embed=embed)

    @fb_group.command(name="sub", description="Subscribe to team updates")
    async def sub_slash(self, interaction: discord.Interaction, team_name: str):
        await interaction.response.defer()
        api = await self._get_api(interaction.guild_id)
        if not api: return await interaction.followup.send("Missing API Key.")

        team = await api.search_team(team_name)
        if not team:
            return await interaction.followup.send(f"❌ Could not find team: {team_name}")
        
        success = await self.repo.add_subscription(interaction.guild_id, interaction.channel_id, team['name'], team['id'])
        if success:
            await interaction.followup.send(f"✅ Subscribed to **{team['name']}** updates in this channel.")
        else:
            await interaction.followup.send(f"⚠️ Already subscribed to {team['name']}.")

    @fb_group.command(name="unsub", description="Unsubscribe from team")
    async def unsub_slash(self, interaction: discord.Interaction, team_name: str):
         await interaction.response.defer()
         success = await self.repo.remove_subscription(interaction.guild_id, team_name)
         msg = f"✅ Unsubscribed from {team_name}." if success else "❌ Subscription not found."
         await interaction.followup.send(msg)

    @fb_group.command(name="list", description="List subscriptions")
    async def list_slash(self, interaction: discord.Interaction):
        subs = await self.repo.get_guild_subscriptions(interaction.guild_id)
        if not subs:
            return await interaction.response.send_message("No football subscriptions in this server.")
        
        msg = "**Subscriptions:**\n" + "\n".join([f"• {s.team_name} (<#{s.channel_id}>)" for s in subs])
        await interaction.response.send_message(msg)

    @tasks.loop(minutes=2)
    async def check_matches(self):
        subs = await self.repo.get_all_subscriptions()
        if not subs: return

        guild_ids = set(s.guild_id for s in subs)
        
        for gid in guild_ids:
            api = await self._get_api(gid)
            if not api: continue
            
            matches = await api.get_matches_today()
            if not matches: continue
            
            guild_subs = [s for s in subs if s.guild_id == gid]
            
            for m in matches:
                mid = m['id']
                home_id = m['homeTeam']['id']
                away_id = m['awayTeam']['id']
                status = m['status']
                match_time = datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00'))
                
                relevant_subs = [s for s in guild_subs if s.team_id in [home_id, away_id]]
                if not relevant_subs: continue
                
                # 1. Upcoming Notification
                if status == 'TIMED': 
                    now = datetime.utcnow().replace(tzinfo=match_time.tzinfo)
                    diff = (match_time - now).total_seconds()
                    
                    if 540 <= diff <= 660:
                        if mid not in self._notified_upcoming:
                            await self._notify(relevant_subs, m, "UPCOMING")
                            self._notified_upcoming.add(mid)
                            
                # 2. Result Notification
                if status == 'FINISHED':
                    if mid not in self._notified_result:
                         await self._notify(relevant_subs, m, "FINISHED")
                         self._notified_result.add(mid)

    async def _notify(self, subs, match, type):
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        
        if type == "UPCOMING":
            title = "⚽ Trận đấu sắp diễn ra!"
            desc = f"**{home}** vs **{away}**\nBắt đầu trong 10 phút!"
            color = discord.Color.orange()
            
        elif type == "FINISHED":
            title = "🏁 Kết quả trận đấu"
            score = f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}"
            desc = f"**{home}** {score} **{away}**\nTrận đấu đã kết thúc."
            color = discord.Color.gold()
        
        embed = discord.Embed(title=title, description=desc, color=color)
        
        target_channels = set(s.channel_id for s in subs)
        
        for cid in target_channels:
            channel = self.bot.get_channel(cid)
            if channel:
                try:
                    await channel.send(embed=embed)
                except: pass

    @check_matches.before_loop
    async def before_check_matches(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(FootballCog(bot))
