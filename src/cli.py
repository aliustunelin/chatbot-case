#!/usr/bin/env python3
"""
Healthy Eating Chatbot - CLI Demo
Terminal'de interaktif sohbet deneyimi
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.utils.logger import Logger
from src.repository.openai_repository import OpenAIRepository
from src.repository.redis_repository import RedisRepository
from src.service.scoring_service import ScoringService
from src.service.chat_service import ChatService

load_dotenv()
logger = Logger.setup()


def print_banner():
    """Banner yazdır"""
    print("\n" + "="*60)
    print("   🥗 Healthy Eating Chatbot - CLI Demo")
    print("   Sağlıklı beslenme hakkında sohbet edelim!")
    print("="*60)
    print("\nKomutlar:")
    print("  'quit' veya 'q'  - Çıkış")
    print("  'score' veya 's' - Mevcut skoru göster")
    print("  'reset' veya 'r' - Konuşmayı sıfırla")
    print("-"*60 + "\n")


def print_score_details(score_result):
    """Skor detaylarını yazdır"""
    print("\n" + "="*50)
    print(f"📊 SKOR: {score_result.total_score:.1f} / {score_result.max_possible_score}")
    print("="*50)
    
    for cs in score_result.category_scores:
        bar_filled = int((cs.score / cs.max_score) * 10)
        bar_empty = 10 - bar_filled
        bar = "█" * bar_filled + "░" * bar_empty
        
        print(f"\n{cs.category}: [{bar}] {cs.score:.1f}/{cs.max_score}")
        if cs.matched_keywords:
            print(f"  Eşleşen: {', '.join(cs.matched_keywords[:5])}")
    
    print("\n" + "-"*50)
    print(score_result.evaluation_summary)
    print("="*50 + "\n")


async def main():
    """CLI ana döngüsü"""
    print_banner()
    
    # Servisleri başlat
    print("Servisler başlatılıyor...")
    openai_repo = OpenAIRepository()
    redis_repo = RedisRepository()
    scoring_service = ScoringService(openai_repo, redis_repo)
    chat_service = ChatService(openai_repo, redis_repo, scoring_service)
    
    try:
        await chat_service.initialize()
        print("✅ Servisler hazır!\n")
        
        # Konuşmayı başlat
        print("🤖 Bot:")
        response = await chat_service.start_conversation()
        print(f"   {response.response}\n")
        
        conversation_id = response.conversation_id
        
        # Ana döngü
        while True:
            try:
                user_input = input("👤 Sen: ").strip()
                
                if not user_input:
                    continue
                
                # Komutları kontrol et
                if user_input.lower() in ['quit', 'q', 'exit']:
                    print("\n👋 Görüşmek üzere! Sağlıklı kalın!")
                    break
                
                if user_input.lower() in ['score', 's']:
                    score_result = await chat_service.get_score(conversation_id)
                    print_score_details(score_result)
                    continue
                
                if user_input.lower() in ['reset', 'r']:
                    await chat_service.reset_conversation(conversation_id)
                    print("\n🔄 Konuşma sıfırlandı. Yeni konuşma başlatılıyor...\n")
                    response = await chat_service.start_conversation()
                    conversation_id = response.conversation_id
                    print(f"🤖 Bot:\n   {response.response}\n")
                    continue
                
                # Mesaj gönder
                response = await chat_service.send_message(conversation_id, user_input)
                print(f"\n🤖 Bot:")
                print(f"   {response.response}")
                print(f"   [Skor: {response.current_score:.1f}/100]\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Görüşmek üzere!")
                break
            except Exception as e:
                print(f"\n❌ Hata: {e}\n")
                logger.error(f"CLI error: {e}")
    
    finally:
        # Cleanup
        await chat_service.close()
        print("\n✅ Bağlantılar kapatıldı.")


if __name__ == "__main__":
    asyncio.run(main())

