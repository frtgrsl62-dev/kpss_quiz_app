# ===============================
# main.py
# ===============================
import streamlit as st
import time
import math
import json
import os

# ===============================
# Dosya Yolu
# ===============================
DOSYA = "kullanicilar.json"

# ===============================
# Sabit Kullanıcılar
# ===============================
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1"},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0"},
}

# ===============================
# Kullanıcıları JSON’dan Yükle
# ===============================
def kullanicilari_yukle():
    if os.path.exists(DOSYA):
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ===============================
# Kullanıcıları JSON’a Kaydet
# ===============================
def kullanicilari_kaydet():
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=2)

# ===============================
# Global Değişkenler
# ===============================
kullanicilar = kullanicilari_yukle()
sonuclar = {}

# ===============================
# Örnek soru bankası
# ===============================
from soru_bankasi import soru_bankasi  # ayrı dosyadan alınıyor

# ===============================
# Login Sayfası
# ===============================
def login_page():
    st.title("Giriş Ekranı")
    k_adi = st.text_input("Kullanıcı Adı", key="login_user")
    sifre = st.text_input("Şifre", type="password", key="login_pass")
    
    if st.button("Giriş Yap"):
        if k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            st.rerun()
        elif k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            st.rerun()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")
    
    if st.button("Kayıt Ol"):
        st.session_state["page"] = "kayit"
        st.rerun()

# ===============================
# Kayıt Sayfası
# ===============================
def kayit_page():
    st.title("Kayıt Ol")
    isim = st.text_input("İsim Soyisim", key="register_name")
    k_adi = st.text_input("Kullanıcı Adı", key="register_user")
    sifre = st.text_input("Şifre", type="password", key="register_pass")
    sifre_tekrar = st.text_input("Şifre Tekrar", type="password", key="register_pass2")
    
    if st.button("Kaydet"):
        if not isim or not k_adi or not sifre or not sifre_tekrar:
            st.error("❌ Lütfen tüm alanları doldurun!")
            return
        if sifre != sifre_tekrar:
            st.error("❌ Şifreler uyuşmuyor!")
            return
        if k_adi in kullanicilar or k_adi in sabit_kullanicilar:
            st.error("❌ Bu kullanıcı adı zaten kayıtlı!")
            return
        kullanicilar[k_adi] = {"isim": isim, "sifre": sifre}
        kullanicilari_kaydet()
        st.success(f"✅ {isim} başarıyla kaydedildi!")
        time.sleep(1)
        st.session_state["page"] = "login"
        st.rerun()

    if st.button("Geri Dön"):
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
    for konu in soru_bankasi[ders].keys():
        if st.button(konu):
            st.session_state["konu"] = konu
            st.session_state["page"] = "test"
            st.rerun()
    
    if st.button("Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

# ===============================
# Test Sayfası
# ===============================
def test_secim_page(ders, konu):
    st.header(f"{ders} - {konu} Test")
    tum_sorular = soru_bankasi[ders][konu]
    
    for i, soru in enumerate(tum_sorular, start=1):
        st.subheader(f"Soru {i}")
        st.write(soru["soru"])
        secim = st.radio("Cevap Seçin:", list(soru["secenekler"].keys()), key=f"{ders}_{konu}_{i}")
        
        if st.button("Cevapla", key=f"btn_{ders}_{konu}_{i}"):
            if secim == soru["dogru_cevap"]:
                st.success("✅ Doğru!")
            else:
                st.error(f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}")
            st.info(f"Çözüm: {soru['cozum']}")
    
    if st.button("Geri"):
        st.session_state["page"] = "konu"
        st.rerun()

# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
    st.header("Genel Rapor")
    for ders, konular in sonuclar.items():
        st.subheader(ders)
        for konu, sonuc in konular.items():
            st.write(f"{konu}: ✅ {sonuc['dogru']} | ❌ {sonuc['yanlis']}")
    
    if st.button("Ana Menü"):
        st.session_state["page"] = "ders"
        st.rerun()

# ===============================
# Router
# ===============================
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "user" not in st.session_state and st.session_state["page"] != "kayit":
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
elif st.session_state["page"] == "rapor":
    genel_rapor_page()
