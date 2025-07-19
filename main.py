from keep_alive import keep_alive

keep_alive()

import discord
from discord.ext import commands, tasks
import json
import random, time
import asyncio
import os
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Required for reading command content
bot = commands.Bot(command_prefix='!', intents=intents)

# File paths
DATA_FILE = 'data.json'
CONFIG_FILE = 'config.json'

# Global variables
user_balances = {}
bot_stats = {'total_given': 0, 'total_in_system': 0, 'last_giveaway': None}
player_stats = {}
config = {}
user_boosts = {}
user_items = {}
user_inventories = {}  # Track user inventories for items won
user_cooldowns = {}  # Track command cooldowns to prevent spam

# Item values for exchange system (per individual item)
ITEM_VALUES = {
    "Rainbow Mini Chest": 600000,
    "Random Huge": 9000000,
    "High Tier Huge": 30000000,
    "Titanic": 4500000000,
    "Titanic!": 4500000000,  # Alternative name
    "Trash Card": 2,
    "Rainbow Trash Card": 10,
    "Exclusive Card": 250000,
    "Huge Exclusive Card": 4000000,
    "Titanic Card": 1100000000,
    "Millionaire Raffle Ticket": 5000,
    "Booth Slot Voucher": 3000,
    "Daycare Slot Voucher": 0,
    "Random Spinny Wheel Ticket": 40000,
    "Fantasy Spinny Wheel Ticket": 30000,
    "Exclusive Raffle Ticket": 8000000,
    "Old Boot": 1,
    "Party Time": 120000000,
    "Nightmare Orb": 220000000,
    "Boss Lucky Block": 400000000,
    "Breakable Mayhem": 1100000000,
    "Diamond Orb": 1400000000,
    "Diamond Gift Bag Hunter": 1800000000,
    "Mega Chest Breaker": 4000000000,
    "Huge": 9000000,  # Consolidated name for Random Huge
    # Add more items as they appear in chests
    "Clan Voucher": 130000000,  # Estimated values for mega chest items
    "Diamond Fishing Rod": 3000000,
    "Nightmare Fuel": 99000,
    "Mastery Potion": 400000,
    "Glitched Drive": 70000000,
    "Diamond Shovel": 5000000,
    "Ultimate XP Potion": 100000,
    "Mini Chest": 20000,
    "Ultra Pet Cube": 50000,
    "Titanic XP Potion": 1500000,
    "Bucket 'o Magic": 20000,
    "Charm Chisels": 100000,
    "Exotic Treasure Flag": 25000,
    "Mega Charm Chest": 80000000,
    "Mega Ultimate Chest": 15000000,
    "Magic Shard": 40000,
    "Mega Potions Chest": 2000000,
    "Mega Enchant Chest": 2100000
}

# Shop items configuration
SHOP_ITEMS = {
    "clover": {
        "id": "S1",
        "name": "Coins Clover Boost",
        "emoji": "<:boost01:1395693938307764274>",
        "price": 10000000,
        "boost": 0.025,  # 2.5%
        "duration": 3600,  # 1 hour in seconds
        "short_description": "Small rewards boost!",
        "description": "This boosts your win rewards by 2.5%! Lasts for 1 hour"
    },
    "coins": {
        "id": "S2",
        "name": "Ultra Coins Boost",
        "emoji": "<:boost02:1395694130780176485>",
        "price": 25000000,
        "boost": 0.04,  # 4%
        "duration": 10800,  # 3 hours in seconds
        "short_description": "Medium rewards boost!",
        "description": "This boosts your win rewards by 4%! Lasts for 3 hours"
    },
    "vip": {
        "id": "S3",
        "name": "VIP",
        "emoji": "<:vip:1395694971218038824>",
        "price": 50000000,
        "boost": 0.055,  # 5.5%
        "duration": -1,  # Permanent
        "short_description": "Permanent rewards boost!",
        "description": "This boosts your win rewards by 5.5%! Permanent!"
    },
    "bulkchest": {
        "id": "S4",
        "name": "Bulk Chest Opener",
        "emoji": "📦",
        "price": 100000000,
        "boost": 0.0,  # Not a boost item
        "duration": -1,  # Permanent
        "short_description": "Open more chests!",
        "description":
        "Allows you to open up to 100 chests at once! Permanent!"
    },
    "bronze": {
        "id":
        "C1",
        "name":
        "Bronze Chest",
        "emoji":
        "🥉",
        "price":
        1000000,
        "boost":
        0.0,
        "duration":
        0,
        "short_description":
        "Low-Tier Loot. Chance for HUGE!",
        "description":
        "Low-tier chest with basic rewards. Small chance for huge pets!"
    },
    "silver": {
        "id":
        "C2",
        "name":
        "Silver Chest",
        "emoji":
        "🥈",
        "price":
        5000000,
        "boost":
        0.0,
        "duration":
        0,
        "short_description":
        "Medium Tier Loot. Chance for HUGES!",
        "description":
        "Medium-tier chest with better rewards. Good chance for huge pets!"
    },
    "diamond": {
        "id":
        "C3",
        "name":
        "Diamond Chest",
        "emoji":
        "💎",
        "price":
        25000000,
        "boost":
        0.0,
        "duration":
        0,
        "short_description":
        "High Tier Pets. Chance for TITANIC!",
        "description":
        "High-tier chest with amazing pets. Chance for titanic pets!"
    },
    "cards": {
        "id":
        "C4",
        "name":
        "Cards Chest",
        "emoji":
        "🎴",
        "price":
        1000000,
        "boost":
        0.0,
        "duration":
        0,
        "short_description":
        "Mixed Cards. Chance for TITANIC CARD!",
        "description":
        "Contains various trading cards with chance for rare titanic cards!"
    },
    "tickets": {
        "id":
        "C5",
        "name":
        "Tickets Chest",
        "emoji":
        "🎫",
        "price":
        10000000,
        "boost":
        0.0,
        "duration":
        0,
        "short_description":
        "Mixed Tickets, Chance for EXCLUSIVE tickets!",
        "description":
        "Contains various game tickets including exclusive raffle tickets!"
    },
    "titanic": {
        "id": "C6",
        "name": "Titanic Chest",
        "emoji": "🚢",
        "price": 10000000,
        "boost": 0.0,
        "duration": 0,
        "short_description": "Chance for TITANIC!",
        "description": "Very rare chance for titanic pets, mostly gives junk!"
    },
    "enchant": {
        "id": "C7",
        "name": "Enchant Chest",
        "emoji": "✨",
        "price": 1000000000,
        "boost": 0.0,
        "duration": 0,
        "short_description": "Chance for MEGA CHEST BREAKER!",
        "description": "Contains powerful enchantments and rare items!"
    },
    "mega": {
        "id":
        "C8",
        "name":
        "Mega Loot Chest",
        "emoji":
        "🎁",
        "price":
        25000000,
        "boost":
        0.0,
        "duration":
        0,
        "short_description":
        "Premium Mixed Rewards!",
        "description":
        "The ultimate chest with high-value mixed rewards and premium items!"
    }
}


def load_data():
    """Load user balances and bot statistics from JSON file"""
    global user_balances, bot_stats, player_stats, user_boosts, user_items, user_inventories
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            user_balances = data.get('balances', {})
            bot_stats = data.get('stats', {
                'total_given': 0,
                'total_in_system': 0,
                'last_giveaway': None
            })
            player_stats = data.get('player_stats', {})
            user_boosts = data.get('user_boosts', {})
            user_items = data.get('user_items', {})
            user_inventories = data.get('user_inventories', {})
    except FileNotFoundError:
        logger.info("Data file not found, starting with empty data")
        user_balances = {}
        bot_stats = {
            'total_given': 0,
            'total_in_system': 0,
            'last_giveaway': None
        }
        player_stats = {}
        user_boosts = {}
        user_items = {}
        user_inventories = {}


