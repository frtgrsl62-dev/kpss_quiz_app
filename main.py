import streamlit as st
import time
import json
import os
import math
from soru_bankasi import soru_bankasi  # Soru bankası ayrı dosyada
# import matplotlib.pyplot as plt

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
    # Üst başlık
    st.markdown("<h1 style='text-align: center; color: orange;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")  # alt çizgi ile ayır

# color: → yazının rengini ayarlar.
    # yeşil = #4CAF50
    # mavi = #1E90FF
    # red
# text-align: center; → ortalar
    
    #st.title("Giriş Ekranı")
    st.markdown("<h1 style='color: white;'>Giriş Ekranı</h1>", unsafe_allow_html=True)
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
    # Üst başlık
    st.markdown("<h1 style='text-align: center; color: orange; font-size:36px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")  # alt çizgi ile ayır

    st.markdown("<h1 style='color: white;'>Kayıt Ol</h1>", unsafe_allow_html=True)
    # st.title("Kayıt Ol")
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

# ===============================
# Ders Seçim Sayfası
# ===============================
def ders_secim_page():
    st.markdown("<h1 style='color: white; font-size:38px;'>Ders Seçiniz</h1>", unsafe_allow_html=True)
    # st.title("Ders Seçiniz")
    for ders in soru_bankasi.keys():
        if st.button(ders):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.rerun()
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Genel Raporu Gör"):
            st.session_state["page"] = "rapor"
            st.rerun()
    with col2:
        if st.button("Çıkış Yap"):
            # çıkış yaparken oturum bilgilerini temizle ama sonuçları kaydet
            kaydet_sonuclar_to_user()
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()

