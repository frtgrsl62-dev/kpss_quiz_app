import streamlit as st
import time
import json
import os
import math
from soru_bankasi import soru_bankasi
from ders_konu_notlari import ders_konu_notlari
from deneme_sinavlari import deneme_sinavlari

# ======================================================
# DOSYA
# ======================================================
DOSYA = "kullanicilar.json"

# ======================================================
# SABİT KULLANICILAR
# ======================================================
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1"},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0"},
}

# ======================================================
# KULLANICI DOSYA İŞLEMLERİ
# ======================================================
def kullanicilari_yukle():
    if not os.path.exists(DOSYA):
        with open(DOSYA, "w", encoding="utf-8") as f:
            json.dump({}, f)
    try:
        with open(DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def kullanicilari_kaydet():
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=2)

# ======================================================
# SONUÇ KAYIT / YÜKLE
# ======================================================
def kaydet_sonuclar_to_user(user):
    if not user or user not in kullanicilar:
        return
    kullanicilar[user]["sonuclar"] = st.session_state.get("sonuclar", {})
    kullanicilari_kaydet()

def kullanici_sonuclarini_yukle_to_session(user):
    if user in kullanicilar:
        st.session_state["sonuclar"] = kullanicilar[user].get("sonuclar", {})
    else:
        st.session_state["sonuclar"] = {}

# ======================================================
# GLOBAL
# ======================================================
kullanicilar = kullanicilari_yukle()

# ======================================================
# LOGIN
# ======================================================
def login_page():
    st.title("KPSS SORU ÇÖZÜM PLATFORMU")

    with st.form("login"):
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        giris = st.form_submit_button("Giriş Yap")
        kayit = st.form_submit_button("Kayıt Ol")

    if giris:
        if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
           (k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre):

            st.session_state.clear()
            st.session_state["current_user"] = k_adi
            kullanici_sonuclarini_yukle_to_session(k_adi)
            st.session_state["page"] = "ders"
            st.rerun()
        else:
            st.error("Hatalı giriş")

    if kayit:
        st.session_state["page"] = "kayit"
        st.rerun()

# ======================================================
# KAYIT
# ======================================================
def kayit_page():
    st.title("Kayıt Ol")

    with st.form("register"):
        isim = st.text_input("İsim Soyisim")
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        sifre2 = st.text_input("Şifre Tekrar", type="password")
        kaydet = st.form_submit_button("Kaydet")

    if kaydet:
        if not isim or not k_adi or not sifre:
            st.error("Alanlar boş")
            return
        if sifre != sifre2:
            st.error("Şifreler uyuşmuyor")
            return
        if k_adi in kullanicilar or k_adi in sabit_kullanicilar:
            st.error("Kullanıcı adı mevcut")
            return

        kullanicilar[k_adi] = {
            "isim": isim,
            "sifre": sifre,
            "sonuclar": {}
        }
        kullanicilari_kaydet()
        st.success("Kayıt başarılı")
        time.sleep(1)
        st.session_state["page"] = "login"
        st.rerun()

# ======================================================
# DERS SEÇİM
# ======================================================
def ders_secim_page():
    st.header("Ders Seç")

    for ders in soru_bankasi:
        if st.button(ders):
            kaydet_sonuclar_to_user(st.session_state["current_user"])
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.rerun()

    if st.button("📝 Deneme"):
        st.session_state["page"] = "deneme"
        st.rerun()

    if st.button("📊 Genel Rapor"):
        st.session_state["page"] = "rapor"
        st.rerun()

    if st.button("🚪 Çıkış"):
        kaydet_sonuclar_to_user(st.session_state["current_user"])
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()

# ======================================================
# KONU
# ======================================================
def konu_secim_page(ders):
    if st.button("⬅️ Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

    st.subheader(ders)
    sonuclar = st.session_state.get("sonuclar", {})

    for konu in soru_bankasi[ders]:
        if st.button(konu):
            kaydet_sonuclar_to_user(st.session_state["current_user"])
            st.session_state["konu"] = konu
            st.session_state["page"] = "test"
            st.rerun()

# ======================================================
# TEST
# ======================================================
def test_secim_page(ders, konu):
    if st.button("⬅️ Geri"):
        st.session_state["page"] = "konu"
        st.rerun()

    tum = soru_bankasi[ders][konu]
    grup = 5
    test_sayisi = math.ceil(len(tum) / grup)

    for i in range(test_sayisi):
        if st.button(f"Test {i+1}"):
            st.session_state["current_test"] = {
                "test": tum[i*grup:(i+1)*grup],
                "index": 0,
                "ders": ders,
                "konu": konu,
                "test_no": i+1
            }
            st.session_state["page"] = "soru"
            st.rerun()

# ======================================================
# SORU
# ======================================================
def soru_page():
    ct = st.session_state["current_test"]
    idx = ct["index"]
    sorular = ct["test"]

    if idx >= len(sorular):
        st.success("Test tamamlandı")
        kaydet_sonuclar_to_user(st.session_state["current_user"])
        if st.button("Geri"):
            st.session_state["page"] = "test"
            st.rerun()
        return

    soru = sorular[idx]
    st.write(soru["soru"])

    secenekler = list(soru["secenekler"].items())
    secim = st.radio("", [f"{k}) {v}" for k, v in secenekler])

    if st.button("Cevapla"):
        if "sonuclar" not in st.session_state:
            st.session_state["sonuclar"] = {}

        dogru = secim.startswith(soru["dogru_cevap"])
        st.success("Doğru" if dogru else "Yanlış")

        ct["index"] += 1
        kaydet_sonuclar_to_user(st.session_state["current_user"])
        st.rerun()

# ======================================================
# RAPOR
# ======================================================
def genel_rapor_page():
    if st.button("⬅️ Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

    st.header("Genel Rapor")
    st.json(st.session_state.get("sonuclar", {}))

# ======================================================
# ROUTER
# ======================================================
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state.get("current_user") is None:
    if st.session_state["page"] not in ["login", "kayit"]:
        st.session_state["page"] = "login"

# Güvenlik kemeri: her rerun'da yaz
if "current_user" in st.session_state:
    kaydet_sonuclar_to_user(st.session_state["current_user"])

page = st.session_state["page"]

if page == "login":
    login_page()
elif page == "kayit":
    kayit_page()
elif page == "ders":
    ders_secim_page()
elif page == "konu":
    konu_secim_page(st.session_state["ders"])
elif page == "test":
    test_secim_page(st.session_state["ders"], st.session_state["konu"])
elif page == "soru":
    soru_page()
elif page == "rapor":
    genel_rapor_page()