def save_data():
    """Save user balances and bot statistics to JSON file"""
    data = {
        'balances': user_balances,
        'stats': bot_stats,
        'player_stats': player_stats,
        'user_boosts': user_boosts,
        'user_items': user_items,
        'user_inventories': user_inventories
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_config():
    """Load bot configuration from JSON file"""
    global config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.info("Config file not found, creating default config")
        config = {
            'owner_id': None,  # Will be set automatically
            'giveaway_channel_id': None,
            'chest_log_channel_id': None,
            'blackjack_win_rate': 0.35,
            'coinflip_win_rate': 0.35,
            'mines_win_rate': 0.15,
            'raffle_win_chance': 0.000001,
            'raffle_ticket_cost': 1,
            'raffle_jackpot': 100000
        }
        save_config()


def save_config():
    """Save bot configuration to JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_user_balance(user_id):
    """Get user's balance, return 0 if user doesn't exist"""
    return user_balances.get(str(user_id), 0)


def format_tokens(amount):
    """Format token amount with custom emoji"""
    return f"{amount:,} <:rngcoin:1395655863510765668>"


def parse_bet_amount(bet_input, user_balance):
    """Parse bet amount from string input (supports k, m, b, q, all)"""
    if isinstance(bet_input, int):
        return bet_input

    bet_str = str(bet_input).lower().strip()

    # Handle "all" or "max"
    if bet_str in ['all', 'max']:
        return user_balance

    # Handle percentage of balance
    if bet_str.endswith('%'):
        try:
            percentage = float(bet_str[:-1])
            return int(user_balance * (percentage / 100))
        except ValueError:
            return None

    # Handle shorthand notation
    multipliers = {
        'k': 1_000,
        'm': 1_000_000,
        'b': 1_000_000_000,
        'q': 1_000_000_000_000,
        't': 1_000_000_000_000_000
    }

    # Check if it ends with a multiplier
    for suffix, multiplier in multipliers.items():
        if bet_str.endswith(suffix):
            try:
                number = float(bet_str[:-1])
                return int(number * multiplier)
            except ValueError:
                return None

    # Try to parse as regular number
    try:
        return int(float(bet_str))
    except ValueError:
        return None


async def send_dm_notification(user_id, message):
    """Send DM notification to user"""
    try:
        user = bot.get_user(user_id)
        if user:
            await user.send(message)
    except discord.Forbidden:
        pass  # User has DMs disabled
    except Exception as e:
        logger.error(f"Failed to send DM to {user_id}: {e}")


def get_player_stats(user_id):
    """Get player's game statistics"""
    user_id = str(user_id)
    if user_id not in player_stats:
        player_stats[user_id] = {
            'blackjack_played': 0,
            'blackjack_won': 0,
            'coinflip_played': 0,
            'coinflip_won': 0,
            'raffle_played': 0,
            'raffle_won': 0,
            'chest_played': 0,
            'chest_won': 0,
            'mines_played': 0,
            'mines_won': 0,
            'total_wagered': 0,
            'total_won': 0
        }
    else:
        # Ensure all keys exist for existing users (backward compatibility)
        if 'mines_played' not in player_stats[user_id]:
            player_stats[user_id]['mines_played'] = 0
        if 'mines_won' not in player_stats[user_id]:
            player_stats[user_id]['mines_won'] = 0
        if 'slots_played' not in player_stats[user_id]:
            player_stats[user_id]['slots_played'] = 0
        if 'slots_won' not in player_stats[user_id]:
            player_stats[user_id]['slots_won'] = 0
    return player_stats[user_id]


def update_player_stats(user_id, game_type, won, amount_wagered, amount_won=0):
    """Update player's game statistics"""
    stats = get_player_stats(user_id)
    stats[f'{game_type}_played'] += 1
    if won:
        stats[f'{game_type}_won'] += 1
    stats['total_wagered'] += amount_wagered
    stats['total_won'] += amount_won
    save_data()


def get_balance_rank(user_id):
    """Get user's balance rank in the server"""
    user_balance = get_user_balance(user_id)
    sorted_balances = sorted(user_balances.items(),
                             key=lambda x: x[1],
                             reverse=True)

    for rank, (uid, balance) in enumerate(sorted_balances, 1):
        if uid == str(user_id):
            return rank, len(sorted_balances)
    return len(sorted_balances), len(sorted_balances)


def get_user_boosts(user_id):
    """Get user's active boosts"""
    user_id = str(user_id)
    if user_id not in user_boosts:
        user_boosts[user_id] = {}

    # Clean expired boosts
    current_time = datetime.now().timestamp()
    expired_boosts = []

    for boost_type, boost_data in user_boosts[user_id].items():
        if boost_data.get('duration', -1) != -1:  # Not permanent
            if current_time > boost_data.get('expires_at', 0):
                expired_boosts.append(boost_type)

    for boost_type in expired_boosts:
        del user_boosts[user_id][boost_type]

    return user_boosts[user_id]


def get_user_items(user_id):
    """Get user's permanent items"""
    user_id = str(user_id)
    if user_id not in user_items:
        user_items[user_id] = {}
    return user_items[user_id]


def user_has_item(user_id, item_name):
    """Check if user has a specific item"""
    items = get_user_items(user_id)
    return item_name in items


def get_user_inventory(user_id):
    """Get user's inventory"""
    user_id = str(user_id)
    if user_id not in user_inventories:
        user_inventories[user_id] = {}
    return user_inventories[user_id]


def add_to_inventory(user_id, item_name):
    """Add an item to user's inventory"""
    user_id = str(user_id)
    inventory = get_user_inventory(user_id)

    # Generate unique ID for the item
    item_id = f"INV{len(inventory) + 1:04d}"
    while item_id in inventory:
        item_id = f"INV{len(inventory) + random.randint(1, 9999):04d}"

    inventory[item_id] = {
        'name': item_name,
        'obtained_at': datetime.now().timestamp()
    }
    save_data()
    return item_id


def remove_from_inventory(user_id, item_id):
    """Remove an item from user's inventory"""
    user_id = str(user_id)
    inventory = get_user_inventory(user_id)

    if item_id in inventory:
        removed_item = inventory.pop(item_id)
        save_data()
        return removed_item
    return None


def apply_boost_to_winnings(user_id, base_winnings):
    """Apply active boosts to winnings and return details"""
    boosts = get_user_boosts(user_id)
    if not boosts:
        return base_winnings, None

    # Find the highest boost (they don't stack)
    highest_boost = 0
    boost_name = ""

    for boost_type, boost_data in boosts.items():
        if boost_data['boost'] > highest_boost:
            highest_boost = boost_data['boost']
            boost_name = boost_data['name']

    if highest_boost > 0:
        boost_amount = int(base_winnings * highest_boost)
        total_winnings = base_winnings + boost_amount
        return total_winnings, {
            "boost_amount": boost_amount,
            "boost_name": boost_name,
            "original": base_winnings
        }

    return base_winnings, None


def format_time_remaining(seconds):
    """Format time remaining in a readable format"""
    if seconds <= 0:
        return "Expired"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def calculate_dynamic_win_rate(game_type, base_win_rate):
    """Calculate dynamic win rate to prevent house losses"""
    current_profit = calculate_profit()

    # If we're making good profit, use base rate
    if current_profit > 1000:  # 1000 tokens buffer
        return base_win_rate

    # If profit is getting low, reduce win rate to protect house
    if current_profit > 500:
        return base_win_rate * 0.8  # 20% reduction
    elif current_profit > 100:
        return base_win_rate * 0.6  # 40% reduction
    else:
        return base_win_rate * 0.4  # 60% reduction - house protection mode


def set_user_balance(user_id, amount):
    """Set user's balance"""
    user_balances[str(user_id)] = max(0, amount)
    save_data()


def calculate_profit():
    """Calculate current profit (money given - money in system)"""
    current_in_system = sum(user_balances.values())
    bot_stats['total_in_system'] = current_in_system
    return bot_stats['total_given'] - current_in_system


@bot.event
async def on_ready():
    """Bot startup event"""
    logger.info(f'{bot.user} has connected to Discord!')

    # Set owner ID if not set
    if config.get('owner_id') is None:
        app_info = await bot.application_info()
        config['owner_id'] = app_info.owner.id
        save_config()

    # Start daily giveaway task
    daily_giveaway.start()


@bot.command(name='balance', aliases=['bal'])
async def check_balance(ctx):
    """Check user's current balance and statistics"""
    user_id = ctx.author.id
    balance = get_user_balance(user_id)
    stats = get_player_stats(user_id)
    rank, total_players = get_balance_rank(user_id)

    # Calculate total games and win rates
    total_games = stats['blackjack_played'] + stats['coinflip_played'] + stats[
        'raffle_played'] + stats['chest_played'] + stats[
            'mines_played'] + stats.get('slots_played', 0)
    total_wins = stats['blackjack_won'] + stats['coinflip_won'] + stats[
        'raffle_won'] + stats['chest_won'] + stats['mines_won'] + stats.get(
            'slots_won', 0)

    embed = discord.Embed(
        title="💰 Your Casino Profile",
        description=
        f"**Balance:** {format_tokens(balance)}\n**Server Rank:** #{rank} of {total_players}",
        color=0x00ff00)

    # Game Statistics
    if total_games > 0:
        win_rate = (total_wins / total_games) * 100
        embed.add_field(
            name="📊 Overall Stats",
            value=
            f"**Games Played:** {total_games:,}\n**Games Won:** {total_wins:,}\n**Win Rate:** {win_rate:.1f}%",
            inline=True)

        # Blackjack Stats
        if stats['blackjack_played'] > 0:
            bj_win_rate = (stats['blackjack_won'] /
                           stats['blackjack_played']) * 100
            embed.add_field(
                name="🃏 Blackjack",
                value=
                f"**Played:** {stats['blackjack_played']:,}\n**Won:** {stats['blackjack_won']:,}\n**Win Rate:** {bj_win_rate:.1f}%",
                inline=True)

        # Coinflip Stats
        if stats['coinflip_played'] > 0:
            cf_win_rate = (stats['coinflip_won'] /
                           stats['coinflip_played']) * 100
            embed.add_field(
                name="🪙 Coinflip",
                value=
                f"**Played:** {stats['coinflip_played']:,}\n**Won:** {stats['coinflip_won']:,}\n**Win Rate:** {cf_win_rate:.1f}%",
                inline=True)

        # Chest Stats
        if stats['chest_played'] > 0:
            chest_win_rate = (stats['chest_won'] / stats['chest_played']) * 100
            embed.add_field(
                name="📦 Chests",
                value=
                f"**Opened:** {stats['chest_played']:,}\n**Profitable:** {stats['chest_won']:,}\n**Profit Rate:** {chest_win_rate:.1f}%",
                inline=True)

        # Mines Stats
        if stats['mines_played'] > 0:
            mines_win_rate = (stats['mines_won'] / stats['mines_played']) * 100
            embed.add_field(
                name="💣 Mines",
                value=
                f"**Played:** {stats['mines_played']:,}\n**Won:** {stats['mines_won']:,}\n**Win Rate:** {mines_win_rate:.1f}%",
                inline=True)

        # Slots Stats
        if stats.get('slots_played', 0) > 0:
            slots_win_rate = (stats.get('slots_won', 0) /
                              stats['slots_played']) * 100
            embed.add_field(
                name="🎰 Slots",
                value=
                f"**Played:** {stats['slots_played']:,}\n**Won:** {stats.get('slots_won', 0):,}\n**Win Rate:** {slots_win_rate:.1f}%",
                inline=True)

        # Financial Stats
        net_profit = stats['total_won'] - stats['total_wagered']
        embed.add_field(
            name="💸 Financial",
            value=
            f"**Total Wagered:** {format_tokens(stats['total_wagered'])}\n**Total Won:** {format_tokens(stats['total_won'])}\n**Net:** {format_tokens(net_profit)} {'📈' if net_profit >= 0 else '📉'}",
            inline=True)
    else:
        embed.add_field(
            name="🎮 Ready to Play?",
            value=
            "Start playing to see your statistics here!\nTry `!blackjack`, `!coinflip`, `!chest`, or `!raffle`",
            inline=False)

    # Show active boosts
    boosts = get_user_boosts(user_id)
    if boosts:
        boost_text = ""
        current_time = datetime.now().timestamp()

        for boost_type, boost_data in boosts.items():
            boost_emoji = boost_data.get('emoji', '🚀')
            boost_name = boost_data['name']
            boost_percent = boost_data['boost'] * 100

            if boost_data.get('duration', -1) == -1:
                time_left = "Permanent"
            else:
                expires_at = boost_data.get('expires_at', current_time)
                time_remaining = expires_at - current_time
                time_left = format_time_remaining(time_remaining)

            boost_text += f"{boost_emoji} **{boost_name}** (+{boost_percent:.1f}%) - {time_left}\n"

        embed.add_field(name="🚀 Active Boosts", value=boost_text, inline=False)

    embed.set_footer(text="💎 Your casino journey awaits! 💎")
    await ctx.send(embed=embed)


@bot.command(name='give')
async def give_money(ctx, user: discord.Member, amount: int):
    """Give money to a user (owner only)"""
    if ctx.author.id != config['owner_id']:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    current_balance = get_user_balance(user.id)
    new_balance = current_balance + amount
    set_user_balance(user.id, new_balance)

    # Update statistics
    bot_stats['total_given'] += amount
    save_data()

    # Send DM notification to user
    await send_dm_notification(
        user.id,
        f"💰 You received {format_tokens(amount)} from the bot owner!\nYour new balance: {format_tokens(new_balance)}"
    )

    embed = discord.Embed(
        title="💰 Money Given",
        description=
        f"Gave **{format_tokens(amount)}** to {user.mention}!\nTheir new balance: **{format_tokens(new_balance)}**",
        color=0x00ff00)
    await ctx.send(embed=embed)


# Blackjack game data storage
active_games = {}


class BlackjackGame:

    def __init__(self, user_id, bet, predetermined_result):
        self.user_id = user_id
        self.bet = bet
        self.predetermined_result = predetermined_result
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.dealer_revealed = False

    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = [
            'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'
        ]
        deck = []
        for suit in suits:
            for rank in ranks:
                deck.append(f"{rank}{suit}")
        random.shuffle(deck)
        return deck

    def deal_card(self):
        return self.deck.pop()

    def card_value(self, card):
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11
        else:
            return int(rank)

    def hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            card_val = self.card_value(card)
            if card_val == 11:
                aces += 1
            value += card_val

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def format_hand(self, hand, hide_first=False):
        if hide_first and len(hand) > 1:
            return f"🂠 {' '.join(hand[1:])}"
        return ' '.join(hand)

    def start_game(self):
        # Deal initial cards
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]

        # Check for natural blackjack
        if self.hand_value(self.player_hand) == 21:
            self.game_over = True
            self.dealer_revealed = True
            return self.create_embed()

        return self.create_embed()

    def hit(self):
        if self.game_over:
            return None

        self.player_hand.append(self.deal_card())
        if self.hand_value(self.player_hand) > 21:
            self.game_over = True
            self.dealer_revealed = True

        return self.create_embed()

    def stand(self):
        if self.game_over:
            return None

        self.game_over = True
        self.dealer_revealed = True

        # Dealer plays according to predetermined result
        dealer_value = self.hand_value(self.dealer_hand)
        player_value = self.hand_value(self.player_hand)

        if self.predetermined_result:
            # Player should win - dealer plays to lose
            while dealer_value < 17 and dealer_value < player_value:
                self.dealer_hand.append(self.deal_card())
                dealer_value = self.hand_value(self.dealer_hand)
                if dealer_value > 21:
                    break
        else:
            # Player should lose - dealer plays to win
            while dealer_value < 17:
                self.dealer_hand.append(self.deal_card())
                dealer_value = self.hand_value(self.dealer_hand)

        return self.create_embed()

    def create_embed(self):
        player_value = self.hand_value(self.player_hand)
        dealer_value = self.hand_value(self.dealer_hand)

        embed = discord.Embed(title="🃏 Blackjack", color=0x0066cc)

        # Player hand
        embed.add_field(
            name="🙋 Your Hand",
            value=
            f"{self.format_hand(self.player_hand)} (Value: {player_value})",
            inline=False)

        # Dealer hand
        if self.dealer_revealed:
            embed.add_field(
                name="🏪 Dealer's Hand",
                value=
                f"{self.format_hand(self.dealer_hand)} (Value: {dealer_value})",
                inline=False)
        else:
            embed.add_field(
                name="🏪 Dealer's Hand",
                value=
                f"{self.format_hand(self.dealer_hand, hide_first=True)} (Value: ?)",
                inline=False)

        # Game status
        if self.game_over:
            result = self.determine_winner()
            embed.add_field(name="📊 Result", value=result, inline=False)
        else:
            embed.add_field(
                name="🎯 Actions",
                value="Use the buttons below to **Hit** or **Stand**",
                inline=False)

        embed.set_footer(text=f"Bet: {self.bet:,} coins")
        return embed

    def determine_winner(self):
        player_value = self.hand_value(self.player_hand)
        dealer_value = self.hand_value(self.dealer_hand)

        if player_value > 21:
            return "🔥 **BUST!** You went over 21!"
        elif dealer_value > 21:
            return "🎉 **DEALER BUST!** You win!"
        elif player_value == 21 and len(self.player_hand) == 2:
            return "🎊 **BLACKJACK!** You win!"
        elif dealer_value == 21 and len(self.dealer_hand) == 2:
            return "😔 **Dealer Blackjack!** You lose!"
        elif player_value > dealer_value:
            return "🎉 **YOU WIN!** Your hand beats the dealer!"
        elif player_value < dealer_value:
            return "😔 **YOU LOSE!** Dealer's hand beats yours!"
        else:
            return "🤝 **PUSH!** It's a tie!"


