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

# yardımcı: oturum kullanıcısına sonucları kaydet
def kaydet_sonuclar_to_user():
    user = st.session_state.get("user")
    if not user:
        return
    if user not in sabit_kullanicilar:
        # normal kayıtlı kullanıcılar dosyasında saklanıyor
        if user not in kullanicilar:
            kullanicilar[user] = {}
        kullanicilar[user]["sonuclar"] = st.session_state.get("sonuclar", {})
        kullanicilari_kaydet()

# oturum açılınca kullanıcının önceki sonuclarını yükle
def kullanici_sonuclarini_yukle_to_session(user):
    # yalnızca kayıtlı (sabit olmayan) kullanıcılar için
    if user in kullanicilar and "sonuclar" in kullanicilar[user]:
        st.session_state["sonuclar"] = kullanicilar[user]["sonuclar"]
    else:
        # eğer yoksa boş bir yapı oluştur
        if "sonuclar" not in st.session_state:
            st.session_state["sonuclar"] = {}

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
            # kullanıcının önceki sonuçlarını yükle
            kullanici_sonuclarini_yukle_to_session(k_adi)
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
        kullanicilar[k_adi] = {"isim": isim, "sifre": sifre, "sonuclar": {}}
        kullanicilari_kaydet()
        st.success(f"✅ {isim} başarıyla kaydedildi!")
        time.sleep(1)
        st.session_state["page"] = "login"
        st.rerun()

    if geri_btn:
        st.session_state["page"] = "login"
        st.rerun()

# -------------------
# Ders Seçim
# -------------------
def ders_secim_page():
    st.title("Ders Seçiniz")
    for ders in soru_bankasi.keys():
        if st.button(ders):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.experimental_rerun()
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Genel Rapor"):
            st.session_state["page"] = "rapor"
            st.experimental_rerun()
    with col2:
        if st.button("Çıkış"):
            kaydet_sonuclar_to_user()
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.experimental_rerun()

# -------------------
# Konu Seçim
# -------------------
def konu_secim_page(ders):
    st.header(f"{ders} - Konu Seçimi")
    konular = list(soru_bankasi[ders].keys())
    sonuclar = st.session_state.get("sonuclar", {})

    for konu in konular:
        dogru = sonuclar.get(ders, {}).get(konu, {}).get("dogru", 0)
        yanlis = sonuclar.get(ders, {}).get(konu, {}).get("yanlis", 0)
        toplam = dogru + yanlis
        yuzde = int(dogru / toplam * 100) if toplam>0 else 0
        st.metric(label=konu, value=f"{yuzde}%")

        if st.button(f"Gir {konu}", key=f"konu_{konu}"):
            st.session_state["konu"] = konu
            st.session_state["page"] = "test"
            st.experimental_rerun()
    if st.button("🔙 Geri"):
        st.session_state["page"] = "ders"
        st.experimental_rerun()

# -------------------
# Test Seçim
# -------------------
def test_secim_page(ders, konu):
    st.header(f"{ders} - {konu} Testleri")
    tum_sorular = soru_bankasi[ders][konu]
    if not tum_sorular:
        st.info("Henüz soru yok")
        if st.button("Geri"):
            st.session_state["page"] = "konu"
            st.experimental_rerun()
        return
    soru_grubu_sayisi = 5
    test_sayisi = math.ceil(len(tum_sorular)/soru_grubu_sayisi)
    sonuclar = st.session_state.get("sonuclar", {})
    for i in range(test_sayisi):
        baslangic = i*soru_grubu_sayisi
        bitis = min((i+1)*soru_grubu_sayisi, len(tum_sorular))
        test_adi = f"Test {i+1}"
        test_sonuc = sonuclar.get(ders, {}).get(konu, {}).get(f"test_{i+1}")
        if test_sonuc:
            oran = test_sonuc["dogru"]/(bitis-baslangic)
            simge = "✅" if oran>=0.6 else "❌"
            label = f"{test_adi} {simge}"
        else:
            label = f"{test_adi} ⏺"
        if st.button(label, key=f"testbtn_{i}"):
            for k in list(st.session_state.keys()):
                if k.startswith("cevap_"): del st.session_state[k]
            st.session_state["current_test"] = {"test": tum_sorular[baslangic:bitis], "index":0,
                                                "ders":ders,"konu":konu,"test_no":i+1,"test_sayisi":test_sayisi}
            st.session_state["page"] = "soru"
            st.experimental_rerun()
    if st.button("Geri"):
        st.session_state["page"] = "konu"
        st.experimental_rerun()

