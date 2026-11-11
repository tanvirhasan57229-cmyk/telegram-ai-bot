import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# লোগ সেটআপ (কনসোল লগের জন্য)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# আপনার এপিআই কি এবং টেলিগ্রাম টোকেন এখানে বসান
# নিরাপত্তার জন্য এনভায়রনমেন্ট ভ্যারিয়েবল ব্যবহার করা সবচেয়ে ভালো
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# জেমিনি ক্লায়েন্ট ইনিশিয়ালাইজ করা
client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logging.info(f"Message from {user_name}: {user_message}")
    
    try:
        # জেমিনি মডেল থেকে রেসপন্স আনা
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        reply_text = response.text
    except Exception as e:
        reply_text = "দুঃখিত, এই মুহূর্তে এআই রেসপন্স পেতে সমস্যা হচ্ছে। একটু পরে আবার চেষ্টা করুন।"
        logging.error(f"Error generating content: {e}")
        
    # টেলিগ্রামে রিপ্লাই পাঠানো
    await update.message.reply_text(reply_text)

if __name__ == "__main__":
    # টেলিগ্রাম অ্যাপ্লিকেশন বিল্ড করা
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # টেক্সট মেসেজ হ্যান্ডলার রেজিস্টার করা
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(echo_handler)

    print("🤖 আপনার টেলিগ্রাম এআই বট সফলভাবে চালু হয়েছে এবং মেসেজের জন্য অপেক্ষা করছে...")
    
    # বট রান করার জন্য পোলিং শুরু করা (24/7 রানিংয়ের জন্য)
    application.run_polling()