class BlackjackView(discord.ui.View):

    def __init__(self, game):
        super().__init__(timeout=300)
        self.game = game

    @discord.ui.button(label='Hit',
                       style=discord.ButtonStyle.primary,
                       emoji='🃏')
    async def hit_button(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ This isn't your game!",
                                                    ephemeral=True)
            return

        embed = self.game.hit()
        if embed:
            if self.game.game_over:
                await self.end_game(interaction)
            else:
                await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Stand',
                       style=discord.ButtonStyle.secondary,
                       emoji='✋')
    async def stand_button(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ This isn't your game!",
                                                    ephemeral=True)
            return

        embed = self.game.stand()
        if embed:
            await self.end_game(interaction)

    async def end_game(self, interaction):
        # Remove from active games
        if self.game.user_id in active_games:
            del active_games[self.game.user_id]

        # Calculate winnings
        player_value = self.game.hand_value(self.game.player_hand)
        dealer_value = self.game.hand_value(self.game.dealer_hand)
        current_balance = get_user_balance(self.game.user_id)

        # Determine actual result
        boost_info = None
        if player_value > 21:
            # Player busted
            new_balance = current_balance - self.game.bet
            result_color = 0xff0000
            amount_won = 0
        elif dealer_value > 21:
            # Dealer busted
            base_winnings = self.game.bet
            total_winnings, boost_info = apply_boost_to_winnings(
                self.game.user_id, base_winnings)
            new_balance = current_balance + total_winnings
            result_color = 0x00ff00
            amount_won = total_winnings
        elif player_value == 21 and len(self.game.player_hand) == 2:
            # Player blackjack
            base_winnings = int(self.game.bet * 1.5)
            total_winnings, boost_info = apply_boost_to_winnings(
                self.game.user_id, base_winnings)
            new_balance = current_balance + total_winnings
            result_color = 0xffd700
            amount_won = total_winnings
        elif dealer_value == 21 and len(self.game.dealer_hand) == 2:
            # Dealer blackjack
            new_balance = current_balance - self.game.bet
            result_color = 0xff0000
            amount_won = 0
        elif player_value > dealer_value:
            # Player wins
            base_winnings = self.game.bet
            total_winnings, boost_info = apply_boost_to_winnings(
                self.game.user_id, base_winnings)
            new_balance = current_balance + total_winnings
            result_color = 0x00ff00
            amount_won = total_winnings
        elif player_value < dealer_value:
            # Dealer wins
            new_balance = current_balance - self.game.bet
            result_color = 0xff0000
            amount_won = 0
        else:
            # Push
            new_balance = current_balance
            result_color = 0xffff00
            amount_won = 0

        set_user_balance(self.game.user_id, new_balance)

        # Update player statistics
        won = amount_won > 0
        update_player_stats(self.game.user_id, 'blackjack', won, self.game.bet,
                            amount_won)

        # Create final embed
        embed = self.game.create_embed()
        embed.color = result_color

        balance_text = f"New balance: **{format_tokens(new_balance)}**"
        if boost_info:
            balance_text = f"Base winnings: **{format_tokens(boost_info['original'])}**\n{boost_info['boost_name']}: +**{format_tokens(boost_info['boost_amount'])}**\nTotal winnings: **{format_tokens(boost_info['original'] + boost_info['boost_amount'])}**\nNew balance: **{format_tokens(new_balance)}**"

        embed.add_field(name="💰 Balance Update",
                        value=balance_text,
                        inline=False)

        # Check for bankruptcy and send DM
        if new_balance == 0:
            await send_dm_notification(
                self.game.user_id,
                "💔 You've gone bankrupt! Better luck next time.")

        # Disable all buttons
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


@bot.command(name='blackjack', aliases=['bj'])
async def blackjack(ctx, bet):
    """Play interactive blackjack"""
    try:
        user_id = ctx.author.id
        current_balance = get_user_balance(user_id)

        # Parse bet amount
        parsed_bet = parse_bet_amount(bet, current_balance)
        if parsed_bet is None:
            await ctx.send(
                "❌ Invalid bet amount! Use numbers, 'all', or shorthand like 100k, 50m, 2.5b"
            )
            return

        bet = parsed_bet

        if bet <= 0:
            await ctx.send("❌ Bet must be positive!")
            return

        if bet > current_balance:
            await ctx.send("❌ You don't have enough tokens!")
            return

        # Check if user already has an active game
        if user_id in active_games:
            await ctx.send(
                "❌ You already have an active blackjack game! Finish it first."
            )
            return

        # Determine if player should win based on dynamic odds
        base_win_rate = config['blackjack_win_rate']
        dynamic_win_rate = calculate_dynamic_win_rate('blackjack',
                                                      base_win_rate)
        predetermined_result = random.random() < dynamic_win_rate

        # Create and start game
        game = BlackjackGame(user_id, bet, predetermined_result)
        active_games[user_id] = game

        embed = game.start_game()
        view = BlackjackView(game)

        if game.game_over:
            # Natural blackjack - end immediately
            await view.end_game_immediate(ctx, embed)
        else:
            await ctx.send(embed=embed, view=view)

    except Exception as e:
        logger.error(f"Error in blackjack command: {e}")
        await ctx.send(f"❌ An error occurred: {str(e)}")


# Add method to BlackjackView for immediate game end
def end_game_immediate(self, ctx, embed):
    if self.game.user_id in active_games:
        del active_games[self.game.user_id]

    current_balance = get_user_balance(self.game.user_id)
    player_value = self.game.hand_value(self.game.player_hand)

    if player_value == 21:
        # Natural blackjack
        new_balance = current_balance + int(self.game.bet * 1.5)
        embed.color = 0xffd700

    set_user_balance(self.game.user_id, new_balance)
    embed.add_field(name="💰 Balance Update",
                    value=f"New balance: **{format_tokens(new_balance)}**",
                    inline=False)

    return ctx.send(embed=embed)


BlackjackView.end_game_immediate = end_game_immediate


@bot.command(name='coinflip', aliases=['cf'])
async def coinflip(ctx, bet):
    """Play coin flip"""
    user_id = ctx.author.id
    current_balance = get_user_balance(user_id)

    # Parse bet amount
    parsed_bet = parse_bet_amount(bet, current_balance)
    if parsed_bet is None:
        await ctx.send(
            "❌ Invalid bet amount! Use numbers, 'all', or shorthand like 100k, 50m, 2.5b"
        )
        return

    bet = parsed_bet

    if bet <= 0:
        await ctx.send("❌ Bet must be positive!")
        return

    if bet > current_balance:
        await ctx.send("❌ You don't have enough tokens!")
        return

    # Simulate coin flip with dynamic win rate
    base_win_rate = config['coinflip_win_rate']
    dynamic_win_rate = calculate_dynamic_win_rate('coinflip', base_win_rate)
    won = random.random() < dynamic_win_rate
    result = "Heads" if won else "Tails"

    if won:
        base_winnings = bet
        total_winnings, boost_info = apply_boost_to_winnings(
            user_id, base_winnings)
        new_balance = current_balance + total_winnings
        set_user_balance(user_id, new_balance)

        # Update player statistics
        update_player_stats(user_id, 'coinflip', True, bet, total_winnings)

        description = f"You won **{format_tokens(base_winnings)}**!"
        if boost_info:
            description += f"\n{boost_info['boost_name']}: +{format_tokens(boost_info['boost_amount'])}"
            description += f"\n**Total:** {format_tokens(total_winnings)}"
        description += f"\nNew balance: **{format_tokens(new_balance)}**"

        embed = discord.Embed(title=f"🪙 Coin Flip - {result}!",
                              description=description,
                              color=0x00ff00)
    else:
        new_balance = current_balance - bet
        set_user_balance(user_id, new_balance)

        # Update player statistics
        update_player_stats(user_id, 'coinflip', False, bet, 0)

        embed = discord.Embed(
            title=f"🪙 Coin Flip - {result}!",
            description=
            f"You lost **{format_tokens(bet)}**!\nNew balance: **{format_tokens(new_balance)}**",
            color=0xff0000)

        # Check for bankruptcy and send DM
        if new_balance == 0:
            await send_dm_notification(
                user_id, "💔 You've gone bankrupt! Better luck next time.")

    await ctx.send(embed=embed)


@bot.command(name='raffle')
async def raffle(ctx, amount: int = 1):
    """Buy raffle tickets for a chance to win the jackpot"""
    user_id = ctx.author.id
    current_balance = get_user_balance(user_id)
    ticket_cost = config['raffle_ticket_cost']
    jackpot = config['raffle_jackpot']
    total_cost = ticket_cost * amount

    if amount <= 0:
        await ctx.send("❌ You need to buy at least 1 raffle ticket!")
        return

    if amount > 1000:
        await ctx.send("❌ You can only buy up to 1,000 raffle tickets at once!"
                       )
        return

    if current_balance < total_cost:
        await ctx.send(
            f"❌ You need **{format_tokens(total_cost)}** to buy {amount} raffle ticket{'s' if amount > 1 else ''}!"
        )
        return

    # Check if jackpot would cause system loss
    profit = calculate_profit()
    if jackpot > profit:
        # Make it impossible to win when insufficient funds
        win_chance = 0.0
    else:
        win_chance = config['raffle_win_chance']

    # Simulate multiple raffles
    total_winnings = 0
    wins = 0

    for i in range(amount):
        if random.random() < win_chance:
            total_winnings += jackpot
            wins += 1

    # Update balance
    new_balance = current_balance - total_cost + total_winnings
    set_user_balance(user_id, new_balance)

    # Update player statistics
    won = total_winnings > 0
    update_player_stats(user_id, 'raffle', won, total_cost, total_winnings)

    if wins > 0:
        embed = discord.Embed(
            title=
            f"🎰 RAFFLE JACKPOT WINNER! ({wins} win{'s' if wins > 1 else ''})",
            description=
            f"🎉 **CONGRATULATIONS!** 🎉\nYou won {wins} raffle jackpot{'s' if wins > 1 else ''} totaling **{format_tokens(total_winnings)}**!\n\n**Tickets bought:** {amount}\n**Winning tickets:** {wins}\n**New balance:** {format_tokens(new_balance)}",
            color=0xffd700)

        # Announce in all channels if possible
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    try:
                        if wins == 1:
                            await channel.send(
                                f"🎰 **RAFFLE JACKPOT WINNER:** {ctx.author.mention} won **{format_tokens(jackpot)}**! 🎰"
                            )
                        else:
                            await channel.send(
                                f"🎰 **MULTIPLE RAFFLE WINS:** {ctx.author.mention} won {wins} jackpots totaling **{format_tokens(total_winnings)}**! 🎰"
                            )
                        break
                    except:
                        continue
    else:
        new_balance = current_balance - total_cost
        set_user_balance(user_id, new_balance)

        embed = discord.Embed(
            title=f"🎰 Raffle Ticket{'s' if amount > 1 else ''} Purchased",
            description=
            f"You bought {amount} raffle ticket{'s' if amount > 1 else ''} for **{format_tokens(total_cost)}**!\nBetter luck next time!\nNew balance: **{format_tokens(new_balance)}**",
            color=0xff8800)

        # Check for bankruptcy and send DM
        if new_balance == 0:
            await send_dm_notification(
                user_id, "💔 You've gone bankrupt! Better luck next time.")

    await ctx.send(embed=embed)


# Interactive Mines Game
active_mines_games = {}


