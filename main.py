import streamlit as st
import time
import json
import os
import math
from soru_bankasi import soru_bankasi  # Soru bankası ayrı dosyada

# ===============================
# Dosya yolu
# ===============================
DOSYA = "kullanicilar.json"

# ===============================
# Sabit kullanıcılar
# ===============================
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1"},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0"},
}

# ===============================
# Kullanıcı yükle / oluştur
# ===============================
def kullanicilari_yukle():
    if not os.path.exists(DOSYA):
        with open(DOSYA, "w", encoding="utf-8") as f:
            f.write("{}")
    with open(DOSYA, "r", encoding="utf-8") as f:
        return json.load(f)

def kullanicilari_kaydet():
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=2)

# ===============================
# Global değişkenler
# ===============================
kullanicilar = kullanicilari_yukle()
sonuclar = {}

# ===============================
# Login Sayfası
# ===============================
def login_page():
    st.title("Giriş Ekranı")
    with st.form("login_form"):
        k_adi = st.text_input("Kullanıcı Adı", key="login_user")
        sifre = st.text_input("Şifre", type="password", key="login_pass")
        giris_btn = st.form_submit_button("Giriş Yap")
        kayit_btn = st.form_submit_button("Kayıt Ol")

    if giris_btn:
        if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
           (k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre):
            st.session_state["user"] = k_adi
            st.session_state["page"] = "ders"
            st.rerun()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")

    if kayit_btn:
        st.session_state["page"] = "kayit"
        st.rerun()

# ===============================
# Kayıt Sayfası
# ===============================
def kayit_page():
    st.title("Kayıt Ol")
    with st.form("kayit_form"):
        isim = st.text_input("İsim Soyisim", key="register_name")
        k_adi = st.text_input("Kullanıcı Adı", key="register_user")
        sifre = st.text_input("Şifre", type="password", key="register_pass")
        sifre_tekrar = st.text_input("Şifre Tekrar", type="password", key="register_pass2")
        kaydet_btn = st.form_submit_button("Kaydet")
        geri_btn = st.form_submit_button("Geri Dön")

    if kaydet_btn:
        if not isim or not k_adi or not sifre or not sifre_tekrar:
            st.error("❌ Lütfen tüm alanları doldurun!")
            return
        if sifre != sifre_tekrar:
            st.error("❌ Şifreler uyuşmuyor!")
            return
        if k_adi in sabit_kullanicilar or k_adi in kullanicilar:
            st.error("❌ Bu kullanıcı adı zaten kayıtlı!")
            return
        kullanicilar[k_adi] = {"isim": isim, "sifre": sifre}
        kullanicilari_kaydet()
        st.success(f"✅ {isim} başarıyla kaydedildi!")
        time.sleep(1)
        st.session_state["page"] = "login"
        st.rerun()

    if geri_btn:
        st.session_state["page"] = "login"
        st.rerun()

# ===============================
# Ders Seçim Sayfası
# ===============================
def ders_secim_page():
    st.title("Ders Seçiniz")
    for ders in soru_bankasi.keys():
        if st.button(ders):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.rerun()
    if st.button("Genel Raporu Gör"):
        st.session_state["page"] = "rapor"
        st.rerun()
    if st.button("Çıkış Yap"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()

# ===============================
# Konu Seçim Sayfası
# ===============================
def konu_secim_page(ders):
    st.header(f"{ders} - Konu Seçimi")
    konular = list(soru_bankasi[ders].keys())
    for konu in konular:
        if st.button(f"→ {konu}", key=f"konu_{konu}"):
            st.session_state["konu"] = konu
            st.session_state["page"] = "test"
            st.rerun()
    if st.button("Geri"):
        st.session_state["page"] = "ders"
        st.rerun()



# ===============================
# Test Seçim Sayfası
# ===============================
def test_secim_page(secilen_ders, secilen_konu):
    st.header(f"{secilen_ders} - {secilen_konu} Test Seçimi")
    tum_sorular = soru_bankasi[secilen_ders][secilen_konu]
    if not tum_sorular:
        st.info("Bu konu için henüz soru eklenmemiş.")
        if st.button("Geri"):
            st.session_state["page"] = "konu"
            st.rerun()
        return

    soru_grubu_sayisi = 10
    test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)

    for i in range(test_sayisi):
        baslangic = i * soru_grubu_sayisi
        bitis = min((i + 1) * soru_grubu_sayisi, len(tum_sorular))
        test_adi = f"Test {i+1}: Soru {baslangic+1}-{bitis}"

        if st.button(test_adi, key=f"testbtn_{i}"):
            st.session_state["current_test"] = {
                "test": tum_sorular[baslangic:bitis],
                "index": 0,
                "ders": secilen_ders,
                "konu": secilen_konu,
                "test_no": i+1,
                "test_sayisi": test_sayisi
            }
            st.session_state["page"] = "soru"
            st.rerun()

    if st.button("Geri"):
        st.session_state["page"] = "konu"
        st.rerun()

