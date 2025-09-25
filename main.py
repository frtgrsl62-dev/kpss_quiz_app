import streamlit as st
import time
import json
import os
import math
import uuid
from soru_bankasi import soru_bankasi  # Soru bankası ayrı dosyada

# ===============================
# Dosya yolları
# ===============================
DOSYA = "kullanicilar.json"
AKTIF_DOSYA = "aktif_kullanicilar.json"  # çoklu cihaz desteği

# ===============================
# Sabit kullanıcılar
# ===============================
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1"},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0"},
}

# ===============================
# Kullanıcı yükle / kaydet
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
# Aktif kullanıcı dosyası (çoklu cihaz için)
# ===============================
def aktif_kullanicilar_yukle():
    if not os.path.exists(AKTIF_DOSYA):
        with open(AKTIF_DOSYA, "w", encoding="utf-8") as f:
            f.write("{}")
    with open(AKTIF_DOSYA, "r", encoding="utf-8") as f:
        return json.load(f)

def aktif_kullanicilar_kaydet(data):
    with open(AKTIF_DOSYA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def aktif_kullanici_ekle(user, session_id):
    aktifler = aktif_kullanicilar_yukle()
    aktifler[session_id] = {"user": user, "time": time.time()}
    aktif_kullanicilar_kaydet(aktifler)

def aktif_kullanici_sil(session_id):
    aktifler = aktif_kullanicilar_yukle()
    if session_id in aktifler:
        del aktifler[session_id]
        aktif_kullanicilar_kaydet(aktifler)

# ===============================
# Sonuçları kullanıcıya kaydet
# ===============================
def kaydet_sonuclar_to_user(user):
    if user not in kullanicilar:
        return
    kullanicilar[user]["sonuclar"] = st.session_state.get("sonuclar", {})
    kullanicilari_kaydet()

def kullanici_sonuclarini_yukle_to_session(user):
    if user in kullanicilar and "sonuclar" in kullanicilar[user]:
        st.session_state["sonuclar"] = kullanicilar[user]["sonuclar"]

# ===============================
# Global değişkenler
# ===============================
kullanicilar = kullanicilari_yukle()

# ===============================
# Login Sayfası
# ===============================
def login_page():
    st.markdown("<h1 style='text-align: center; color: orange;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<h1>Giriş Ekranı</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        k_adi = st.text_input("Kullanıcı Adı", key="login_user")
        sifre = st.text_input("Şifre", type="password", key="login_pass")
        giris_btn = st.form_submit_button("🟢 Giriş Yap 🟢")
        kayit_btn = st.form_submit_button("🔹 Kayıt Ol 🔹")

    if giris_btn:
        if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
           (k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre):
            st.session_state["current_user"] = k_adi
            if "session_id" not in st.session_state:
                st.session_state["session_id"] = str(uuid.uuid4())  # cihaz için unique ID
            aktif_kullanici_ekle(k_adi, st.session_state["session_id"])
            kullanici_sonuclarini_yukle_to_session(k_adi)
            st.session_state["page"] = "ders"
            st.rerun()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")

    if kayit_btn:
        st.session_state["page"] = "kayit"
        st.rerun()

# ===============================
# Router (çoklu cihaz uyumlu)
# ===============================
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "page" not in st.session_state:
    st.session_state["page"] = "login"

# Sayfa yönlendirme
if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "kayit":
    kayit_page()
elif st.session_state["page"] == "ders":
    ders_secim_page()
elif st.session_state["page"] == "konu":
    if "ders" in st.session_state:
        konu_secim_page(st.session_state["ders"])
    else:
        st.session_state["page"] = "ders"
        st.rerun()
elif st.session_state["page"] == "test":
    if "ders" in st.session_state and "konu" in st.session_state:
        test_secim_page(st.session_state["ders"], st.session_state["konu"])
    else:
        st.session_state["page"] = "ders"
        st.rerun()
elif st.session_state["page"] == "soru":
    soru_goster_page()
elif st.session_state["page"] == "rapor":
    genel_rapor_page()
elif st.session_state["page"] == "profil":
    profil_page()
