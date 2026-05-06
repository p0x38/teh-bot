# Locales Directory (`/src/assets/locales/`)

This directory contains all the translation resources for the bot, organized by locale and namespace. We use [Project Fluent](https://projectfluent.org/) to allow for natural-sounding, context-aware dialogue.

## Structure

```text
locales/
├── en_US/                # Locale folder (matches I18nContext.locale)
│   ├── commands.ftl      # Namespace for command responses
│   ├── errors.ftl        # Namespace for error messages
│   ├── personality.ftl   # Core bot dialogue and flavor text
│   └── <namespace>.ftl   # Custom namespace btw
└── ja/
    └── ...
```

## Available Variables

The `Translator` automatically injects the following variables from the `I18nContext`:

### Logic Variables
*   **`$streak`**: The number of times the user has repeated this specific command.
*   **`$seed`**: A random integer (1-16) used to select between message variants.
*   **`$hour`**: The current hour (0-23) for time-of-day logic.

### Personality Variables
*   **`$emotion`**: The bot's current mood (e.g., `happy`, `annoyed`, `mad`, `sad`).
*   **`$tone`**: The personality archetype (e.g., `casual`, `formal`, `chaotic`, `silly`).
*   **`$intensity`**: How strongly the personality traits are applied (`low`, `normal`, `high`).
*   **`$bot_name`**: The bot's name.
*   **`$bot_nick`**: The bot's nickname each guild (WIP).

### User/Context Variables
*   **`$is_admin`**: Boolean indicating if the user has admin permissions.
*   **`$is_new_user`**: Boolean to trigger unique first-time interactions.
*   **`$is_guild` / `$is_dm`**: Context of where the command was run.
*   **`$level`**: The user's progression level.

## Available Personality Tones
*   **Normal (`normal`)**: Normal tone.
*   **Casual (`casual`)**: Casual tone.
*   **Formal (`formal`)**: Formal tone.
*   **Silly (`silly`)**: Silly tone.
*   **Chaotic (`chaotic`)**: Chaotic tone.

## Available Emotions
*   **Neutral (`neutral`)**: Neutral mood.
*   **Angry (`angry`)**: Angry mood.
*   **Sad (`sad`)**: Sad mood.
*   **Happy (`happy`)**: Happy mood.
*   **Scared (`scared`)**: Scared mood.
*   **Annoyed (`annoyed`)**: Annoyed mood.
*   **Mad (`mad`)**: Mad mood.

## Writing Translations

### Basic Annoyance Logic
Use the `$streak` variable to change the bot's reaction as a user repeats a command:

```fluent
# commands.ftl
ping-command = { $streak ->
    [1] Pong!
    [2] Yes, I'm still here.
    [3] Stop it. I know you doing this for annoying me.
   *[other] I am literally ignoring you now stupid.
}
```

### Random Variants
Use the `$seed` with the modulo operator or specific ranges to provide variety:

```fluent
# personality.ftl
bot-greeting = { $seed ->
    [1] Hello there!
    [2] Hi! How can I help?
   *[other] Hey! Good to see you.
}
```

### Personality-Based Tones
Combine `$tone` and `$emotion` for deeply contextual responses:

```fluent
# errors.ftl
access-denied = { $tone ->
    [formal] I apologize, but you do not have the required permissions.
    [casual] { $emotion ->
        [annoyed] Use your brain. You can't do that.
       *[happy] Sorry! That's off-limits for you.
    }
   *[normal] You don't have permission to use this.
}
```

## Best Practices
1.  **Unique Keys**: Ensure message IDs (e.g., `ping-command`) are unique across all files within a locale, as they are merged into a single bundle during loading.
2.  **Fallback**: Always provide a default case (`*[other]`) in your selectors to prevent translation crashes.
3.  **Cross-File References**: You can reference terms or messages across files within the same locale folder.