# 1. Paketleri güncelle
pkg update && pkg upgrade

# 2. Gerekli paketleri kur
pkg install python termux-api openssh wget

# 3. Python requests modülünü kur
pip install requests

# 4. Depolama izinlerini etkinleştir
termux-setup-storage

# 5. Script'i çalıştır
cd /storage/emulated/0/Download
python setup_android_agent.py