class MinesGame:

    def __init__(self, user_id, bet, num_mines):
        self.user_id = user_id
        self.bet = bet
        self.num_mines = num_mines
        self.grid_size = 5
        self.total_cells = self.grid_size * self.grid_size
        self.revealed_cells = set()
        self.mine_positions = set()
        self.game_over = False
        self.won = False
        self.hit_mine_position = None  # Track which mine was hit

        # Place mines randomly but rigged based on config
        self.place_mines()

    def place_mines(self):
        """Place mines randomly on the grid - completely fair"""
        # Simply place mines randomly across the grid
        available_positions = list(range(self.total_cells))
        self.mine_positions = set(
            random.sample(available_positions, self.num_mines))

    def click_cell(self, position):
        """Click a cell and return the result"""
        if self.game_over or position in self.revealed_cells:
            return False

        self.revealed_cells.add(position)

        if position in self.mine_positions:
            # Hit a mine - game over
            self.game_over = True
            self.won = False
            self.hit_mine_position = position
            return True

        # Check if won (all non-mine cells revealed)
        safe_cells = self.total_cells - len(self.mine_positions)
        if len(self.revealed_cells) >= safe_cells:
            self.game_over = True
            self.won = True
            return True

        return True

    def get_multiplier(self):
        """Calculate multiplier based on mines and revealed cells"""
        base_multiplier = 0.80  # Start at 0.80x
        cells_revealed = len(self.revealed_cells)

        # Each safe cell revealed increases multiplier by (mines * 0.04)
        multiplier_per_cell = self.num_mines * 0.04
        return base_multiplier + (cells_revealed * multiplier_per_cell)

    def create_embed(self):
        """Create the game embed"""
        embed = discord.Embed(
            title="💣 Interactive Mines",
            description=
            f"**Bet:** {format_tokens(self.bet)}\n**Mines:** {self.num_mines}\n**Current Multiplier:** {self.get_multiplier():.2f}x",
            color=0x0066cc)

        if self.game_over:
            if self.won:
                winnings = int(self.bet * self.get_multiplier())
                embed.color = 0x00ff00
                embed.add_field(
                    name="🎉 SUCCESS!",
                    value=
                    f"You avoided all mines!\n**Winnings:** {format_tokens(winnings)}",
                    inline=False)
            else:
                embed.color = 0xff0000
                embed.add_field(
                    name="💥 BOOM!",
                    value=
                    f"You hit a mine!\n**Lost:** {format_tokens(self.bet)}",
                    inline=False)
        else:
            cells_revealed = len(self.revealed_cells)
            safe_cells = self.total_cells - self.num_mines
            embed.add_field(
                name="📊 Progress",
                value=
                f"**Cells Revealed:** {cells_revealed}/{safe_cells}\n**Risk Level:** {'🔥 EXTREME' if self.num_mines >= 15 else '⚠️ HIGH' if self.num_mines >= 10 else '⚡ MEDIUM' if self.num_mines >= 5 else '✅ LOW'}",
                inline=False)

        return embed


class MinesView(discord.ui.View):

    def __init__(self, game):
        super().__init__(timeout=300)
        self.game = game
        self.create_buttons()

    def create_buttons(self):
        """Create the 5x5 grid of buttons"""
        self.clear_items()

        # Create all 25 grid buttons
        for i in range(self.game.total_cells):
            row = i // self.game.grid_size

            if i in self.game.revealed_cells:
                if i in self.game.mine_positions:
                    # Mine revealed - show if it was the hit mine or just revealed
                    if i == self.game.hit_mine_position:
                        button = discord.ui.Button(
                            label="💥",
                            style=discord.ButtonStyle.danger,
                            row=row,
                            disabled=True)
                    else:
                        button = discord.ui.Button(
                            label="💣",
                            style=discord.ButtonStyle.danger,
                            row=row,
                            disabled=True)
                else:
                    # Safe cell revealed - can be clicked to cash out if game is ongoing
                    if self.game.game_over:
                        button = discord.ui.Button(
                            label="✅",
                            style=discord.ButtonStyle.success,
                            row=row,
                            disabled=True)
                    else:
                        button = discord.ui.Button(
                            label="💰",
                            style=discord.ButtonStyle.primary,
                            row=row,
                            disabled=False)
            else:
                # Unrevealed cell - use a proper label
                button = discord.ui.Button(label="❓",
                                           style=discord.ButtonStyle.secondary,
                                           row=row,
                                           disabled=self.game.game_over)

            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, position):
        """Create a callback function for a specific button"""

        async def button_callback(interaction):
            if interaction.user.id != self.game.user_id:
                await interaction.response.send_message(
                    "❌ This isn't your game!", ephemeral=True)
                return

            # Check if this is a revealed safe cell (cash out)
            if position in self.game.revealed_cells and position not in self.game.mine_positions and not self.game.game_over:
                # Cash out
                self.game.game_over = True
                self.game.won = True

                embed = self.game.create_embed()
                embed.title = "💰 Cashed Out!"

                await self.end_game(interaction, embed)
            else:
                # Click the cell normally
                self.game.click_cell(position)

                # Update the view
                self.create_buttons()
                embed = self.game.create_embed()

                if self.game.game_over:
                    await self.end_game(interaction, embed)
                else:
                    await interaction.response.edit_message(embed=embed,
                                                            view=self)

        return button_callback

    async def end_game(self, interaction, embed):
        """End the game and update balances"""
        # Remove from active games
        if self.game.user_id in active_mines_games:
            del active_mines_games[self.game.user_id]

        current_balance = get_user_balance(self.game.user_id)

        if self.game.won:
            base_winnings = int(self.game.bet * self.game.get_multiplier())
            total_winnings, boost_info = apply_boost_to_winnings(
                self.game.user_id, base_winnings)
            new_balance = current_balance - self.game.bet + total_winnings
            net_gain = total_winnings - self.game.bet

            balance_text = f"**Net Gain:** +{format_tokens(net_gain)}\n**New Balance:** {format_tokens(new_balance)}"
            if boost_info:
                balance_text = f"**Base winnings:** {format_tokens(boost_info['original'])}\n**{boost_info['boost_name']}:** +{format_tokens(boost_info['boost_amount'])}\n**Total winnings:** {format_tokens(total_winnings)}\n**Net Gain:** +{format_tokens(net_gain)}\n**New Balance:** {format_tokens(new_balance)}"

            embed.add_field(name="💰 Balance Update",
                            value=balance_text,
                            inline=False)

            # Update player statistics
            update_player_stats(self.game.user_id, 'mines', True,
                                self.game.bet, total_winnings)
        else:
            new_balance = current_balance - self.game.bet
            embed.add_field(
                name="💰 Balance Update",
                value=
                f"**Loss:** -{format_tokens(self.game.bet)}\n**New Balance:** {format_tokens(new_balance)}",
                inline=False)

            # Update player statistics
            update_player_stats(self.game.user_id, 'mines', False,
                                self.game.bet, 0)

            # Check for bankruptcy and send DM
            if new_balance == 0:
                await send_dm_notification(
                    self.game.user_id,
                    "💔 You've gone bankrupt! Better luck next time.")

        set_user_balance(self.game.user_id, new_balance)

        # Show all mines in final state
        if not self.game.won:
            for mine_pos in self.game.mine_positions:
                if mine_pos not in self.game.revealed_cells:
                    self.game.revealed_cells.add(mine_pos)

        self.create_buttons()
        await interaction.response.edit_message(embed=embed, view=self)


@bot.command(name='mines')
async def mines(ctx, bet, num_mines: int = 5):
    """Play interactive mines - click buttons to reveal cells and avoid mines!"""
    user_id = ctx.author.id
    current_balance = get_user_balance(user_id)

    # Parse bet amount
    parsed_bet = parse_bet_amount(bet, current_balance)
    if parsed_bet is None:
        await ctx.send(
            "❌ Invalid bet amount! Use numbers, 'all', or shorthand like 100k, 50m, 2.5b"
        )
        return

    bet = parsed_bet

    if bet <= 0:
        await ctx.send("❌ Bet must be positive!")
        return

    if bet > current_balance:
        await ctx.send("❌ You don't have enough tokens!")
        return

    if num_mines < 1 or num_mines > 20:
        await ctx.send("❌ Number of mines must be between 1 and 20!")
        return

    # Check if user already has an active game
    if user_id in active_mines_games:
        await ctx.send(
            "❌ You already have an active mines game! Finish it first.")
        return

    # Create game
    game = MinesGame(user_id, bet, num_mines)
    active_mines_games[user_id] = game

    # Create view and send
    view = MinesView(game)
    embed = game.create_embed()

    embed.add_field(
        name="🎯 How to Play",
        value=
        "Click the ❓ buttons to reveal cells. Avoid the mines! You can cash out anytime after revealing at least one cell.",
        inline=False)

    await ctx.send(embed=embed, view=view)


# Chest system configuration
CHEST_TYPES = {
    "bronze": {
        "name":
        "Bronze Chest",
        "emoji":
        "🥉",
        "cost":
        1000000,
        "rewards": [(0.40, ("money", 600000)), (0.35, ("money", 700000)),
                    (0.217, ("item", "Rainbow Mini Chest")),
                    (0.03, ("item", "Random Huge")),
                    (0.003, ("money", 30000000))]
    },
    "silver": {
        "name":
        "Silver Chest",
        "emoji":
        "🥈",
        "cost":
        5000000,
        "rewards": [(0.40, ("money", 3500000)), (0.35, ("money", 4000000)),
                    (0.217, ("money", 5000000)),
                    (0.03, ("item", "x2 Random Huges")),
                    (0.003, ("item", "x5 Random Huges"))]
    },
    "diamond": {
        "name":
        "Diamond Chest",
        "emoji":
        "💎",
        "cost":
        25000000,
        "rewards": [(0.85, ("item", "Random Huge")),
                    (0.13, ("item", "x4 Random Huge")),
                    (0.015, ("item", "x6 Random Huge")),
                    (0.004, ("item", "x1 High Tier Huge")),
                    (0.001, ("item", "Titanic!"))]
    },
    "cards": {
        "name":
        "Cards Chest",
        "emoji":
        "🎴",
        "cost":
        1000000,
        "rewards": [(0.40, ("item", "Trash Card")),
                    (0.35, ("item", "Rainbow Trash Card")),
                    (0.217, ("item", "Exclusive Card")),
                    (0.03, ("item", "Huge Exclusive Card")),
                    (0.003, ("item", "Titanic Card"))]
    },
    "tickets": {
        "name":
        "Tickets Chest",
        "emoji":
        "🎫",
        "cost":
        10000000,
        "rewards": [(0.20, ("item", "x100 Millionaire Raffle Ticket")),
                    (0.20, ("item", "x10 Booth Slot Voucher")),
                    (0.20, ("item", "x10 Daycare Slot Voucher")),
                    (0.20, ("item", "x5 Random Spinny Wheel Tickets")),
                    (0.15, ("item", "x10 Fantasy Spinny Wheel Tickets")),
                    (0.05, ("item", "x5 Exclusive Raffle Tickets"))]
    },
    "titanic": {
        "name":
        "Titanic Chest",
        "emoji":
        "🚢",
        "cost":
        10000000,
        "rewards": [(0.99999, ("item", "Old Boot")),
                    (0.00001, ("item", "Titanic"))]
    },
    "enchant": {
        "name":
        "Enchant Chest",
        "emoji":
        "✨",
        "cost":
        1000000000,
        "rewards": [(0.50, ("item", "Party Time")),
                    (0.35, ("item", "Nightmare Orb")),
                    (0.13, ("item", "Boss Lucky Block")),
                    (0.015, ("item", "Breakable Mayhem")),
                    (0.0039, ("item", "Diamond Orb")),
                    (0.001, ("item", "Diamond Gift Bag Hunter")),
                    (0.0001, ("item", "Mega Chest Breaker"))]
    },
    "mega": {
        "name":
        "Mega Loot Chest",
        "emoji":
        "🎁",
        "cost":
        25000000,
        "rewards": [(0.00288, ("item", "Clan Voucher")),
                    (0.0048, ("item", "Daycare Voucher")),
                    (0.0183, ("item", "Diamond Fishing Rod")),
                    (0.0207, ("item", "x10 Rainbow Mini Chest")),
                    (0.0275, ("item", "x25 Nightmare Fuel")),
                    (0.0294, ("item", "x5 Mastery Potion")),
                    (0.0298, ("item", "Glitched Drive")),
                    (0.0329, ("item", "Diamond Shovel")),
                    (0.034, ("item", "x20 Ultimate XP Potion")),
                    (0.034, ("item", "x100 Mini Chest")),
                    (0.0528, ("item", "x25 Ultra Pet Cube")),
                    (0.0534, ("item", "x50 Titanic XP Potion")),
                    (0.0544, ("item", "x100 Bucket 'o Magic")),
                    (0.0633, ("item", "x50 Charm Chisels")),
                    (0.0707, ("item", "x25 Exotic Treasure Flag")),
                    (0.072, ("item", "Mega Charm Chest")),
                    (0.0724, ("item", "Mega Ultimate Chest")),
                    (0.085, ("item", "x50 Magic Shard")),
                    (0.100, ("item", "Mega Potions Chest")),
                    (0.141, ("item", "Mega Enchant Chest"))]
    }
}


