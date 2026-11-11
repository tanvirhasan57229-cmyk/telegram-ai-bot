import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# লগিং সেটআপ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# আপনার এপিআই কি এবং টেলিগ্রাম টোকেন এখানে বসান
TELEGRAM_BOT_TOKEN = "9165091984:AAFwaMnBZ952o4Ncq4cvtVwIsP2OnLpJI6g"
GEMINI_API_KEY = "AQ.Ab8RN6KOfBZQDE53k1heoI1RO-fuQ95pLaytvb3ZJbQIlaw5CA"

# জেমিনি ক্লায়েন্ট ইনিশিয়ালাইজ করা
client = genai.Client(api_key=GEMINI_API_KEY)

# ১. ছবি বা ফটো হ্যান্ডেল করার ফাংশন (Gemini Vision)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    logging.info(f"Photo received from {user_name}")
    
    # টেলিগ্রাম থেকে ছবির ক্যাপশন নেওয়া (যদি থাকে)
    caption = update.message.caption or "এই ছবিটি বর্ণনা করুন এবং বিশ্লেষণ করুন।"
    
    status_message = await update.message.reply_text("🖼️ ছবিটি প্রসেস করা হচ্ছে, একটু অপেক্ষা করুন...")

    try:
        # টেলিগ্রাম সার্ভার থেকে হাই-কোয়ালিটি ফটো ফাইল ডাউনলোড করা
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # জেমিনি মাল্টিমোডাল মডেলের মাধ্যমে ইমেজ প্রসেস করা
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                caption,
                {
                    'inline_data': {
                        'data': bytes(image_bytes),
                        'mime_type': 'image/jpeg'
                    }
                }
            ]
        )
        reply_text = response.text
    except Exception as e:
        reply_text = f"দুঃখিত, ছবিটি প্রসেস করার সময় একটি সমস্যা হয়েছে: {e}"
        logging.error(f"Vision Error: {e}")

    await status_message.edit_text(reply_text)


# ২. ভয়েস বা অডিও মেসেজ হ্যান্ডেল করার ফাংশন (Gemini Audio)
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    logging.info(f"Voice message received from {user_name}")
    
    status_message = await update.message.reply_text("🎙️ ভয়েস মেসেজটি প্রসেস করা হচ্ছে...")

    try:
        # টেলিগ্রাম থেকে ভয়েস ফাইল ডাউনলোড করা (.ogg ফরম্যাট)
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # জেমিনি মডেলের কাছে অডিও ফাইল পাঠানো (ট্রান্সক্রিপশন বা উত্তরের জন্য)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                "এই ভয়েস মেসেজটিতে কী বলা হয়েছে তা শুনুন, বাংলায় এর ট্রান্সক্রিপশন দিন এবং এর যথাযথ উত্তর দিন।",
                {
                    'inline_data': {
                        'data': bytes(voice_bytes),
                        'mime_type': 'audio/ogg'
                    }
                }
            ]
        )
        reply_text = response.text
    except Exception as e:
        reply_text = f"দুঃখিত, ভয়েস মেসেজটি প্রসেস করার সময় সমস্যা হয়েছে: {e}"
        logging.error(f"Audio Error: {e}")

    await status_message.edit_text(reply_text)


if __name__ == "__main__":
    # টেলিগ্রাম অ্যাপ্লিকেশন বিল্ড করা
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # ফটো এবং ভয়েস হ্যান্ডলার রেজিস্টার করা
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("🤖 মিডিয়া ও ভয়েস সাপোর্টেড টেলিগ্রাম বট চালু হয়েছে...")
    
    # বট রান করা
    application.run_polling()