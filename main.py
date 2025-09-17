import streamlit as st
import time
import math
from soru_bankasi import soru_bankasi  # Soru bankası ayrı dosyada

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

    with st.form("login_form"):
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        giris_btn = st.form_submit_button("Giriş Yap")
        kayit_btn = st.form_submit_button("Kayıt Ol")

    if giris_btn:
        if k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            st.session_state["page"] = "ders_secim"
            st.experimental_rerun()
        elif k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            st.session_state["page"] = "ders_secim"
            st.experimental_rerun()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")

    if kayit_btn:
        st.session_state["page"] = "kayit"
        st.experimental_rerun()


# ===============================
# Kayıt Sayfası
# ===============================
def kayit_page():
    st.title("Kayıt Ol")

    with st.form("kayit_form"):
        isim = st.text_input("İsim Soyisim")
        k_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        sifre_tekrar = st.text_input("Şifre Tekrar", type="password")
        kaydet_btn = st.form_submit_button("Kaydet")
        geri_btn = st.form_submit_button("Geri")

    if kaydet_btn:
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
        st.session_state["page"] = "login"
        st.experimental_rerun()

    if geri_btn:
        st.session_state["page"] = "login"
        st.experimental_rerun()


# ===============================
# Ders Seçim Sayfası
# ===============================
def ders_secim_page():
    st.title("Ders Seçiniz")
    for ders in soru_bankasi.keys():
        if st.button(ders, key=f"ders_{ders}"):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu_secim"
            st.experimental_rerun()
    
    if st.button("Genel Raporu Gör", key="rapor"):
        st.session_state["page"] = "rapor"
        st.experimental_rerun()
    
    if st.button("Çıkış Yap", key="cikis"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.experimental_rerun()


# ===============================
# Konu Seçim Sayfası
# ===============================
def konu_secim_page():
    ders = st.session_state["ders"]
    st.header(f"{ders} - Konu Seçimi")
    for konu in soru_bankasi[ders].keys():
        if st.button(konu, key=f"konu_{konu}"):
            st.session_state["konu"] = konu
            st.session_state["page"] = "test"
            st.experimental_rerun()
    
    if st.button("Geri", key="geri_ders"):
        st.session_state["page"] = "ders_secim"
        st.experimental_rerun()


# ===============================
# Test Sayfası
# ===============================
def test_secim_page():
    ders = st.session_state["ders"]
    konu = st.session_state["konu"]
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

    if st.button("Geri", key="geri_konu"):
        st.session_state["page"] = "konu_secim"
        st.experimental_rerun()


# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
    st.header("Genel Rapor")
    for ders, konular in sonuclar.items():
        st.subheader(ders)
        for konu, sonuc in konular.items():
            st.write(f"{konu}: ✅ {sonuc['dogru']} | ❌ {sonuc['yanlis']}")
    
    if st.button("Ana Menü", key="ana_menu"):
        st.session_state["page"] = "ders_secim"
        st.experimental_rerun()


# ===============================
# Başlatıcı
# ===============================
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "user" not in st.session_state:
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "kayit":
        kayit_page()
else:
    if st.session_state["page"] == "ders_secim":
        ders_secim_page()
    elif st.session_state["page"] == "konu_secim":
        konu_secim_page()
    elif st.session_state["page"] == "test":
        test_secim_page()
    elif st.session_state["page"] == "rapor":
        genel_rapor_page()