# ===============================
# Soru Gösterim Sayfası
# ===============================
import streamlit as st
import json
import random
from soru_bankasi import soru_bankasi

# Kullanıcıları yükle
def load_users():
    try:
        with open("kullanicilar.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("kullanicilar.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# Kullanıcı oturumu
if "page" not in st.session_state:
    st.session_state.page = "menu"
if "ders" not in st.session_state:
    st.session_state.ders = None
if "konu" not in st.session_state:
    st.session_state.konu = None
if "soru_index" not in st.session_state:
    st.session_state.soru_index = 0
if "sorular" not in st.session_state:
    st.session_state.sorular = []
if "cevaplar" not in st.session_state:
    st.session_state.cevaplar = []

# Ana menü
if st.session_state.page == "menu":
    st.title("KPSS Quiz Uygulaması")
    dersler = list(soru_bankasi.keys())
    secilen_ders = st.selectbox("Ders Seçiniz", dersler)

    if secilen_ders:
        konular = list(soru_bankasi[secilen_ders].keys())
        secilen_konu = st.selectbox("Konu Seçiniz", konular)

        if st.button("Teste Başla"):
            st.session_state.ders = secilen_ders
            st.session_state.konu = secilen_konu
            st.session_state.sorular = soru_bankasi[secilen_ders][secilen_konu]
            st.session_state.soru_index = 0
            st.session_state.cevaplar = [None] * len(st.session_state.sorular)
            st.session_state.page = "quiz"
            st.rerun()

# Quiz ekranı
elif st.session_state.page == "quiz":
    sorular = st.session_state.sorular
    soru_index = st.session_state.soru_index
    soru = sorular[soru_index]

    st.subheader(f"Soru {soru_index+1}/{len(sorular)}")
    st.write(soru["soru"])

    secenekler = soru["secenekler"]
    cevap = st.radio("Şıklar", secenekler, index=None, key=f"cevap_{soru_index}")

    if st.button("Cevabı Göster"):
        dogru = soru["cevap"]
        st.success(f"Doğru Cevap: {dogru}")
        if "cozum" in soru:
            st.info(f"Çözüm: {soru['cozum']}")

    # Butonlar için iki kolon
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Geri", type="secondary", key=f"geri_{soru_index}"):
            if st.session_state.soru_index > 0:
                st.session_state.soru_index -= 1
                st.rerun()
            else:
                st.session_state.page = "menu"
                st.rerun()

    with col2:
        if soru_index < len(sorular) - 1:
            if st.button("Sonraki Soru ➡️", key=f"sonraki_{soru_index}"):
                st.session_state.soru_index += 1
                st.rerun()
        else:
            # Test bitti
            if st.button("Sonraki Test ➡️", key="next_test"):
                # Konu içinde başka test mantığı buraya eklenebilir
                st.session_state.page = "menu"
                st.rerun()

            if st.button("🏠 Ana Menü", key="main_menu"):
                st.session_state.page = "menu"
                st.rerun()




# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
    st.header("Genel Rapor")
    if not sonuclar:
        st.info("Henüz herhangi bir test çözülmedi.")
    for ders, konular in sonuclar.items():
        st.subheader(ders)
        for konu, sonuc in konular.items():
            if isinstance(sonuc, dict) and "dogru" in sonuc:
                st.markdown(f"{konu}: ✅ {sonuc['dogru']} | ❌ {sonuc['yanlis']}")

    if st.button("Ana Menü"):
        st.session_state["page"] = "ders"
        st.rerun()

# ===============================
# Router
# ===============================
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "kayit":
    kayit_page()
elif st.session_state["page"] == "ders":
    ders_secim_page()
elif st.session_state["page"] == "konu":
    konu_secim_page(st.session_state["ders"])
elif st.session_state["page"] == "test":
    test_secim_page(st.session_state["ders"], st.session_state["konu"])
elif st.session_state["page"] == "soru":
    soru_goster_page()
elif st.session_state["page"] == "rapor":
    genel_rapor_page()













