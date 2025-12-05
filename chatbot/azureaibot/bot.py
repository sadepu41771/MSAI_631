from datetime import datetime
import random
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from config import DefaultConfig

class MyBot(ActivityHandler):
    def __init__(self):
        super().__init__()
        # Initialize Azure AI Text Analytics client
        self.text_analytics_client = TextAnalyticsClient(
            endpoint=DefaultConfig.AZURE_LANGUAGE_ENDPOINT,
            credential=AzureKeyCredential(DefaultConfig.AZURE_LANGUAGE_KEY)
        )

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using Azure AI"""
        try:
            response = self.text_analytics_client.analyze_sentiment(documents=[text])[0]
            return {
                "sentiment": response.sentiment,
                "positive": response.confidence_scores.positive,
                "neutral": response.confidence_scores.neutral,
                "negative": response.confidence_scores.negative
            }
        except Exception as e:
            return {"error": str(e)}

    async def extract_key_phrases(self, text: str) -> list:
        """Extract key phrases using Azure AI"""
        try:
            response = self.text_analytics_client.extract_key_phrases(documents=[text])[0]
            return response.key_phrases
        except Exception as e:
            return []

    async def detect_language(self, text: str) -> dict:
        """Detect language using Azure AI"""
        try:
            response = self.text_analytics_client.detect_language(documents=[text])[0]
            return {
                "language": response.primary_language.name,
                "iso6391_name": response.primary_language.iso6391_name,
                "confidence": response.primary_language.confidence_score
            }
        except Exception as e:
            return {"error": str(e)}

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.strip()
        lower_text = text.lower()
        
        if lower_text in ["help", "capabilities", "what can you do?"]:
            await turn_context.send_activity(
                "I am an AI-powered chatbot integrated with Azure AI Language Services!\\n\\n"
                "Here is what I can do:\\n"
                "1. **Sentiment**: Type 'sentiment' to analyze the sentiment of your next message.\\n"
                "2. **Key Phrases**: Type 'keyphrases' to extract key phrases from your message.\\n"
                "3. **Language**: Type 'language' to detect the language of your message.\\n"
                "4. **Analyze**: Type 'analyze [your text]' for full AI analysis (sentiment + key phrases).\\n"
                "5. **Time**: Ask 'time' to see the current server time.\\n"
                "6. **Palindrome**: Type 'palindrome [word]' to check if it is a palindrome.\\n"
                "7. **Reverse**: Send any other text and I'll say it backwards."
            )
        elif lower_text == "time":
            current_time = datetime.now().strftime("%I:%M:%S %p")
            await turn_context.send_activity(f"The current server time is: {current_time}")
        
        elif lower_text.startswith("analyze"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                user_text = parts[1]
                
                # Perform sentiment analysis
                sentiment_result = await self.analyze_sentiment(user_text)
                
                # Extract key phrases
                key_phrases = await self.extract_key_phrases(user_text)
                
                # Detect language
                language_result = await self.detect_language(user_text)
                
                response = f"**Azure AI Analysis Results:**\\n\\n"
                
                if "error" not in sentiment_result:
                    response += f"**Sentiment:** {sentiment_result['sentiment'].capitalize()}\\n"
                    response += f"- Positive: {sentiment_result['positive']:.2%}\\n"
                    response += f"- Neutral: {sentiment_result['neutral']:.2%}\\n"
                    response += f"- Negative: {sentiment_result['negative']:.2%}\\n\\n"
                
                if key_phrases:
                    response += f"**Key Phrases:** {', '.join(key_phrases)}\\n\\n"
                
                if "error" not in language_result:
                    response += f"**Language:** {language_result['language']} ({language_result['iso6391_name']}) "
                    response += f"[Confidence: {language_result['confidence']:.2%}]"
                
                await turn_context.send_activity(response)
            else:
                await turn_context.send_activity("Please provide text to analyze, e.g., 'analyze I love this product!'")
        
        elif lower_text == "sentiment":
            await turn_context.send_activity("Please send me a message and I'll analyze its sentiment!")
        
        elif lower_text == "keyphrases":
            await turn_context.send_activity("Please send me a message and I'll extract the key phrases!")
        
        elif lower_text == "language":
            await turn_context.send_activity("Please send me a message and I'll detect its language!")
        
        elif lower_text.startswith("palindrome"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                word = parts[1]
                clean_word = ''.join(c.lower() for c in word if c.isalnum())
                is_palindrome = clean_word == clean_word[::-1]
                result = "is" if is_palindrome else "is not"
                await turn_context.send_activity(f"'{word}' {result} a palindrome (ignoring case/symbols).")
            else:
                await turn_context.send_activity("Please provide a word to check, e.g., 'palindrome racecar'.")
        
        elif lower_text == "error":
            try:
                raise Exception("This is a simulated error for demonstration purposes.")
            except Exception as e:
                await turn_context.send_activity(f"Oops! I encountered an error: {str(e)}")
        
        else:
            # Default: Analyze sentiment and reverse text
            sentiment_result = await self.analyze_sentiment(text)
            reversed_text = text[::-1]
            
            # Sentiment-based response phrases
            sentiment_phrases = {
                "positive": [
                    "That's wonderful! 😊",
                    "I'm glad to hear such positive vibes! 🌟",
                    "Great to see you're feeling good! 👍",
                    "Love the positivity! ✨"
                ],
                "neutral": [
                    "I see, thanks for sharing.",
                    "Understood, that's quite neutral.",
                    "Got it, keeping things balanced I see.",
                    "Fair enough!"
                ],
                "negative": [
                    "I'm sorry to hear that. 😔",
                    "That sounds challenging.",
                    "I understand your frustration.",
                    "Hope things get better soon."
                ]
            }
            
            response = f"You said '{text}', which backwards is '{reversed_text}'\n\n"
            
            if "error" not in sentiment_result:
                sentiment = sentiment_result['sentiment'].lower()
                
                # Pick a random phrase based on sentiment
                sentiment_phrase = random.choice(sentiment_phrases.get(sentiment, ["Interesting!"]))
                
                response += f"**{sentiment_phrase}**\n\n"
                response += f"**Sentiment Analysis:** {sentiment_result['sentiment'].capitalize()} "
                response += f"(Positive: {sentiment_result['positive']:.0%}, "
                response += f"Neutral: {sentiment_result['neutral']:.0%}, "
                response += f"Negative: {sentiment_result['negative']:.0%})"
            
            await turn_context.send_activity(response)

    async def on_members_added_activity(
        self,
        members_added: list[ChannelAccount],
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hello and welcome! I'm now powered by Azure AI Language Services. "
                    "Type 'help' to see what I can do."
                )
