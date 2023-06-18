import json

def flatten_dict(m):
    d = {}
    for item in m['map']:
        for t in item['terms']:
            d[t] = item['emoji']
    return d

def generate_dict(path):
    emoji_map = json.load(open(path))
    return flatten_dict(emoji_map)

def detect_emojis(string, path):
    emoji_dict = generate_dict(path)
    ls = string.split()
    for word in ls:
        try:
            found_emoji = emoji_dict[word]+" "
            break
        except KeyError:
            found_emoji = ''

    return found_emoji+string
