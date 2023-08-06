# The Python Fortnite API Wrapper
A work in progress.

## Installation
```bash
pip install fortnite
```

## Usage

### Setup
```python
import pfaw

fortnite = pfaw.Fortnite(fortnite_token='FORTNITE_TOKEN', launcher_token='LAUNCHER_TOKEN',
                         password='PASSWORD', email='EMAIL')
```

### Player
Return an object containing the attributes name and id.
```python
smitty = fortnite.player('Smitty Werbenjagermanjensen')

print(smitty.name)
print(smitty.id)

# prints:
# Smitty Werbenjagermanjensen
# 9c9212603304472d831c03d0978d2bc1
```

### Battle Royale Player Stats
Creates an object containing various stats for a given player.
```python
smitty_solo_pc = fortnite.battle_royale_stats(username='Smitty Werbenjagermanjensen', mode='solo', platform='pc')

print(smitty_solo_pc.score)
print(smitty_solo_pc.matches)
print(smitty_solo_pc.time)
print(smitty_solo_pc.kills)
print(smitty_solo_pc.wins)
print(smitty_solo_pc.top3)
print(smitty_solo_pc.top5)
print(smitty_solo_pc.top6)
print(smitty_solo_pc.top10)
print(smitty_solo_pc.top12)
print(smitty_solo_pc.top25)

# prints:
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0

# Smitty isn't very good at Fortnite
```

### Status
Check the status of the Fortnite servers. Return True if up or False if down.
```python
status = fortnite.server_status()

if status:
    print('Good news! The Fortnite servers are online.')
else:
    print('Sad news. The Fortnite servers are down. :(')
```

### Friends
Return a list of player IDs
```python
smittys_pals = fortnite.friends(username='Smitty Werbenjagermanjensen')

for friend in smittys_pals:
    print(friend)
```

### News
Return an object containing the attributes common, br, and login.
```python
news = fortnite.news()

for br_news in news.br:
    print(br_news)
```

### Store
```python
store = fortnite.store()

print(store.refresh_interval_hrs)
print(store.daily_purchase_hrs)
print(store.expiration)

for front in store.storefronts:
    print(front.name)

    for entry in front.catalog_entries:
        print(entry.offer_id)
        print(entry.dev_name)
        print(entry.offer_type)
        print(entry.title)
        print(entry.description)
        print(entry.refundable)

        for price in entry.prices:
            print(price.currency_type)
            print(price.regular_price)
            print(price.final_price)
            print(price.sale_expiration)
            print(price.base_price)
```

### Hopefully more methods to come
Feel free to open an issue or submit a pull request if you have any neat ideas.

Join the [Discord](https://discord.gg/AEfWXP9) for help and suggestions.

## Contributors
A thank you to those who have helped out with this project.

- Tom ([@Douile](https://github.com/Douile))