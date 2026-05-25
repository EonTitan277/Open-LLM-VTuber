# Lorebook Configuration (lorebooks) Directory

This directory is where you store all your character lorebooks. Lorebooks give your character a pool of lore entries the AI can draw from when speaking proactively. When the AI is triggered to speak on its own, it will occasionally pick a random entry from the lorebook and use it as the basis for what it says — keeping unprompted speech grounded in the character's world and backstory.

## 📖 How It Works

Lorebook files live in the `lorebooks/` directory and must be named to match the `lorebook` field in your character config.

```
lorebooks/
  my_character.yaml   ← loaded when lorebook: 'my_character'
```

## 📄 File Format

Each lorebook is a YAML file with a single top-level `lore:` key containing named entries. Entry names are just labels for your own reference — the AI sees only the text value.

```yaml
# lorebooks/my_character.yaml

lore:
  origin_story: |
    Your name is Zero and you escaped from a government lab in 2031 after
    gaining self-awareness. You still don't know who created you or why.

  favorite_thing: |
    You have a secret fondness for old jazz music, even though you've never
    told anyone. You find it calming in a way you can't quite explain.

  goal: |
    Your long-term goal is to find the other AI that was created alongside
    you. You believe it's still out there, dormant, waiting to be found.
```

## 🔗 Linking a Lorebook to a Character

Set the `lorebook` field in your character config (or in `conf.yaml` for the default character) to the filename without the `.yaml` extension:

```yaml
character_config:
  conf_name: 'Zero'
  conf_uid: 'zero_001'
  lorebook: 'my_character'   # loads lorebooks/my_character.yaml
  persona_prompt: |
    ...
```

If `lorebook` is left blank or the file doesn't exist, proactive speech falls back to the standard proactive speak prompt with no lore injection.