# -------------------
# Soru Sayfası
# -------------------
def soru_goster_page():
    current = st.session_state["current_test"]
    test_list = current["test"]
    idx = current["index"]
    ders = current["ders"]
    konu = current["konu"]
    test_no = current["test_no"]

    if idx>=len(test_list):
        st.success("Test tamamlandı!")
        sonuclar = st.session_state.setdefault("sonuclar", {})
        sonuclar.setdefault(ders, {}).setdefault(konu, {"dogru":0,"yanlis":0})
        dogru = yanlis = 0
        for k in list(st.session_state.keys()):
            if k.startswith("cevap_"):
                i = int(k.split("_")[1])
                cevap = st.session_state[k]
                if i<len(test_list):
                    if cevap==test_list[i]["dogru_cevap"]: dogru+=1
                    else: yanlis+=1
        sonuclar[ders][konu]["dogru"]+=dogru
        sonuclar[ders][konu]["yanlis"]+=yanlis
        sonuclar[ders][konu][f"test_{test_no}"]={"dogru":dogru,"yanlis":yanlis}
        st.session_state["sonuclar"]=sonuclar
        kaydet_sonuclar_to_user()
        if st.button("Testleri Gör"):
            st.session_state["page"]="test"
            st.experimental_rerun()
        return

    soru = test_list[idx]
    st.markdown(f"**Soru {idx+1}/{len(test_list)}:** {soru['soru']}")
    secenekler = [f"{h}) {m}" for h,m in soru["secenekler"].items()]
    key = f"cevap_{idx}"
    if key not in st.session_state: st.session_state[key]=None
    secim = st.radio("Cevap Seçin:", options=secenekler, index=-1, key=f"soru_radio_{idx}")
    if st.session_state[key]:
        secilen = st.session_state[key]
        if secilen==soru["dogru_cevap"]: st.success("✅ Doğru!")
        else: st.error(f"❌ Yanlış! Doğru: {soru['dogru_cevap']}) {soru['secenekler'][soru['dogru_cevap']]}")
        st.info(f"Çözüm: {soru['cozum']}")
    else:
        if st.button("Cevapla", key=f"cevapla_{idx}"):
            if secim:
                st.session_state[key]=secim.split(")")[0]
                st.experimental_rerun()
            else: st.warning("Seçim yapın!")

    col1,col2 = st.columns([1,1])
    with col1:
        if st.button("🔙 Geri"):
            st.session_state["page"]="test"
            st.experimental_rerun()
    with col2:
        if idx<len(test_list)-1:
            if st.button("Sonraki Soru ➡️"):
                if st.session_state[key]:
                    current["index"]+=1
                    st.experimental_rerun()
                else: st.warning("Önce cevap ver!")
        else:
            if st.button("Testi Bitir 🏠"):
                st.session_state["page"]="test"
                st.experimental_rerun()

# -------------------
# Genel Rapor
# -------------------
def genel_rapor_page():
    st.header("📊 Genel Rapor")
    sonuclar = st.session_state.get("sonuclar", {})
    if not sonuclar:
        st.info("Henüz test çözülmedi.")
    else:
        for ders, konular in sonuclar.items():
            st.subheader(ders)
            for konu, s in konular.items():
                if "dogru" in s:
                    dogru=s["dogru"]; yanlis=s["yanlis"]
                    toplam=dogru+yanlis
                    oran=f"{dogru/ toplam*100:.0f}%" if toplam>0 else "0%"
                    st.markdown(f"- {konu}: ✅ {dogru} | ❌ {yanlis} | Başarı: {oran}")
    if st.button("Ana Menü"):
        st.session_state["page"]="ders"
        st.experimental_rerun()

# -------------------
# Router
# -------------------
if "page" not in st.session_state: st.session_state["page"]="login"

if st.session_state["page"]=="login": login_page()
elif st.session_state["page"]=="kayit": kayit_page()
elif st.session_state["page"]=="ders": ders_secim_page()
elif st.session_state["page"]=="konu": konu_secim_page(st.session_state["ders"])
elif st.session_state["page"]=="test": test_secim_page(st.session_state["ders"], st.session_state["konu"])
elif st.session_state["page"]=="soru": soru_goster_page()
elif st.session_state["page"]=="rapor": genel_rapor_page()

