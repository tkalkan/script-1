#!/usr/bin/env python3
"""
Lenovo Android Tablet Otomatik Kurulum Script'i
Bu script, istanbul-print-agent.py'yi ve web sayfasını otomatik başlatır.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command):
    """Shell komutunu çalıştır"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_termux():
    """Termux'un kurulu olup olmadığını kontrol et"""
    success, stdout, stderr = run_command("pkg list-installed termux-api")
    return success

def install_termux_packages():
    """Gerekli paketleri kur"""
    print("📦 Gerekli paketler kuruluyor...")
    
    # Önce pkg repository'sini güncelle
    run_command("pkg update -y")
    
    packages = [
        "termux-api",
        "python",
        "openssh",
        "wget"
    ]
    
    for package in packages:
        print(f"Kuruluyor: {package}")
        success, stdout, stderr = run_command(f"pkg install -y {package}")
        if not success:
            print(f"❌ {package} kurulumu başarısız: {stderr}")
            return False
    
    # Python paketlerini kur
    print("Kuruluyor: Python requests modülü")
    success, stdout, stderr = run_command("pip install requests")
    if not success:
        print(f"⚠️  requests kurulumu başarısız, urllib kullanılacak: {stderr}")
    
    print("✅ Tüm paketler başarıyla kuruldu")
    return True

def setup_boot_directory():
    """Boot dizinini oluştur"""
    boot_dir = Path.home() / ".termux" / "boot"
    boot_dir.mkdir(parents=True, exist_ok=True)
    return boot_dir

def create_startup_script(agent_path, web_url):
    """Başlangıç script'ini oluştur"""
    boot_script = """#!/data/data/com.termux/files/usr/bin/bash

# CPU uyku modunu engelle
termux-wake-lock

# Pil optimizasyonunu atlamak için bildirim
termux-notification -t "Agent Çalışıyor" -c "Sistem aktif, web sayfası açılıyor..."

# Web sayfasını aç
sleep 5
termux-open-url "{web_url}"

# Agent'ı başlat
sleep 10
cd "{agent_dir}"
python "{agent_file}" &

# Agent'ın çalıştığını kontrol et
while true; do
    if pgrep -f "{agent_file}" > /dev/null; then
        echo "Agent çalışıyor..."
    else
        echo "Agent yeniden başlatılıyor..."
        python "{agent_file}" &
    fi
    sleep 30
done
""".format(
        web_url=web_url,
        agent_dir=str(agent_path.parent),
        agent_file=agent_path.name
    )
    
    return boot_script

def setup_storage_permissions():
    """Depolama izinlerini ayarla"""
    print("🔐 Depolama izinleri ayarlanıyor...")
    run_command("termux-setup-storage")
    time.sleep(3)

def disable_battery_optimization():
    """Pil optimizasyonunu devre dışı bırak"""
    print("🔋 Pil optimizasyonu devre dışı bırakılıyor...")
    
    # Termux için pil optimizasyonunu kapat
    run_command("termux-battery-optimization -ignore")
    
    # Gerekli komutlar
    commands = [
        "dumpsys deviceidle whitelist +com.termux",
        "dumpsys deviceidle enable false",
        "settings put global app_standby_enabled 0"
    ]
    
    for cmd in commands:
        run_command(cmd)

