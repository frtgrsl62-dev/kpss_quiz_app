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
# Kullanıcı Girişi (Form ile)
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
            ders_secim_page()
        elif k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre:
            st.session_state["user"] = k_adi
            ders_secim_page()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre!")

    if kayit_btn:
        st.session_state["page"] = "kayit"
        st.experimental_rerun()


# ===============================
# Kayıt Sayfası (Form ile)
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
        if st.button(ders):
            st.session_state["ders"] = ders
            konu_secim_page(ders)
    
    if st.button("Genel Raporu Gör"):
        genel_rapor_page()
    
    if st.button("Çıkış Yap"):
        st.session_state.clear()
        login_page()

# ===============================
# Konu Seçim Sayfası
# ===============================
def konu_secim_page(ders):
    st.header(f"{ders} - Konu Seçimi")
    for konu in soru_bankasi[ders].keys():
        if st.button(konu):
            st.session_state["konu"] = konu
            test_secim_page(ders, konu)
    
    if st.button("Geri"):
        ders_secim_page()

# ===============================
# Test Seçimi
# ===============================
def test_secim_page(ders, konu):
    st.header(f"{ders} - {konu} Test Seçimi")
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
        konu_secim_page(ders)

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
        ders_secim_page()

# ===============================
# Başlat
# ===============================
if "user" not in st.session_state:
    login_page()
else:
    ders_secim_page()


