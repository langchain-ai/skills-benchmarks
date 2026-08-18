# Fix: Chat Application Issues

Users are reporting problems with the chat application in `environment/chat_app.py`. The app was working fine until a recent refactor, and now users are seeing various issues:

1. **"The bot makes up answers"** - Instead of using its tools, the bot fabricates responses. Asked to search, it pretends to search. Asked to calculate, it guesses numbers.

2. **"Random crashes during responses"** - Users report `AttributeError` exceptions at random times while the bot is responding.

3. **"Progress tracking is broken"** - The `chat_with_progress` function that shows both tool execution and response tokens doesn't work properly.

4. **"Web API is unusably slow"** - The async endpoint hangs the entire web server during requests.

Please investigate and fix all the issues.