def copy_agent_to_home():
    """Agent dosyasını home dizinine kopyala"""
    download_path = "/storage/emulated/0/Download/istanbul-print-agent.py"
    home_path = Path.home() / "istanbul-print-agent.py"
    
    if os.path.exists(download_path):
        print("📄 Agent dosyası kopyalanıyor...")
        try:
            with open(download_path, 'r', encoding='utf-8') as src:
                content = src.read()
            with open(home_path, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            # Çalıştırma izni ver
            run_command(f"chmod +x {home_path}")
            print(f"✅ Agent kopyalandı: {home_path}")
            return home_path
        except Exception as e:
            print(f"❌ Kopyalama hatası: {e}")
            return None
    else:
        print("❌ İndirilenler klasöründe istanbul-print-agent.py bulunamadı!")
        print(f"Aranan yol: {download_path}")
        return None

def create_launcher_script(agent_path, web_url):
    """Hızlı başlatma script'i oluştur"""
    launcher_script = Path.home() / "start-agent.sh"
    
    script_content = f"""#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Agent ve Web Sayfası Başlatılıyor..."

# Web sayfasını aç
termux-open-url "{web_url}"

# Agent'ı başlat
cd {agent_path.parent}
python {agent_path.name} &

echo "✅ Sistem başlatıldı!"
echo "Web Sayfası: {web_url}"
echo "Agent: {agent_path.name}"
"""

    with open(launcher_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    run_command(f"chmod +x {launcher_script}")
    print(f"✅ Hızlı başlatma script'i oluşturuldu: {launcher_script}")

def check_android_environment():
    """Android ortamını kontrol et"""
    print("🔍 Ortam kontrol ediliyor...")
    
    # Termux kontrolü
    if not os.path.exists("/data/data/com.termux/files/usr/bin/bash"):
        print("❌ Termux bulunamadı!")
        return False
    
    print("✅ Termux ortamı tespit edildi")
    return True

def main():
    """Ana kurulum fonksiyonu"""
    print("=" * 50)
    print("🤖 Lenovo Android Tablet Kurulumu")
    print("=" * 50)
    
    # Web sayfası URL'si
    web_url = "https://digitalmenu.hilfex.com/siparis"
    
    # Android ortam kontrolü
    if not check_android_environment():
        print("❌ Bu script sadece Termux ortamında çalıştırılabilir!")
        print("Lütfen önce Termux uygulamasını kurun:")
        print("https://f-droid.org/en/packages/com.termux/")
        sys.exit(1)
    
    # Termux kontrolü
    if not check_termux():
        print("❌ Termux API bulunamadı!")
        print("Termux API paketini kuruyorum...")
    
    # Paketleri kur
    if not install_termux_packages():
        print("❌ Paket kurulumu başarısız!")
        sys.exit(1)
    
    # Depolama izinleri
    setup_storage_permissions()
    
    # Agent'ı kopyala
    agent_path = copy_agent_to_home()
    if not agent_path:
        print("❌ Agent dosyası bulunamadı!")
        print("Lütfen 'istanbul-print-agent.py' dosyasını İndirilenler klasörüne koyun.")
        sys.exit(1)
    
    # Boot dizinini oluştur
    boot_dir = setup_boot_directory()
    
    # Başlangıç script'ini oluştur
    boot_script_path = boot_dir / "00-start-agent"
    boot_script_content = create_startup_script(agent_path, web_url)
    
    with open(boot_script_path, 'w', encoding='utf-8') as f:
        f.write(boot_script_content)
    
    run_command(f"chmod +x {boot_script_path}")
    print(f"✅ Başlangıç script'i oluşturuldu: {boot_script_path}")
    
    # Hızlı başlatma script'i
    create_launcher_script(agent_path, web_url)
    
    # Pil optimizasyonu
    disable_battery_optimization()
    
    print("\n" + "=" * 50)
    print("🎉 KURULUM TAMAMLANDI!")
    print("=" * 50)
    print("\n📋 Yapılan ayarlar:")
    print("  ✅ Termux paketleri kuruldu")
    print("  ✅ Agent dosyası kopyalandı")
    print("  ✅ Başlangıç script'i oluşturuldu")
    print("  ✅ Web sayfası ayarlandı")
    print("  ✅ Pil optimizasyonu devre dışı")
    print(f"  ✅ Hızlı başlatma script'i oluşturuldu")
    
    print("\n🔧 Son adımlar:")
    print("  1. F-Droid'den 'Termux:Boot' uygulamasını kurun")
    print("  2. 'Termux:Boot' uygulamasını bir kere açın")
    print("  3. Tableti yeniden başlatın")
    print("  4. Sistem otomatik başlayacaktır")
    
    print(f"\n🚀 Manuel başlatmak için:")
    print(f"   ./start-agent.sh")
    
    print("\n📞 Sorun giderme:")
    print("   - Pil optimizasyonunu kontrol edin")
    print("   - Termux:Boot'un çalıştığından emin olun")
    print("   - Depolama izinlerini kontrol edin")

if __name__ == "__main__":
    main()