from soru_bankasi import soru_bankasi

# ===============================
# main.py
# ===============================
import streamlit as st
import time
import math

# ===============================
# Kullanıcı Bilgileri
# ===============================
sabit_kullanicilar = {
    "a": {"isim": "Yönetici", "sifre": "1"},
    "m": {"isim": "Misafir Kullanıcı", "sifre": "0"},
}
kullanicilar = {}
sonuclar = {}

# ===============================
# Kullanıcı Girişi
# ===============================
def login_page():
    st.title("Giriş Ekranı")
    k_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap"):
        if k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            ders_secim_page()
        elif k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            ders_secim_page()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")
    
    if st.button("Kayıt Ol"):
        kayit_page()

# ===============================
# Kayıt Sayfası
# ===============================
def kayit_page():
    st.title("Kayıt Ol")
    isim = st.text_input("İsim Soyisim")
    k_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    sifre_tekrar = st.text_input("Şifre Tekrar", type="password")
    
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
        st.success(f"✅ {isim} başarıyla kaydedildi!")
        time.sleep(1)
        login_page()


