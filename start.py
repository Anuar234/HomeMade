#!/usr/bin/env python3
"""
Универсальный скрипт запуска Home Food Abu Dhabi
Запускает API и Telegram Bot одновременно
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.OKGREEN):
    """Печать цветного текста"""
    print(f"{color}{text}{Colors.ENDC}")

def check_env():
    """Проверка наличия .env файла"""
    if not Path('.env').exists():
        print_colored("⚠️  ВНИМАНИЕ: Файл .env не найден!", Colors.WARNING)
        print_colored("Создайте .env файл на основе .env.example", Colors.WARNING)
        
        if Path('.env.example').exists():
            response = input("\n❓ Создать .env из .env.example? (y/n): ")
            if response.lower() == 'y':
                import shutil
                shutil.copy('.env.example', '.env')
                print_colored("✅ Файл .env создан!", Colors.OKGREEN)
                print_colored("⚠️  Не забудьте отредактировать .env с вашими настройками!", Colors.WARNING)
                return False
        return False
    return True

def check_database():
    """Проверка наличия базы данных"""
    if not Path('homefood.db').exists():
        print_colored("ℹ️  База данных не найдена, будет создана автоматически", Colors.OKCYAN)
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    required = ['fastapi', 'uvicorn', 'telegram']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_colored(f"❌ Не установлены зависимости: {', '.join(missing)}", Colors.FAIL)
        print_colored("Запустите: pip install -r requirements.txt", Colors.WARNING)
        return False
    return True

def print_banner():
    """Вывод баннера"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║   🍽️  Home Food Abu Dhabi           ║
    ║   Платформа домашней еды             ║
    ╚═══════════════════════════════════════╝
    """
    print_colored(banner, Colors.HEADER)

def print_info():
    """Информация о запуске"""
    info = """
    📱 API: http://localhost:8000
    📄 Docs: http://localhost:8000/docs
    🤖 Telegram Bot: Запущен
    📊 Database: homefood.db
    
    Команды:
    - Ctrl+C для остановки
    """
    print_colored(info, Colors.OKCYAN)

def start_services():
    """Запуск сервисов"""
    processes = []
    
    try:
        # Запуск API
        print_colored("\n🚀 Запуск API сервера...", Colors.OKGREEN)
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("API", api_process))
        time.sleep(2)  # Даем время API запуститься
        
        # Запуск Telegram Bot
        print_colored("🤖 Запуск Telegram бота...", Colors.OKGREEN)
        bot_process = subprocess.Popen(
            [sys.executable, "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Bot", bot_process))
        time.sleep(1)
        
        print_colored("\n✅ Все сервисы запущены!", Colors.OKGREEN)
        print_info()
        
        # Мониторинг процессов
        print_colored("📡 Мониторинг сервисов (Ctrl+C для остановки)...\n", Colors.OKCYAN)
        
        while True:
            for name, process in processes:
                if process.poll() is not None:
                    print_colored(f"❌ {name} остановлен с кодом {process.returncode}", Colors.FAIL)
                    # Читаем ошибки
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    if stderr:
                        print_colored(f"Ошибка:\n{stderr}", Colors.FAIL)
                    raise Exception(f"{name} crashed")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print_colored("\n\n⏹️  Остановка сервисов...", Colors.WARNING)
        for name, process in processes:
            print_colored(f"   Остановка {name}...", Colors.WARNING)
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print_colored("✅ Все сервисы остановлены", Colors.OKGREEN)
        
    except Exception as e:
        print_colored(f"\n❌ Ошибка: {e}", Colors.FAIL)
        for name, process in processes:
            process.terminate()
        sys.exit(1)

def main():
    """Главная функция"""
    print_banner()
    
    print_colored("🔍 Проверка системы...", Colors.OKCYAN)
    
    # Проверки
    if not check_dependencies():
        sys.exit(1)
    
    if not check_env():
        print_colored("\n❌ Настройте .env файл и запустите снова", Colors.FAIL)
        sys.exit(1)
    
    check_database()
    
    print_colored("✅ Все проверки пройдены!\n", Colors.OKGREEN)
    
    # Запуск
    try:
        start_services()
    except Exception as e:
        print_colored(f"\n❌ Критическая ошибка: {e}", Colors.FAIL)
        sys.exit(1)

if __name__ == "__main__":
    main()