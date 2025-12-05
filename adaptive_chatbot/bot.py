from datetime import datetime
from botbuilder.core import ActivityHandler, TurnContext, UserState
from botbuilder.schema import ChannelAccount

class UserProfile:
    def __init__(self, name: str = None, sentiment: str = "neutral"):
        self.name = name
        self.sentiment = sentiment

class MyBot(ActivityHandler):
    def __init__(self, user_state: UserState):
        self.user_state = user_state
        self.user_profile_accessor = self.user_state.create_property("UserProfile")

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        # Save any state changes that might have occurred during the turn.
        await self.user_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        profile = await self.user_profile_accessor.get(turn_context, UserProfile)
        
        text = turn_context.activity.text.strip()
        lower_text = text.lower()

        # 1. Detect Sentiment
        self._detect_sentiment(text, profile)

        # 2. Learn Name
        if lower_text.startswith("my name is"):
            parts = text.split("is")
            if len(parts) > 1:
                name = parts[1].strip()
                profile.name = name
                await turn_context.send_activity(f"Nice to meet you, {name}!")
                return # Exit to avoid double processing

        # 3. Adaptive Response Logic
        if lower_text in ["help", "capabilities", "what can you do?"]:
             await self._send_help(turn_context, profile)
        
        elif lower_text == "time":
            current_time = datetime.now().strftime("%I:%M:%S %p")
            await turn_context.send_activity(f"The current server time is: {current_time}")
            
        elif lower_text.startswith("palindrome"):
            await self._handle_palindrome(turn_context, text)
            
        elif lower_text == "error":
            # Simulate an error
            try:
                raise Exception("This is a simulated error for demonstration purposes.")
            except Exception as e:
                # Adaptation: specific error message based on sentiment could go here
                await turn_context.send_activity(f"Oops! I encountered an error: {str(e)}")
        else:
            # Echo with Adaptation
            reversed_text = text[::-1]
            response = f"You said '{text}', which backwards is '{reversed_text}'"
            
            # Incorporate Name if known
            if profile.name:
                response = f"{profile.name}, {response}"
            
            # Incorporate Sentiment
            if profile.sentiment == "happy":
                response += " (I'm glad to see you're in good spirits!)"
            elif profile.sentiment == "unhappy":
                response = f"I apologize if I am not being helpful. {response}"
            
            await turn_context.send_activity(response)

    def _detect_sentiment(self, text: str, profile: UserProfile):
        lower_text = text.lower()
        positive_keywords = ["good", "great", "happy", "awesome", "thanks", "excellent"]
        negative_keywords = ["bad", "terrible", "sad", "angry", "hate", "stupid", "error", "bug"]
        
        if any(word in lower_text for word in positive_keywords):
            profile.sentiment = "happy"
        elif any(word in lower_text for word in negative_keywords):
            profile.sentiment = "unhappy"
        # If no keywords match, keep existing sentiment or default to neutral (we keep existing to have 'memory' of mood)

    async def _send_help(self, turn_context: TurnContext, profile: UserProfile):
        intro = "I am an **Adaptive Bot**!"
        if profile.name:
            intro = f"Hi {profile.name}, {intro}"
            
        await turn_context.send_activity(
            f"{intro}\n\n"
            "I adapt to your sentiment and remember your name.\n"
            "1. **Time**: Ask 'time'.\n"
            "2. **Palindrome**: Type 'palindrome [word]'.\n"
            "3. **Name**: Tell me 'My name is [name]'.\n"
            "4. **Sentiment**: Say something 'good' or 'bad' and watch me adapt."
        )

    async def _handle_palindrome(self, turn_context: TurnContext, text: str):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            word = parts[1]
            clean_word = ''.join(c.lower() for c in word if c.isalnum())
            is_palindrome = clean_word == clean_word[::-1]
            result = "is" if is_palindrome else "is not"
            await turn_context.send_activity(f"'{word}' {result} a palindrome.")
        else:
            await turn_context.send_activity("Please provide a word to check, e.g., 'palindrome racecar'.")

    async def on_members_added_activity(
        self,
        members_added: list[ChannelAccount],
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome! Type 'help' to see what I can do.")