class ChestPaginationView(discord.ui.View):

    def __init__(self, chest_types, page=0):
        super().__init__(timeout=300)
        self.chest_types = chest_types
        self.page = page
        self.items_per_page = 3
        self.max_pages = (len(chest_types) - 1) // self.items_per_page + 1

        # Update button states
        self.previous_button.disabled = page == 0
        self.next_button.disabled = page >= self.max_pages - 1

    def get_chest_embed(self):
        """Create embed for current page"""
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.chest_types))

        embed = discord.Embed(
            title="📦 Available Chests",
            description=
            f"Choose from our selection of treasure chests! (Page {self.page + 1}/{self.max_pages})",
            color=0x9932cc)

        chest_items = list(self.chest_types.items())
        for i in range(start_idx, end_idx):
            chest_id, chest_data = chest_items[i]
            rewards_text = ""

            if chest_data["rewards"] == "random_chest":
                rewards_text = "Opens a random chest from the other available chests!"
            else:
                for prob, (reward_type, reward_value) in chest_data["rewards"]:
                    if reward_type == "money":
                        rewards_text += f"**{prob*100:.3f}%** - {format_tokens(reward_value)}\n"
                    else:
                        rewards_text += f"**{prob*100:.4f}%** - {reward_value}\n"

            embed.add_field(
                name=
                f"{chest_data['emoji']} {chest_data['name']} - {format_tokens(chest_data['cost'])}",
                value=rewards_text,
                inline=False)

        embed.add_field(
            name="💡 How to Use",
            value=
            "Use `!chest <chest_name> <amount>` to open chests!\nExample: `!chest bronze 5` or `!chest enchant 1`\nMax 10 chests at once (100 with Bulk Opener).",
            inline=False)

        return embed

    @discord.ui.button(label='◀️ Previous',
                       style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction,
                              button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self.previous_button.disabled = self.page == 0
            self.next_button.disabled = False

            embed = self.get_chest_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='▶️ Next', style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self.page < self.max_pages - 1:
            self.page += 1
            self.next_button.disabled = self.page >= self.max_pages - 1
            self.previous_button.disabled = False

            embed = self.get_chest_embed()
            await interaction.response.edit_message(embed=embed, view=self)


async def send_chest_log(user, items_won):
    """Send chest win message to configured log channel"""
    if not config.get('chest_log_channel_id') or not items_won:
        return

    try:
        channel = bot.get_channel(config['chest_log_channel_id'])
        if channel:
            # Consolidate similar items (but not identical)
            item_counts = {}
            for item in items_won:
                # Handle special consolidation for Random Huge items
                if "Random Huge" in item and "High Tier" not in item:
                    consolidated_item = "Huge"
                    item_counts[consolidated_item] = item_counts.get(
                        consolidated_item, 0) + 1
                else:
                    # For all other items, just count them normally since multipliers are already handled
                    item_counts[item] = item_counts.get(item, 0) + 1

            # Send consolidated message
            messages = []
            for item, count in item_counts.items():
                if count == 1:
                    messages.append(f"**{item}**")
                else:
                    # Pluralize common items
                    if item.lower().endswith("time"):
                        plural_item = f"{item} Books"
                    elif item.lower().endswith("orb"):
                        plural_item = f"{item}s"
                    elif item.lower().endswith("block"):
                        plural_item = f"{item}s"
                    elif item.lower().endswith("mayhem"):
                        plural_item = f"{item} Items"
                    elif item.lower().endswith("hunter"):
                        plural_item = f"{item} Items"
                    elif item.lower().endswith("breaker"):
                        plural_item = f"{item} Items"
                    elif item.lower() == "huge":
                        plural_item = "Huges"
                    else:
                        plural_item = f"{item}s"

                    messages.append(f"**{count} {plural_item}**")

            if messages:
                message = f"{user.mention} won {', '.join(messages)}!"
                await channel.send(message)
    except Exception as e:
        logger.error(f"Failed to send chest log: {e}")


def open_single_chest(chest_type):
    """Open a single chest and return the reward"""
    if chest_type not in CHEST_TYPES:
        return None

    chest_data = CHEST_TYPES[chest_type]

    # Normal chest opening
    rand = random.random()
    cumulative = 0

    for reward_data in chest_data["rewards"]:
        if len(reward_data) == 2:
            chance, reward = reward_data
        else:
            continue  # Skip malformed reward data

        cumulative += chance
        if rand < cumulative:
            # Check if the reward is a multiplied item
            if len(reward) == 2 and reward[0] == "item":
                item_name = reward[1]
                # Handle all multiplied rewards (x2, x4, x5, x6, x10, x100, etc.)
                if item_name.startswith("x") and " " in item_name:
                    try:
                        # Extract multiplier from items like "x4 Random Huge", "x2 Random Huges", "x100 Millionaire Raffle Ticket"
                        parts = item_name.split(" ",
                                                1)  # Split only on first space
                        if len(parts) >= 2 and parts[0].startswith("x"):
                            multiplier = int(
                                parts[0][1:])  # Extract number after 'x'
                            base_item = parts[
                                1]  # Everything after the multiplier
                            # Return multiple items
                            return ("multiple_items",
                                    [("item", base_item)] * multiplier)
                    except (ValueError, IndexError):
                        # If parsing fails, return original reward
                        pass
            return reward

    # Fallback to last reward if something goes wrong
    last_reward = chest_data["rewards"][-1]
    if len(last_reward) == 2:
        return last_reward[1]
    else:
        return ("item", "Error Reward")


@bot.command(name='stats')
async def bot_stats_command(ctx):
    """Show bot statistics (owner only)"""
    if ctx.author.id != config['owner_id']:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    profit = calculate_profit()
    total_users = len(user_balances)

    embed = discord.Embed(title="📊 Bot Statistics", color=0x0099ff)
    embed.add_field(name="Total Given",
                    value=f"{format_tokens(bot_stats['total_given'])}",
                    inline=True)
    embed.add_field(name="Total in System",
                    value=f"{format_tokens(bot_stats['total_in_system'])}",
                    inline=True)
    embed.add_field(name="Current Profit",
                    value=f"{format_tokens(profit)}",
                    inline=True)
    embed.add_field(name="Total Users", value=f"{total_users}", inline=True)
    embed.add_field(name="Giveaway Pool",
                    value=f"{format_tokens(max(0, profit // 4))}",
                    inline=True)

    await ctx.send(embed=embed)


@bot.command(name='setchannel')
async def set_giveaway_channel(ctx):
    """Set the current channel as the giveaway announcement channel (owner only)"""
    if ctx.author.id != config['owner_id']:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    config['giveaway_channel_id'] = ctx.channel.id
    save_config()

    await ctx.send(f"✅ Giveaway channel set to {ctx.channel.mention}")


@bot.command(name='chestlog')
async def set_chest_log_channel(ctx):
    """Set the current channel for chest log messages (owner only)"""
    if ctx.author.id != config['owner_id']:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    config['chest_log_channel_id'] = ctx.channel.id
    save_config()

    await ctx.send(f"✅ Chest log channel set to {ctx.channel.mention}")


@bot.command(name='setodds')
async def set_odds(ctx, game=None, new_odds=None):
    """Configure game odds and settings (owner only)"""
    if ctx.author.id != config['owner_id']:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    if game is None:
        # Show current settings
        embed = discord.Embed(
            title="🎲 Current Game Settings",
            description="Current odds and configurations for all games",
            color=0x0099ff)

        embed.add_field(
            name="🃏 Blackjack",
            value=f"Win Rate: {config['blackjack_win_rate']*100:.1f}%",
            inline=True)

        embed.add_field(
            name="🪙 Coin Flip",
            value=f"Win Rate: {config['coinflip_win_rate']*100:.1f}%",
            inline=True)

        embed.add_field(
            name="🎰 Raffle",
            value=
            f"Ticket Cost: {format_tokens(config['raffle_ticket_cost'])}\nJackpot: {format_tokens(config['raffle_jackpot'])}\nWin Chance: {config['raffle_win_chance']*100:.6f}%",
            inline=False)

        embed.add_field(name="💣 Mines",
                        value="**Fair & Random** - No rigging applied!",
                        inline=True)

        embed.add_field(
            name="📝 Usage",
            value=
            "```!setodds blackjack 35\n!setodds coinflip 50\n!setodds raffle_cost 15000\n!setodds raffle_jackpot 2000000000```",
            inline=False)

        await ctx.send(embed=embed)
        return

    if new_odds is None:
        await ctx.send("❌ Please provide a new value!")
        return

    try:
        if game.lower() == 'blackjack':
            new_odds = float(new_odds)
            if not 0 < new_odds <= 100:
                await ctx.send("❌ Win rate must be between 0 and 100!")
                return
            config['blackjack_win_rate'] = new_odds / 100.0
            await ctx.send(f"✅ Blackjack win rate set to {new_odds}%")

        elif game.lower() == 'coinflip':
            new_odds = float(new_odds)
            if not 0 < new_odds <= 100:
                await ctx.send("❌ Win rate must be between 0 and 100!")
                return
            config['coinflip_win_rate'] = new_odds / 100.0
            await ctx.send(f"✅ Coin flip win rate set to {new_odds}%")

        elif game.lower() == 'raffle_cost':
            new_odds = int(new_odds)
            if new_odds <= 0:
                await ctx.send("❌ Raffle cost must be positive!")
                return
            config['raffle_ticket_cost'] = new_odds
            await ctx.send(
                f"✅ Raffle ticket cost set to {format_tokens(new_odds)}")

        elif game.lower() == 'raffle_jackpot':
            new_odds = int(new_odds)
            if new_odds <= 0:
                await ctx.send("❌ Raffle jackpot must be positive!")
                return
            config['raffle_jackpot'] = new_odds
            await ctx.send(f"✅ Raffle jackpot set to {format_tokens(new_odds)}"
                           )

        else:
            await ctx.send(
                "❌ Unknown game! Use: blackjack, coinflip, raffle_cost, or raffle_jackpot"
            )
            return

        save_config()

    except ValueError:
        await ctx.send("❌ Invalid value! Please provide a valid number.")


# Deposit ticket system
class TicketCloseView(discord.ui.View):

    def __init__(self, owner_id, creator_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.creator_id = creator_id

    @discord.ui.button(label='Close Ticket',
                       style=discord.ButtonStyle.red,
                       emoji='🔒')
    async def close_ticket(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        # Only owner can close tickets
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Only the bot owner can close tickets!", ephemeral=True)
            return

        # Delete the channel
        await interaction.response.send_message("🔒 Closing ticket...",
                                                ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()


@bot.command(name='deposit')
async def deposit_command(ctx):
    """Create a private deposit ticket channel"""
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return

    # Create private channel
    category = None
    for cat in ctx.guild.categories:
        if cat.name.lower() == 'tickets':
            category = cat
            break

    if not category:
        # Create tickets category if it doesn't exist
        category = await ctx.guild.create_category('Tickets')

    # Set up permissions
    overwrites = {
        ctx.guild.default_role:
        discord.PermissionOverwrite(view_channel=False),
        ctx.author:
        discord.PermissionOverwrite(view_channel=True, send_messages=True),
        ctx.guild.me:
        discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    # Add owner permissions
    owner = ctx.guild.get_member(config['owner_id'])
    if owner:
        overwrites[owner] = discord.PermissionOverwrite(view_channel=True,
                                                        send_messages=True)

    # Create channel
    channel_name = f"deposit-{ctx.author.name.lower()}"
    channel = await ctx.guild.create_text_channel(channel_name,
                                                  category=category,
                                                  overwrites=overwrites)

    # Send confirmation to user
    await ctx.send(f"✅ Created deposit ticket: {channel.mention}")

    # Send welcome message in the ticket
    embed = discord.Embed(
        title="🎫 Deposit Ticket Created",
        description=
        f"**User:** {ctx.author.mention}\n**Created:** {discord.utils.format_dt(datetime.now())}\n\n💰 Please describe your deposit request below.",
        color=0x00ff00)

    # Always ping limeytaco
    ping_message = "<@limeytaco> "

    # Create close ticket view
    view = TicketCloseView(config['owner_id'], ctx.author.id)

    await channel.send(f"{ping_message}New deposit ticket created!",
                       embed=embed,
                       view=view)


@bot.command(name='withdraw')
async def withdraw_command(ctx):
    """Create a private withdrawal ticket channel"""
    if not ctx.guild:
        await ctx.send("❌ This command can only be used in a server!")
        return

    # Create private channel
    category = None
    for cat in ctx.guild.categories:
        if cat.name.lower() == 'tickets':
            category = cat
            break

    if not category:
        # Create tickets category if it doesn't exist
        category = await ctx.guild.create_category('Tickets')

    # Set up permissions
    overwrites = {
        ctx.guild.default_role:
        discord.PermissionOverwrite(view_channel=False),
        ctx.author:
        discord.PermissionOverwrite(view_channel=True, send_messages=True),
        ctx.guild.me:
        discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    # Add owner permissions
    owner = ctx.guild.get_member(config['owner_id'])
    if owner:
        overwrites[owner] = discord.PermissionOverwrite(view_channel=True,
                                                        send_messages=True)

    # Create channel
    channel_name = f"withdrawal-{ctx.author.name.lower()}"
    channel = await ctx.guild.create_text_channel(channel_name,
                                                  category=category,
                                                  overwrites=overwrites)

    # Send confirmation to user
    await ctx.send(
        f"Creating a withdrawal ticket... (This can take 5 - 10 seconds...)")
    time.sleep(random.randint(5, 10))
    await ctx.send(f"✅ Created withdrawal ticket: {channel.mention}")

    # Send welcome message in the ticket
    user_balance = get_user_balance(ctx.author.id)
    embed = discord.Embed(
        title="💸 Withdrawal Ticket Created",
        description=
        f"**User:** {ctx.author.mention}\n**Created:** {discord.utils.format_dt(datetime.now())}\n**Current Balance:** {format_tokens(user_balance)}\n\n💰 Please specify your withdrawal request below.",
        color=0xff8800)

    # Always ping limeytaco
    ping_message = "<@1221338797602635827> "

    # Create close ticket view
    view = TicketCloseView(config['owner_id'], ctx.author.id)

    await channel.send(f"{ping_message}New withdrawal ticket created!",
                       embed=embed,
                       view=view)


@tasks.loop(hours=24)
async def daily_giveaway():
    """Daily giveaway task that runs every 24 hours"""
    profit = calculate_profit()

    if profit <= 0:
        logger.info("No profit for giveaway")
        return

    giveaway_amount = profit // 4
    if giveaway_amount <= 0:
        logger.info("Giveaway amount too small")
        return

    # Get all users with balances
    eligible_users = [
        user_id for user_id, balance in user_balances.items() if balance > 0
    ]

    if not eligible_users:
        logger.info("No eligible users for giveaway")
        return

    # Select random winner
    winner_id = random.choice(eligible_users)
    current_balance = get_user_balance(int(winner_id))
    set_user_balance(int(winner_id), current_balance + giveaway_amount)

    # Update statistics
    bot_stats['last_giveaway'] = datetime.now().isoformat()
    bot_stats['total_given'] += giveaway_amount
    save_data()

    # Get winner user object
    winner_user = bot.get_user(int(winner_id))
    if winner_user is None:
        logger.error(f"Could not find user with ID {winner_id}")
        return

    # Send giveaway announcement
    announcement = f"DAILY GIVEAWAY WINNER: **{winner_user.mention}** - {format_tokens(giveaway_amount)}"

    # Send to configured channel or first available channel
    channel = None
    if config.get('giveaway_channel_id'):
        channel = bot.get_channel(config['giveaway_channel_id'])

    if channel is None:
        # Find any available channel
        for guild in bot.guilds:
            for text_channel in guild.text_channels:
                if text_channel.permissions_for(guild.me).send_messages:
                    channel = text_channel
                    break
            if channel:
                break

    if channel:
        embed = discord.Embed(title="🎉 DAILY GIVEAWAY WINNER! 🎉",
                              description=announcement,
                              color=0xffd700)
        await channel.send(embed=embed)
        logger.info(f"Daily giveaway sent: {announcement}")
    else:
        logger.error("No available channel to send giveaway announcement")


@daily_giveaway.before_loop
async def before_daily_giveaway():
    """Wait for bot to be ready before starting daily giveaway loop"""
    await bot.wait_until_ready()


# Error handlers
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required arguments! Check the command usage."
                       )
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument! Please check your input.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        logger.error(f"Command error: {error}")
        await ctx.send("❌ An error occurred while processing your command.")


# Commands help
@bot.command(name='leaderboard', aliases=['lb'])
async def leaderboard_command(ctx):
    """Show the server leaderboard of richest players"""
    if not user_balances:
        await ctx.send("❌ No players have balances yet!")
        return

    # Sort users by balance (highest first)
    sorted_balances = sorted(user_balances.items(),
                             key=lambda x: x[1],
                             reverse=True)

    # Take top 10 players
    top_players = sorted_balances[:10]

    embed = discord.Embed(title="🏆 Casino Leaderboard",
                          description="Top 10 richest players in the server",
                          color=0xffd700)

    leaderboard_text = ""
    for rank, (user_id, balance) in enumerate(top_players, 1):
        try:
            user = bot.get_user(int(user_id))
            if user:
                username = user.display_name
            else:
                username = f"<@{user_id}>"
        except:
            username = f"<@{user_id}>"

        # Add medal emojis for top 3
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"
        else:
            medal = f"{rank}."

        leaderboard_text += f"{medal} **{username}** - {format_tokens(balance)}\n"

    embed.add_field(name="💰 Top Players", value=leaderboard_text, inline=False)

    # Add some stats
    total_players = len(user_balances)
    total_tokens = sum(user_balances.values())

    embed.add_field(
        name="📊 Server Stats",
        value=
        f"**Total Players:** {total_players:,}\n**Total Tokens:** {format_tokens(total_tokens)}",
        inline=True)

    # Show requesting user's rank if not in top 10
    user_rank, total_count = get_balance_rank(ctx.author.id)
    if user_rank > 10:
        user_balance = get_user_balance(ctx.author.id)
        embed.add_field(
            name="📍 Your Position",
            value=
            f"**Rank #{user_rank}** of {total_count}\n{format_tokens(user_balance)}",
            inline=True)

    embed.set_footer(text="💎 Keep playing to climb the ranks! 💎")
    await ctx.send(embed=embed)


class ChestQuantityView(discord.ui.View):

    def __init__(self, user_id, chest_key, chest_data):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.chest_key = chest_key
        self.chest_data = chest_data

        # Add buttons for different quantities
        self.add_quantity_button(1)
        self.add_quantity_button(3)
        self.add_quantity_button(10)

        # Only add Buy 100 button if user has the bulk chest opener
        user_items = get_user_items(user_id)
        if "bulkchest" in user_items:
            self.add_quantity_button(100)
        else:
            # Add disabled Buy 100 button with special message
            buy_100_button = discord.ui.Button(
                label="Buy 100",
                style=discord.ButtonStyle.secondary,
                disabled=True)

            async def need_bulk_opener(interaction):
                await interaction.response.send_message(
                    "❌ You need to buy the Bulk Chest Opener first to open 100 chests at once!",
                    ephemeral=True)

            buy_100_button.callback = need_bulk_opener
            self.add_item(buy_100_button)

    def add_quantity_button(self, quantity):
        """Add a quantity button"""
        button = discord.ui.Button(label=f"Buy {quantity}",
                                   style=discord.ButtonStyle.primary)

        async def quantity_callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "❌ This isn't your purchase!", ephemeral=True)
                return

            await self.handle_chest_purchase(interaction, quantity)

        button.callback = quantity_callback
        self.add_item(button)

    async def handle_chest_purchase(self, interaction, quantity):
        """Handle chest purchase and opening"""
        current_balance = get_user_balance(self.user_id)
        total_cost = self.chest_data['price'] * quantity

        if total_cost > current_balance:
            await interaction.response.send_message(
                f"❌ You need {format_tokens(total_cost)} to buy {quantity} {self.chest_data['name']}{'s' if quantity > 1 else ''}! You have {format_tokens(current_balance)}.",
                ephemeral=True)
            return

        # Send opening message
        opening_embed = discord.Embed(
            title=f"{self.chest_data['emoji']} Opening...",
            description=
            f"Opening {quantity} {self.chest_data['name']}{'s' if quantity > 1 else ''}...",
            color=0xffff00)
        await interaction.response.send_message(embed=opening_embed)

        # Add delay for effect
        await asyncio.sleep(2)

        # Open chests
        total_money_won = 0
        items_won = []

        for i in range(quantity):
            reward = open_single_chest(self.chest_key)

            if reward and len(reward) == 2:
                reward_type, reward_value = reward
                if reward_type == "money":
                    total_money_won += reward_value
                elif reward_type == "multiple_items":
                    for sub_reward in reward_value:
                        if len(sub_reward) == 2:
                            sub_type, sub_value = sub_reward
                            if sub_type == "money":
                                total_money_won += sub_value
                            else:
                                items_won.append(sub_value)
                                add_to_inventory(self.user_id, sub_value)
                else:
                    items_won.append(reward_value)
                    add_to_inventory(self.user_id, reward_value)

        # Send batched log message
        if items_won:
            user = interaction.user
            await send_chest_log(user, items_won)

        # Update balance
        new_balance = current_balance - total_cost + total_money_won
        set_user_balance(self.user_id, new_balance)

        # Update player statistics
        won = total_money_won > total_cost
        update_player_stats(self.user_id, 'chest', won, total_cost,
                            total_money_won)

        # Create result embed
        net_result = total_money_won - total_cost

        if quantity == 1:
            if items_won:
                color = 0xffd700
                title = f"🎉 {self.chest_data['emoji']} {self.chest_data['name']} Opened!"
                description = f"You won: **{items_won[0]}**!\n\n**Cost:** {format_tokens(total_cost)}"
            else:
                color = 0x00ff00 if net_result > 0 else 0xff0000
                title = f"{self.chest_data['emoji']} {self.chest_data['name']} Opened!"
                description = f"You won: **{format_tokens(total_money_won)}**!\n\n**Cost:** {format_tokens(total_cost)}\n**Net:** {format_tokens(net_result)} {'📈' if net_result > 0 else '📉'}"

            description += f"\n**New Balance:** {format_tokens(new_balance)}"

            result_embed = discord.Embed(title=title,
                                         description=description,
                                         color=color)
        else:
            color = 0x00ff00 if net_result > 0 or items_won else 0xff0000
            title = f"{self.chest_data['emoji']} Opened {quantity} {self.chest_data['name']}s!"

            description = f"**Total Cost:** {format_tokens(total_cost)}\n"
            if total_money_won > 0:
                description += f"**Money Won:** {format_tokens(total_money_won)}\n**Net Money:** {format_tokens(net_result)} {'📈' if net_result > 0 else '📉'}\n"
            description += f"**New Balance:** {format_tokens(new_balance)}"

            result_embed = discord.Embed(title=title,
                                         description=description,
                                         color=color)

            # Show items won
            if items_won:
                items_breakdown = {}
                for item in items_won:
                    items_breakdown[item] = items_breakdown.get(item, 0) + 1

                items_text = ""
                for item, count in items_breakdown.items():
                    items_text += f"**{item}** x{count}\n"

                result_embed.add_field(name="🎁 Items Won",
                                       value=items_text,
                                       inline=False)

        # Check for bankruptcy
        if new_balance == 0:
            await send_dm_notification(
                self.user_id, "💔 You've gone bankrupt! Better luck next time.")

        # Edit the opening message with results
        await interaction.edit_original_response(embed=result_embed)


class ShopView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id


@bot.command(name='shop')
async def shop_command(ctx, item_name=None):
    """View the casino shop and available items"""
    if item_name is None:
        # Show shop overview
        embed = discord.Embed(
            title="🛒 Casino Shop",
            description="Browse our premium items and chests!",
            color=0x9932cc)

        for item_id, item in SHOP_ITEMS.items():
            embed.add_field(
                name=
                f"{item['emoji']} {item['name']} - {format_tokens(item['price'])} (ID: {item['id']})",
                value=item['short_description'],
                inline=True)

        embed.add_field(
            name="💡 How to Use",
            value=
            "Use `!shop <item>` to see full details, odds, and buy options!\nExample: `!shop vip`, `!shop bronze`, or `!shop S1`",
            inline=False)

        embed.set_footer(
            text="💎 Use !shop <item> for detailed info and purchase options! 💎"
        )
        await ctx.send(embed=embed)
        return

    # Show specific item details
    item_input = item_name.upper()
    item_key = None

    # Check if it's an ID first
    for key, shop_item in SHOP_ITEMS.items():
        if shop_item['id'] == item_input:
            item_key = key
            break

    # If not found by ID, try by name
    if item_key is None:
        item_input = item_name.lower()
        if item_input in SHOP_ITEMS:
            item_key = item_input

    if item_key is None:
        await ctx.send(
            "❌ That item doesn't exist! Use `!shop` to see available items.")
        return

    item_data = SHOP_ITEMS[item_key]

    embed = discord.Embed(title=f"{item_data['emoji']} {item_data['name']}",
                          description=item_data['description'],
                          color=0x9932cc)

    embed.add_field(name="💰 Price",
                    value=format_tokens(item_data['price']),
                    inline=True)

    embed.add_field(name="🆔 Item ID", value=item_data['id'], inline=True)

    if item_data['boost'] > 0:
        duration_text = "Permanent" if item_data[
            'duration'] == -1 else f"{item_data['duration']//3600} hour{'s' if item_data['duration']//3600 != 1 else ''}"
        embed.add_field(
            name="⚡ Boost Info",
            value=
            f"**Boost:** +{item_data['boost']*100:.1f}%\n**Duration:** {duration_text}",
            inline=False)

    # Show odds for chest items
    if item_key in [
            "bronze", "silver", "diamond", "cards", "tickets", "titanic",
            "enchant", "mega"
    ]:
        chest_data = CHEST_TYPES[item_key]
        odds_text = ""
        for prob, (reward_type, reward_value) in chest_data["rewards"]:
            if reward_type == "money":
                odds_text += f"**{prob*100:.3f}%** - {format_tokens(reward_value)}\n"
            else:
                odds_text += f"**{prob*100:.4f}%** - {reward_value}\n"

        embed.add_field(name="🎲 Drop Rates", value=odds_text, inline=False)

    # Create buy button
    view = discord.ui.View(timeout=300)

    async def buy_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                "❌ This isn't your shop session!", ephemeral=True)
            return

        # Execute buy logic
        user_id = interaction.user.id
        current_balance = get_user_balance(user_id)

        # Handle different item types
        if item_key in [
                "bronze", "silver", "diamond", "cards", "tickets", "titanic",
                "enchant", "mega"
        ]:
            # These are chest items - show quantity selection buttons
            chest_view = ChestQuantityView(user_id, item_key, item_data)
            chest_embed = discord.Embed(
                title=f"{item_data['emoji']} {item_data['name']}",
                description=
                f"**Price per chest:** {format_tokens(item_data['price'])}\n**Your balance:** {format_tokens(current_balance)}\n\nSelect quantity to open:",
                color=0x9932cc)

            await interaction.response.send_message(embed=chest_embed,
                                                    view=chest_view,
                                                    ephemeral=True)
            return

        if current_balance < item_data['price']:
            await interaction.response.send_message(
                f"❌ You need {format_tokens(item_data['price'])} to buy this item! You have {format_tokens(current_balance)}.",
                ephemeral=True)
            return

        if item_key == "bulkchest":
            # Check if user already has bulk chest opener
            user_items_data = get_user_items(user_id)
            if item_key in user_items_data:
                await interaction.response.send_message(
                    f"❌ You already own {item_data['name']}!", ephemeral=True)
                return

            # Add bulk chest opener item
            user_items_data[item_key] = {
                'name': item_data['name'],
                'emoji': item_data['emoji'],
                'purchased_at': datetime.now().timestamp()
            }
        else:
            # Handle boost items
            user_boosts_data = get_user_boosts(user_id)
            if item_key in user_boosts_data:
                if item_data['duration'] == -1:  # Permanent item
                    await interaction.response.send_message(
                        f"❌ You already own {item_data['name']}!",
                        ephemeral=True)
                    return
                else:
                    # Extend duration for temporary items
                    current_time = datetime.now().timestamp()
                    current_expires = user_boosts_data[item_key].get(
                        'expires_at', current_time)

                    # If current boost hasn't expired, extend from expiry time, otherwise from now
                    extend_from = max(current_time, current_expires)
                    new_expires = extend_from + item_data['duration']

                    user_boosts_data[item_key]['expires_at'] = new_expires
            else:
                # Add new boost
                current_time = datetime.now().timestamp()
                expires_at = current_time + item_data['duration'] if item_data[
                    'duration'] != -1 else -1

                user_boosts_data[item_key] = {
                    'name': item_data['name'],
                    'emoji': item_data['emoji'],
                    'boost': item_data['boost'],
                    'duration': item_data['duration'],
                    'expires_at': expires_at,
                    'purchased_at': current_time
                }

        # Deduct money for non-chest items
        if item_key not in [
                "bronze", "silver", "diamond", "cards", "tickets", "titanic",
                "enchant", "mega"
        ]:
            new_balance = current_balance - item_data['price']
            set_user_balance(user_id, new_balance)

            result_embed = discord.Embed(
                title="✅ Purchase Successful!",
                description=
                f"You bought {item_data['emoji']} **{item_data['name']}**!",
                color=0x00ff00)

            result_embed.add_field(
                name="💰 Transaction",
                value=
                f"**Cost:** {format_tokens(item_data['price'])}\n**New Balance:** {format_tokens(new_balance)}",
                inline=True)

            if item_data['duration'] != -1 and item_data['duration'] > 0:
                duration_text = f"{item_data['duration']//3600} hour{'s' if item_data['duration']//3600 != 1 else ''}"
                result_embed.add_field(
                    name="⏰ Duration",
                    value=
                    f"**Active for:** {duration_text}\n**Boost:** +{item_data['boost']*100:.1f}%",
                    inline=True)
            elif item_data['boost'] > 0:
                result_embed.add_field(
                    name="♾️ Permanent",
                    value=
                    f"**Boost:** +{item_data['boost']*100:.1f}%\n**Forever!**",
                    inline=True)

            await interaction.response.send_message(embed=result_embed)

        # Save data
        save_data()

    buy_button = discord.ui.Button(label=f"Buy for {item_data['price']:,}",
                                   style=discord.ButtonStyle.success,
                                   emoji="💰")
    buy_button.callback = buy_callback
    view.add_item(buy_button)

    await ctx.send(embed=embed, view=view)


class InventoryExchangeView(discord.ui.View):

    def __init__(self, user_id, total_value):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.total_value = total_value

    @discord.ui.button(label=f'Exchange All Items',
                       style=discord.ButtonStyle.success,
                       emoji='💰')
    async def exchange_all_button(self, interaction: discord.Interaction,
                                  button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your inventory!", ephemeral=True)
            return

        # Create confirmation view
        confirm_view = InventoryExchangeConfirmView(self.user_id,
                                                    self.total_value)

        embed = discord.Embed(
            title="⚠️ Confirm Exchange",
            description=
            f"**You will exchange ALL items for {format_tokens(self.total_value)}**\n\n🚨 **Warning: You will not get these items back. Proceed?**",
            color=0xff8800)

        await interaction.response.send_message(embed=embed,
                                                view=confirm_view,
                                                ephemeral=True)


class InventoryExchangeConfirmView(discord.ui.View):

    def __init__(self, user_id, total_value):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.total_value = total_value

    @discord.ui.button(label='Confirm Exchange',
                       style=discord.ButtonStyle.danger,
                       emoji='✅')
    async def confirm_button(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This isn't your exchange!", ephemeral=True)
            return

        # Get inventory and exchange all items
        inventory = get_user_inventory(self.user_id)
        if not inventory:
            await interaction.response.send_message(
                "❌ Your inventory is empty!", ephemeral=True)
            return

        # Calculate actual total value (in case inventory changed)
        actual_total = 0
        items_exchanged = 0

        for item_id, item_data in list(inventory.items()):
            item_name = item_data['name']
            item_value = ITEM_VALUES.get(item_name, 0)
            if item_value > 0:
                actual_total += item_value
                items_exchanged += 1
                # Remove item from inventory
                remove_from_inventory(self.user_id, item_id)

        # Add tokens to balance
        current_balance = get_user_balance(self.user_id)
        new_balance = current_balance + actual_total
        set_user_balance(self.user_id, new_balance)

        # Create success embed
        embed = discord.Embed(
            title="✅ Exchange Complete!",
            description=
            f"Successfully exchanged {items_exchanged} items for {format_tokens(actual_total)}!",
            color=0x00ff00)

        embed.add_field(
            name="💰 Balance Update",
            value=
            f"**Previous Balance:** {format_tokens(current_balance)}\n**Exchange Value:** {format_tokens(actual_total)}\n**New Balance:** {format_tokens(new_balance)}",
            inline=False)

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label='Cancel',
                       style=discord.ButtonStyle.secondary,
                       emoji='❌')
    async def cancel_button(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        embed = discord.Embed(title="❌ Exchange Cancelled",
                              description="Your items are safe and sound!",
                              color=0xff0000)
        await interaction.response.edit_message(embed=embed, view=None)


@bot.command(name='inv', aliases=['inventory'])
async def inventory_command(ctx,
                            user: discord.Member = None,
                            action=None,
                            item_id=None,
                            quantity=None):
    """Check inventory or manage items (admins can check others and remove items)"""
    # Admin check for checking other users' inventories or removing items
    is_admin = ctx.author.id == config['owner_id']

    # Determine target user
    if user is None or not is_admin:
        target_user = ctx.author
        target_user_id = ctx.author.id
    else:
        target_user = user
        target_user_id = user.id

    # Handle remove action (admin only)
    if action == "remove" and item_id:
        if not is_admin:
            await ctx.send("❌ Only admins can remove items from inventories!")
            return

        # Parse quantity
        if quantity is None:
            quantity = 1
        else:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    await ctx.send("❌ Quantity must be a positive number!")
                    return
            except ValueError:
                await ctx.send(
                    "❌ Invalid quantity! Please provide a valid number.")
                return

        inventory = get_user_inventory(target_user_id)

        # Find items with the specified ID
        items_to_remove = []
        for inv_id, item_data in inventory.items():
            if inv_id.upper() == item_id.upper():
                items_to_remove.append((inv_id, item_data))

        if not items_to_remove:
            await ctx.send(
                f"❌ Item with ID {item_id.upper()} not found in {target_user.mention}'s inventory."
            )
            return

        if len(items_to_remove) < quantity:
            await ctx.send(
                f"❌ Only {len(items_to_remove)} item(s) with ID {item_id.upper()} found, cannot remove {quantity}."
            )
            return

        # Remove the specified quantity
        removed_items = []
        for i in range(quantity):
            inv_id, item_data = items_to_remove[i]
            removed_item = remove_from_inventory(target_user_id, inv_id)
            if removed_item:
                removed_items.append(removed_item)

        if removed_items:
            item_name = removed_items[0]['name']
            if quantity == 1:
                await ctx.send(
                    f"✅ Removed **{item_name}** (ID: {item_id.upper()}) from {target_user.mention}'s inventory."
                )
            else:
                await ctx.send(
                    f"✅ Removed {quantity}x **{item_name}** from {target_user.mention}'s inventory."
                )
        else:
            await ctx.send(
                f"❌ Failed to remove items from {target_user.mention}'s inventory."
            )
        return

    # Show inventory
    inventory = get_user_inventory(target_user_id)

    if not inventory:
        if target_user == ctx.author:
            await ctx.send(
                "📦 Your inventory is empty! Open some chests to get items.")
        else:
            await ctx.send(f"📦 {target_user.mention}'s inventory is empty!")
        return

    # Fix f-string syntax - cannot use backslashes in expressions
    if target_user == ctx.author:
        title = "📦 Your Inventory"
    else:
        title = f"📦 {target_user.display_name}'s Inventory"

    embed = discord.Embed(title=title,
                          description=f"Items collected from chests and games",
                          color=0x9932cc)

    # Group items by name and calculate total value
    item_groups = {}
    total_value = 0

    for inv_id, item_data in inventory.items():
        item_name = item_data['name']
        if item_name not in item_groups:
            item_groups[item_name] = []
        item_groups[item_name].append((inv_id, item_data))

        # Add to total value if item has value
        item_value = ITEM_VALUES.get(item_name, 0)
        total_value += item_value

    # Show grouped items with values
    for item_name, items in item_groups.items():
        item_value = ITEM_VALUES.get(item_name, 0)
        value_text = f" (Worth: {format_tokens(item_value)} each)" if item_value > 0 else " (No exchange value)"

        if len(items) == 1:
            inv_id, item_data = items[0]
            obtained_time = datetime.fromtimestamp(
                item_data['obtained_at']).strftime("%m/%d/%Y")
            embed.add_field(name=f"**{item_name}**{value_text}",
                            value=f"Obtained: {obtained_time}",
                            inline=True)
        else:
            # Show count without IDs
            obtained_time = datetime.fromtimestamp(
                items[0][1]['obtained_at']).strftime("%m/%d/%Y")
            total_item_value = item_value * len(items)
            value_text = f" (Total: {format_tokens(total_item_value)})" if item_value > 0 else " (No exchange value)"

            embed.add_field(name=f"**{item_name}** x{len(items)}{value_text}",
                            value=f"First obtained: {obtained_time}",
                            inline=True)

    # Add total value field
    if total_value > 0:
        embed.add_field(name="💰 Total Exchange Value",
                        value=format_tokens(total_value),
                        inline=False)

    embed.set_footer(
        text=
        f"Total items: {len(inventory)} | Use !showid to reveal IDs (admin only)"
    )

    # Add exchange button only for own inventory and if items have value
    view = None
    if target_user == ctx.author and total_value > 0:
        view = InventoryExchangeView(target_user_id, total_value)

    await ctx.send(embed=embed, view=view)


@bot.command(name='showid')
async def showid_command(ctx, user: discord.Member = None):
    """Show all item IDs in inventory (admin only)"""
    if ctx.author.id != config['owner_id']:
        await ctx.send("❌ Only admins can use this command!")
        return

    # Determine target user
    if user is None:
        target_user = ctx.author
        target_user_id = ctx.author.id
    else:
        target_user = user
        target_user_id = user.id

    inventory = get_user_inventory(target_user_id)

    if not inventory:
        if target_user == ctx.author:
            await ctx.send("📦 Your inventory is empty!")
        else:
            await ctx.send(f"📦 {target_user.mention}'s inventory is empty!")
        return

    # Create embed with all IDs visible
    if target_user == ctx.author:
        title = "🔍 Your Inventory (Admin View)"
    else:
        title = f"🔍 {target_user.display_name}'s Inventory (Admin View)"

    embed = discord.Embed(title=title,
                          description="Complete inventory with item IDs",
                          color=0xff0000)  # Red color to indicate admin view

    # Group items by name
    item_groups = {}
    total_value = 0

    for inv_id, item_data in inventory.items():
        item_name = item_data['name']
        if item_name not in item_groups:
            item_groups[item_name] = []
        item_groups[item_name].append((inv_id, item_data))

        # Add to total value
        item_value = ITEM_VALUES.get(item_name, 0)
        total_value += item_value

    # Show all items with IDs
    for item_name, items in item_groups.items():
        item_value = ITEM_VALUES.get(item_name, 0)
        value_text = f" (Worth: {format_tokens(item_value)} each)" if item_value > 0 else " (No value)"

        if len(items) == 1:
            inv_id, item_data = items[0]
            obtained_time = datetime.fromtimestamp(
                item_data['obtained_at']).strftime("%m/%d/%Y")
            embed.add_field(
                name=f"**{item_name}**{value_text}",
                value=f"**ID: {inv_id}**\nObtained: {obtained_time}",
                inline=True)
        else:
            # Show all IDs for multiple items
            ids_list = [inv_id for inv_id, _ in items]
            obtained_time = datetime.fromtimestamp(
                items[0][1]['obtained_at']).strftime("%m/%d/%Y")
            total_item_value = item_value * len(items)
            value_text = f" (Total: {format_tokens(total_item_value)})" if item_value > 0 else " (No value)"

            # Split IDs into chunks if too many
            if len(ids_list) <= 10:
                ids_text = f"**IDs: {', '.join(ids_list)}**"
            else:
                ids_text = f"**IDs: {', '.join(ids_list[:10])}**\n*+{len(ids_list)-10} more...*"

            embed.add_field(name=f"**{item_name}** x{len(items)}{value_text}",
                            value=f"{ids_text}\nFirst: {obtained_time}",
                            inline=True)

    # Add total value
    if total_value > 0:
        embed.add_field(name="💰 Total Exchange Value",
                        value=format_tokens(total_value),
                        inline=False)

    embed.set_footer(
        text=
        f"Total items: {len(inventory)} | Use !inv {target_user.mention} remove <id> <quantity>"
    )

    await ctx.send(embed=embed)


@bot.command(name='buy')
async def buy_command(ctx, item=None):
    """Disabled command - redirects to shop"""
    await ctx.send(
        "❌ The `!buy` command has been disabled! Please use `!shop` instead to browse and purchase items."
    )


# Slots machine game
SLOT_SYMBOLS = {
    "🍒": {
        "multiplier": 1.5,
        "weight": 15
    },  # Cherry - common, low multiplier
    "🍋": {
        "multiplier": 1.7,
        "weight": 12
    },  # Lemon
    "🍊": {
        "multiplier": 2.0,
        "weight": 10
    },  # Orange
    "🍇": {
        "multiplier": 2.2,
        "weight": 8
    },  # Grapes
    "🔔": {
        "multiplier": 2.5,
        "weight": 6
    },  # Bell
    "⭐": {
        "multiplier": 2.8,
        "weight": 4
    },  # Star
    "💎": {
        "multiplier": 3.0,
        "weight": 2
    },  # Diamond - rare, high multiplier
    "🎰": {
        "multiplier": 3.0,
        "weight": 1
    }  # Jackpot symbol - very rare
}


def get_random_slot_symbol():
    """Get a random slot symbol based on weighted probabilities"""
    symbols = list(SLOT_SYMBOLS.keys())
    weights = [SLOT_SYMBOLS[symbol]["weight"] for symbol in symbols]
    return random.choices(symbols, weights=weights)[0]


def check_slots_win(symbols):
    """Check if the slot combination is a winner and return multiplier"""
    # Three of a kind
    if symbols[0] == symbols[1] == symbols[2]:
        return SLOT_SYMBOLS[symbols[0]]["multiplier"]

    # Two of a kind (smaller payout)
    if symbols[0] == symbols[1] or symbols[1] == symbols[2] or symbols[
            0] == symbols[2]:
        # Get the symbol that appears twice
        if symbols[0] == symbols[1]:
            symbol = symbols[0]
        elif symbols[1] == symbols[2]:
            symbol = symbols[1]
        else:
            symbol = symbols[0]
        return SLOT_SYMBOLS[symbol][
            "multiplier"] * 0.5  # Half multiplier for two of a kind

    return 0  # No win


@bot.command(name='slots', aliases=['slot'])
async def slots_command(ctx, bet):
    """Play the slot machine with animated spinning"""
    user_id = ctx.author.id
    current_balance = get_user_balance(user_id)

    # Parse bet amount
    parsed_bet = parse_bet_amount(bet, current_balance)
    if parsed_bet is None:
        await ctx.send(
            "❌ Invalid bet amount! Use numbers, 'all', or shorthand like 100k, 50m, 2.5b"
        )
        return

    bet = parsed_bet

    if bet <= 0:
        await ctx.send("❌ Bet must be positive!")
        return

    if bet > current_balance:
        await ctx.send("❌ You don't have enough tokens!")
        return

    # Check for cooldown to prevent spam
    current_time = time.time()
    if user_id in user_cooldowns:
        time_remaining = user_cooldowns[user_id] - current_time
        if time_remaining > 0:
            await ctx.send(
                f"⏳ Please wait {time_remaining:.1f} seconds before spinning again!"
            )
            return

    # Set cooldown (3 seconds for slots)
    user_cooldowns[user_id] = current_time + 3.0

    # Create initial spinning embed
    embed = discord.Embed(title="🎰 Slot Machine",
                          description="🎲 **SPINNING...** 🎲",
                          color=0xffff00)

    embed.add_field(name="🎯 Your Bet",
                    value=f"{format_tokens(bet)}",
                    inline=True)

    embed.add_field(name="💫 Reels", value="🎰 🎰 🎰", inline=True)

    message = await ctx.send(embed=embed)

    # Animation frames
    animation_frames = [["🎲", "🎲", "🎲"], ["🔄", "🔄", "🔄"], ["⚡", "⚡", "⚡"],
                        ["🌟", "🌟", "🌟"]]

    # Show animation
    for frame in animation_frames:
        await asyncio.sleep(0.8)
        embed.set_field_at(1,
                           name="💫 Reels",
                           value=f"{frame[0]} {frame[1]} {frame[2]}",
                           inline=True)
        await message.edit(embed=embed)

    # Determine if this should be a win (20% chance)
    should_win = random.random() < 0.2

    if should_win:
        # Force a winning combination - pick a random symbol and make 3 of a kind
        winning_symbol = get_random_slot_symbol()
        final_symbols = [winning_symbol, winning_symbol, winning_symbol]
        multiplier = SLOT_SYMBOLS[winning_symbol]["multiplier"]
    else:
        # Generate a losing combination
        final_symbols = [get_random_slot_symbol() for _ in range(3)]
        # If by chance it's a winning combo, change one symbol to guarantee loss
        if check_slots_win(final_symbols) > 0:
            # Simply replace the last symbol with a different one
            available_symbols = [
                s for s in SLOT_SYMBOLS.keys()
                if s != final_symbols[0] and s != final_symbols[1]
            ]
            if available_symbols:
                final_symbols[2] = random.choice(available_symbols)
        multiplier = 0

    # Final reveal with dramatic pause
    await asyncio.sleep(1)

    if multiplier > 0:
        # Win!
        base_winnings = int(bet * multiplier)
        total_winnings, boost_info = apply_boost_to_winnings(
            user_id, base_winnings)
        new_balance = current_balance - bet + total_winnings
        net_gain = total_winnings - bet

        embed.color = 0x00ff00
        embed.title = "🎰 SLOT MACHINE - WINNER! 🎉"
        embed.description = f"🎊 **{final_symbols[0]} {final_symbols[1]} {final_symbols[2]}** 🎊"

        balance_text = f"**Multiplier:** {multiplier:.1f}x\n**Base Winnings:** {format_tokens(base_winnings)}\n**Net Gain:** +{format_tokens(net_gain)}\n**New Balance:** {format_tokens(new_balance)}"
        if boost_info:
            balance_text = f"**Multiplier:** {multiplier:.1f}x\n**Base Winnings:** {format_tokens(boost_info['original'])}\n**{boost_info['boost_name']}:** +{format_tokens(boost_info['boost_amount'])}\n**Total Winnings:** {format_tokens(total_winnings)}\n**Net Gain:** +{format_tokens(net_gain)}\n**New Balance:** {format_tokens(new_balance)}"

        embed.set_field_at(1,
                           name="💰 Win Details",
                           value=balance_text,
                           inline=False)

        # Update player statistics
        update_player_stats(user_id, 'slots', True, bet, total_winnings)
    else:
        # Loss
        new_balance = current_balance - bet

        embed.color = 0xff0000
        embed.title = "🎰 Slot Machine - Try Again!"
        embed.description = f"💔 **{final_symbols[0]} {final_symbols[1]} {final_symbols[2]}** 💔"

        embed.set_field_at(
            1,
            name="💸 Result",
            value=
            f"**Loss:** -{format_tokens(bet)}\n**New Balance:** {format_tokens(new_balance)}",
            inline=False)

        # Update player statistics
        update_player_stats(user_id, 'slots', False, bet, 0)

        # Check for bankruptcy
        if new_balance == 0:
            await send_dm_notification(
                user_id, "💔 You've gone bankrupt! Better luck next time.")

    # Update balance
    set_user_balance(user_id, new_balance)

    # Show symbol meanings
    embed.add_field(
        name="🎰 Symbol Values",
        value="🍒(1.5x) 🍋(1.7x) 🍊(2.0x) 🍇(2.2x) 🔔(2.5x) ⭐(2.8x) 💎(3.0x) 🎰(3.0x)",
        inline=False)

    embed.set_field_at(
        1,
        name="🎯 Final Result",
        value=f"{final_symbols[0]} {final_symbols[1]} {final_symbols[2]}",
        inline=True)

    await message.edit(embed=embed)


@bot.command(name='commands')
async def commands_command(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🎰 Casino Commands",
        description=
        "🎲 **Welcome to the Casino!** 🎲\nTry your luck and win big with our exciting games!",
        color=0xffd700)

    embed.add_field(
        name="💰 **Balance & Money**",
        value=
        "`!balance` or `!bal` - Check your current token balance\n`!leaderboard` or `!lb` - View the server leaderboard\n`!deposit` - Create a private deposit ticket\n`!withdraw` - Create a private withdrawal ticket\n`!shop` - View the casino shop\n`!buy <item>` - Buy items from the shop",
        inline=False)

    embed.add_field(
        name="🎲 **Casino Games**",
        value=
        "`!blackjack <bet>` or `!bj <bet>` - Play a classic game of blackjack\n`!coinflip <bet>` or `!cf <bet>` - Call heads or tails on a coin flip\n`!slots <bet>` or `!slot <bet>` - Spin the slot machine for big wins!\n`!mines <bet> <mines>` - Avoid mines for huge multipliers (1-24 mines)\n`!raffle` - Buy a raffle ticket for the mega jackpot!",
        inline=False)

    embed.add_field(
        name="💡 **Bet Formats**",
        value=
        "You can use shorthand for bets:\n`100k` = 100,000 | `2.5m` = 2,500,000 | `1b` = 1,000,000,000\n`500q` = 500 quadrillion | `all` = your entire balance | `50%` = half your balance",
        inline=False)

    embed.add_field(
        name="🎉 **Daily Giveaway**",
        value=
        "Every 24 hours, a portion of the casino's profits is given away to a lucky winner!",
        inline=False)

    embed.set_footer(text="💎 Good luck and gamble responsibly! 💎")

    await ctx.send(embed=embed)


# Main execution
if __name__ == "__main__":
    # Load data and config
    load_data()
    load_config()

    # Get Discord token from environment
    token = "MTM5NTYyNzQwNzI4NDc2ODgzOA.GbfcWT.uc95P1QM2B5EdUgVeOuD_vDKeXUstp1sLKumgo"
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        exit(1)

    # Run the bot
    bot.run(token)
