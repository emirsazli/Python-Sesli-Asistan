import random
import time
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import os
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# Kategorileri eşleştiren bir sözlük
kategori_mapping = {
    "aksiyon": "aksiyon",
    "belgesel": "belgeseller",
    "bilim kurgu": "bilim-kurgu-filmleri",
    "dram": "dram-filmleri",
    "fantastik": "fantastik-filmler",
    "gerilim": "gerilim",
    "gizem": "gizem-fimleri",
    "Hint": "hd-hint-filmleri",
    "kısa film": "kısa-film",
    "komedi": "hd-komedi-filmleri",
    "korku": "korku-fimleri",
    "Kült": "kult-filmler-izle",
    "macera": "macera-fimleri",
    "Oscar Ödüllü": "odullu-fimler-izle",
    "Romantik": "romantik-filmler",
    "gizem filmi": "gizem-filmleri",
    "ödüllü": "odullu-filmler-izle",
    "4k": "4k-film-izle",
    "aile": "aile-filmleri",
    "animasyon": "animasyon",
}

class SesliAsistan:
    def __init__(self):
        self.seslendirme("Ben SeamChat, nasıl yardımcı olabilirim?")
        self.r = sr.Recognizer()
        self.is_running = True
        self.volume_level = 100
        self.current_browser = None

    def seslendirme(self, metin):
        xtts = gTTS(text=metin, lang="tr")
        dosya = "ses_" + str(random.randint(1000, 9999)) + ".mp3"
        xtts.save(dosya)

        try:
            playsound(dosya)
        except Exception as e:
            print(f"Ses dosyası oynatılırken hata: {e}")
        finally:
            time.sleep(1)
            try:
                os.remove(dosya)
            except Exception as e:
                print(f"Dosya silme hatası: {e}")

    def ses_kayit(self):
        with sr.Microphone() as kaynak:
            print("Sizi dinliyorum..")
            listen = self.r.listen(kaynak)
            voice = ""

            try:
                voice = self.r.recognize_google(listen, language="tr-TR")
                print(f"Algılanan ses: {voice}")
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                self.seslendirme("Ses hizmetine bağlanırken hata oluştu.")
                return None

            return voice

    def sağlam_tarayıcı_olustur(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            )
            tarayici = webdriver.Chrome(options=chrome_options)
            return tarayici
        except Exception as e:
            self.seslendirme("Tarayıcı başlatılamadı.")
            print(f"Tarayıcı hatası: {e}")
            return None

    def ses_control(self, miktar):
        if miktar == 0:
            pyautogui.press('volumedown', presses=10)  # Ses kapalı
        elif miktar == 100:
            pyautogui.press('volumeup', presses=10)  # Ses aç
        elif miktar < 0:
            pyautogui.press('volumedown', presses=10)  # Ses kıs
        elif miktar > 0:
            pyautogui.press('volumeup', presses=10)  # Ses aç

    def ses_karsilik(self, gelen_ses):
        if "selam" in gelen_ses:
            self.seslendirme("Size de selamlar, nasıl yardımcı olabilirim?")
        elif "merhaba" in gelen_ses:
            self.seslendirme("Size de Merhaba, nasıl yardımcı olabilirim?")
        elif "teşekkür ederim" in gelen_ses:
            self.seslendirme("Rica ederim.")
        elif "çıkış" in gelen_ses or "kapat" in gelen_ses:
            self.seslendirme("Görüşmek üzere!")
            self.is_running = False
            exit(0)
        elif "geç" in gelen_ses:
            self.seslendirme("Bir sonraki sayfaya geçiyorum...")
            pyautogui.press("right")
        elif "geri gel" in gelen_ses:
            self.seslendirme("Bir önceki sayfaya geri dönüyorum...")
            pyautogui.press("left")

        elif "video aç" in gelen_ses or "müzik aç" in gelen_ses or "youtube aç" in gelen_ses:
            self.seslendirme("Ne açmamı istersiniz?")
            veri = self.ses_kayit()
            if veri:
                self.seslendirme(f"{veri} açılıyor....")
                url = f"https://www.youtube.com/results?search_query={veri}"
                tarayici = self.sağlam_tarayıcı_olustur()
                tarayici.get(url)
                try:
                    WebDriverWait(tarayici, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='video-title']"))
                    ).click()
                except Exception:
                    self.seslendirme("Videoyu açarken bir hata oluştu.")

        elif "google aç" in gelen_ses or "arama yap" in gelen_ses:
            self.seslendirme("Ne aramamı istersiniz?")
            veri = self.ses_kayit()
            if veri:
                self.seslendirme(f"{veri} için bulduklarım bunlar.")
                url = f"https://www.google.com/search?q={veri}"
                tarayici = self.sağlam_tarayıcı_olustur()
                tarayici.get(url)

        elif "film aç" in gelen_ses:
            self.seslendirme("Hangi filmi açmamı istersiniz?")
            veri = self.ses_kayit()
            self.seslendirme(f"{veri} filmini açıyorum.")
            url = "https://www.google.com/search?q={}+izle".format(veri)
            tarayici = webdriver.Chrome()
            tarayici.get(url)

            try:
                WebDriverWait(tarayici, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='rso']/div[2]/div/div[1]/div/span/a/h3"))
                ).click()
            except Exception:
                self.seslendirme("Film açılırken bir hata oluştu.")

        elif "film önerisi yap" in gelen_ses:
            self.seslendirme("Hangi tür film istersiniz?")
            veri = self.ses_kayit()

            if veri:
                kategori_adı = veri.lower().strip()

                kategori_adı = self.kategori_eslestir(kategori_adı)

                if kategori_adı:
                    url_ek = kategori_mapping[kategori_adı]
                    url = f"https://www.filmmodu.tv/hd-film-kategori/{url_ek}"
                    self.seslendirme(f"{veri} için bulduklarım bunlar.")
                    tarayici = self.sağlam_tarayıcı_olustur()
                    if tarayici:
                        tarayici.get(url)
                        self.seslendirme(
                            "Eğer kararsızsanız size film önerisi yapabilirim. Evet veya hayır demeniz yeterli.")

                        cevap = self.ses_kayit()
                        if "evet" in cevap.lower():
                            self.seslendirme("Hemen size bir film öneriyorum.")
                            rastgele_sayi = random.randint(1, 24)
                            try:
                                buton = tarayici.find_element(By.XPATH,
                                                              f"/html/body/main/div[2]/div[{rastgele_sayi}]/div/a")
                                buton.click()
                                self.seslendirme("Keyifli seyirler.")
                            except Exception:
                                self.seslendirme("Film açılırken bir hata oluştu.")
                        else:
                            self.seslendirme("Keyifli seyirler.")
                else:
                    self.seslendirme("Bu kategori bulunamadı. Lütfen farklı bir kategori deneyin.")

        elif "ses aç" in gelen_ses or "ses arttır" in gelen_ses:
            self.seslendirme("Ses açılıyor.")
            self.ses_control(1)

        elif "ses kıs" in gelen_ses or "sesi kıs" in gelen_ses or "sesi azalt" in gelen_ses:
                self.seslendirme("Ses kısılıyor.")
                self.ses_control(-10)

        elif "sesi sıfırla" in gelen_ses:
            self.seslendirme("Ses kapatılıyor.")
            self.ses_control(0)

        elif "tam ekran" in gelen_ses:
            pyautogui.hotkey('f11')
            self.seslendirme("Tam ekran modu etkinleştirildi.")

    def kategori_eslestir(self, kategori_adı):
        for key in kategori_mapping:
            if key in kategori_adı:
                return key
        return None

    def dinle(self):
        while self.is_running:
            ses = self.ses_kayit()
            if ses:
                ses = ses.lower()
                self.ses_karsilik(ses)


# Asistanı başlat
asistan = SesliAsistan()

# Asistanı dinlemeye başlat
dinle_thread = threading.Thread(target=asistan.dinle)
dinle_thread.start()
