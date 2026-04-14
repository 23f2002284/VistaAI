import asyncio
import edge_tts
import os

async def main():
    if not os.path.exists("frontend/public"):
        os.makedirs("frontend/public")
        
    await edge_tts.Communicate("Hi, I am Kore. Your warm and friendly property assistant.", "en-US-AriaNeural").save("frontend/public/kore.mp3")
    await edge_tts.Communicate("Hello, I am Puck. Your sharp, professional architectural guide.", "en-GB-RyanNeural").save("frontend/public/puck.mp3")
    await edge_tts.Communicate("Greetings, I am Aoede. Experience a soft, calm narrative tone.", "en-US-JennyNeural").save("frontend/public/aoede.mp3")

if __name__ == "__main__":
    asyncio.run(main())