# ===============================
# Konu Seçim Sayfası (Dairesel yüzde gösterimi)
# ===============================
def konu_secim_page(ders):
    st.header(f"{ders} - Konu Seçimi")
    konular = list(soru_bankasi[ders].keys())
    sonuclar = st.session_state.get("sonuclar", {})

    for konu in konular:
        tum_sorular = soru_bankasi[ders][konu]
        soru_grubu_sayisi = 5
        toplam_test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)

        # Çözülen test sayısını bul
        testler = sonuclar.get(ders, {}).get(konu, {})
        cozulmus_test_sayisi = sum(
            1 for key in testler if key.startswith("test_")
        )

        # Yüzdeyi çözülen test sayısına göre hesapla
        yuzde = int(cozulmus_test_sayisi / toplam_test_sayisi * 100) if toplam_test_sayisi > 0 else 0

        col1, col2 = st.columns([1, 10])
        with col1:
            # Dairesel yüzde göstergesi HTML + CSS
            st.markdown(f"""
            <div style="
                width:40px; height:40px; border-radius:40%;
                background: conic-gradient(#4CAF50 {yuzde}%, #E0E0E0 {yuzde}%);
                display:flex; align-items:center; justify-content:center;
                font-weight:bold; color:black;">
                {yuzde}%
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button(f"→ {konu}", key=f"konu_{konu}"):
                st.session_state["konu"] = konu
                st.session_state["page"] = "test"
                st.rerun()

    if st.button("🔙 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()




# ===============================
# Test Seçim Sayfası
# ===============================
def test_secim_page(secilen_ders, secilen_konu):
    st.markdown(
    f"<h2 style='color: white; font-size:30px;'>{secilen_ders} - {secilen_konu} Test Seçimi</h2>",
    unsafe_allow_html=True
    )
    tum_sorular = soru_bankasi[secilen_ders][secilen_konu]
    if not tum_sorular:
        st.info("Bu konu için henüz soru eklenmemiş.")
        if st.button("Geri"):
            st.session_state["page"] = "konu"
            st.rerun()
        return

    soru_grubu_sayisi = 5
    test_sayisi = math.ceil(len(tum_sorular) / soru_grubu_sayisi)

    sonuclar = st.session_state.get("sonuclar", {})

    for i in range(test_sayisi):
        baslangic = i * soru_grubu_sayisi
        bitis = min((i + 1) * soru_grubu_sayisi, len(tum_sorular))
        test_adi = f"Test {i+1}: Soru {baslangic+1}-{bitis}"

        # Çözülmüş testleri renklendir: doğru oran >=0.6 ise ✅, değilse ❌
        test_sonuc = sonuclar.get(secilen_ders, {}).get(secilen_konu, {}).get(f"test_{i+1}")
        if test_sonuc:
            dogru_sayi = test_sonuc.get('dogru',0)
            toplam_soru = bitis - baslangic
            oran = dogru_sayi / toplam_soru
            simge = "✅" if oran >= 0.6 else "❌"
            label = f"{test_adi} {simge} ({dogru_sayi}/{toplam_soru})"
        else:
            label = f"{test_adi} ⏺"

        if st.button(label, key=f"testbtn_{i}", help=f"Test {i+1}"):
            # önce önceki cevap anahtarlarını temizle
            cevap_keys = [k for k in list(st.session_state.keys()) if k.startswith("cevap_")]
            for k in cevap_keys:
                del st.session_state[k]

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

    if st.button("🔙 Geri"):
        st.session_state["page"] = "konu"
        st.rerun()


# ===============================
# Soru Gösterim Sayfası (ilk başta boş, seçim sonrası kırmızı işaret gelir)
# ===============================
def soru_goster_page():
    current = st.session_state["current_test"]
    secilen_test = current["test"]
    index = current["index"]
    secilen_ders = current["ders"]
    secilen_konu = current["konu"]
    test_no = current["test_no"]
    test_sayisi = current["test_sayisi"]

    if index >= len(secilen_test):
        st.success("Test tamamlandı!")
        # ... (tamamlama kısmı aynı kalıyor)
        return

    soru = secilen_test[index]
    st.markdown(f"**{secilen_ders} - {secilen_konu}**")
    st.markdown(f"**Soru {index+1}/{len(secilen_test)}:** {soru['soru']}")

    secenekler = [f"{harf}) {metin}" for harf, metin in soru["secenekler"].items()]
    cevap_key = f"cevap_{index}"

    # İlk başta boş olacak şekilde seçenekler
    secenekler_with_none = [None] + secenekler

    secim = st.radio(
        "Cevap Seçin:",
        options=secenekler_with_none,
        index=0,
        format_func=lambda x: "" if x is None else x,
        key=f"soru_radio_{index}"
    )

    # Cevaplama ve kontrol
    if cevap_key in st.session_state:
        secilen_harf = st.session_state[cevap_key]
        if secilen_harf == soru["dogru_cevap"]:
            st.success("✅ Doğru!")
        else:
            st.error(f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}) {soru['secenekler'][soru['dogru_cevap']]}")

        st.info(f"**Çözüm:** {soru['cozum']}")
    else:
        if st.button("Cevapla", key=f"cevapla_{index}"):
            if secim is None:
                st.warning("⚠️ Lütfen bir seçenek seçin!")
            else:
                secilen_harf = secim.split(")")[0]
                st.session_state[cevap_key] = secilen_harf
                st.rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔙 Geri"):
            st.session_state["page"] = "test"
            st.rerun()
    with col2:
        if index < len(secilen_test) - 1:
            if st.button("Sonraki Soru ➡️"):
                if cevap_key in st.session_state:
                    current["index"] += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Lütfen önce bu soruyu cevaplayın!")
        else:
            if st.button("Testi Bitir 🏁"):
                if cevap_key in st.session_state:
                    current["index"] += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Lütfen önce bu soruyu cevaplayın!")





# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
    st.header("📊 Genel Rapor")
    sonuclar = st.session_state.get("sonuclar", {})

    if not sonuclar:
        st.info("Henüz herhangi bir test çözülmedi.")
    else:
        for ders, konular in sonuclar.items():
            st.subheader(f"📘 {ders}")
            for konu, sonuc in konular.items():
                # test_* anahtarlarını hariç tutarak sadece toplam dogru/yanlis oku
                dogru = sonuc.get("dogru", 0)
                yanlis = sonuc.get("yanlis", 0)
                toplam = dogru + yanlis
                oran = f"{dogru/ toplam * 100:.0f}%" if toplam > 0 else "0%"
                st.markdown(f"- **{konu}** → ✅ {dogru} | ❌ {yanlis} | Başarı: {oran}")

    st.markdown("---")
    if st.button("🏠 Ana Menüye Dön"):
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
    # güvenlik: ders mevcut mu kontrolü
    if "ders" in st.session_state:
        konu_secim_page(st.session_state["ders"])
    else:
        st.session_state["page"] = "ders"
        st.rerun()
elif st.session_state["page"] == "test":
    # güvenlik: ders/konu mevcut mu
    if "ders" in st.session_state and "konu" in st.session_state:
        test_secim_page(st.session_state["ders"], st.session_state["konu"])
    else:
        st.session_state["page"] = "ders"
        st.rerun()
elif st.session_state["page"] == "soru":
    soru_goster_page()
elif st.session_state["page"] == "rapor":
    genel_rapor_page()
























































