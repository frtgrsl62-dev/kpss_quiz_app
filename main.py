import streamlit as st
import time
import json
import os
import math
from soru_bankasi import soru_bankasi  # Soru bankası ayrı dosyada

# ===============================
# Dosya yolları
# ===============================
DOSYA = "kullanicilar.json"
AKTIF_DOSYA = "aktif_kullanici.json"

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
# Aktif kullanıcı dosyası
# ===============================
def aktif_kullanici_kaydet(user):
    with open(AKTIF_DOSYA, "w", encoding="utf-8") as f:
        json.dump({"user": user}, f)

def aktif_kullanici_yukle():
    if os.path.exists(AKTIF_DOSYA):
        with open(AKTIF_DOSYA, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("user")
    return None

def aktif_kullanici_sil():
    if os.path.exists(AKTIF_DOSYA):
        os.remove(AKTIF_DOSYA)

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
    # Üst başlık
    st.markdown("<h1 style='text-align: center; color: orange;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")  # alt çizgi ile ayır

# color: → yazının rengini ayarlar.
    # yeşil = #4CAF50
    # mavi = #1E90FF
    # red
    # açık mavi #ADD8E6    #87CEEB
# text-align: center; → ortalar
    
    #st.title("Giriş Ekranı")
    st.markdown("<h1 style='color: ;'>Giriş Ekranı</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        k_adi = st.text_input("Kullanıcı Adı", key="login_user")
        sifre = st.text_input("Şifre", type="password", key="login_pass")
        giris_btn = st.form_submit_button("🟢 Giriş Yap 🟢")
        kayit_btn = st.form_submit_button("🔹 Kayıt Ol 🔹")

    if giris_btn:
        if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
           (k_adi in kullanicilar and kullanicilar[k_adi]["sifre"] == sifre):
            st.session_state["current_user"] = k_adi
            aktif_kullanici_kaydet(k_adi)
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

    st.markdown("<h1 style='color: ;'>Kayıt Ol</h1>", unsafe_allow_html=True)
    # st.title("Kayıt Ol")
    with st.form("kayit_form"):
        isim = st.text_input("İsim Soyisim", key="register_name")
        k_adi = st.text_input("Kullanıcı Adı", key="register_user")
        sifre = st.text_input("Şifre", type="password", key="register_pass")
        sifre_tekrar = st.text_input("Şifre Tekrar", type="password", key="register_pass2")
        kaydet_btn = st.form_submit_button("Kaydet ✅")
        geri_btn = st.form_submit_button("↩️ Geri Dön")

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
        # Sağ üst kullanıcı butonu
    col1, col2 = st.columns([8, 2])
    with col2:
        user = st.session_state.get("current_user")
        if user:
            if st.button(f"👤 {user}"):
                st.session_state["page"] = "profil"
                st.rerun()
    
    st.markdown("<h1 style='font-size:38px;'>Ders Seçiniz</h1>", unsafe_allow_html=True)
    st.markdown("---")  # üst çizgi

    # Ders listesi
    for ders in soru_bankasi.keys():
        if st.button(ders):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.rerun()

    # Genel Raporu Gör
    if st.button("Genel Raporu Gör 📊"):
        st.session_state["page"] = "rapor"
        st.rerun()
        
    # Derslerden sonra çizgi
    st.markdown("---")

    # Çıkış Yap (altta kalsın)
    if st.button("🔻 Çıkış Yap 🔻"):
        kaydet_sonuclar_to_user(st.session_state.get("current_user"))
        aktif_kullanici_sil()
        st.session_state["current_user"] = None
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("---")  # alt çizgi ile ayır
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)




# ===============================
# Konu Seçim Sayfası (Dairesel yüzde gösterimi)
# ===============================
def konu_secim_page(ders):

    # Geri butonu sol üst
    if st.button("🏠 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    # st.header(f"{ders} - Konu Seçimi")
    st.markdown(
    f"<h2 style='color: ; font-size:30px;'>{ders} - Konu Seçimi</h2>",
    unsafe_allow_html=True
    )
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



    st.markdown("---")  # alt çizgi ile ayır
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Test Seçim Sayfası
# ===============================
def test_secim_page(secilen_ders, secilen_konu):
        # Geri butonu sol üst
    if st.button("🔙 Geri"):
        st.session_state["page"] = "konu"
        st.rerun()
    
    st.markdown(
        f"<h2 style='color: ; font-size:25px;'>{secilen_ders} - {secilen_konu} Test Seçimi</h2>",
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
        soru_sayisi = bitis - baslangic
        test_adi = f"Test {i+1}: ({soru_sayisi} Soru)"

        # Çözülmüş testleri renklendir: doğru oran >=0.6 ise ✅, değilse ❌
        test_sonuc = sonuclar.get(secilen_ders, {}).get(secilen_konu, {}).get(f"test_{i+1}")
        if test_sonuc:
            dogru_sayi = test_sonuc.get('dogru', 0)
            oran = dogru_sayi / soru_sayisi
            simge = "✅" if oran >= 0.6 else "❌"
            label = f"{test_adi} {simge} ({dogru_sayi}/{soru_sayisi})"
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

     # if st.button("🔙 Geri"):
     #  st.session_state["page"] = "konu"
     #  st.rerun()

    st.markdown("---")  # alt çizgi ile ayır
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)

# ===============================
# Soru Gösterim Sayfası (Radyo başta seçili gelmez)
# ===============================
def soru_goster_page():
    current = st.session_state["current_test"]
    secilen_test = current.get("test", [])
    index = current.get("index", 0)

    if not secilen_test or index < 0 or index > len(secilen_test):
        st.error("❌ Geçersiz test verisi!")
        if st.button("🔙 Geri Dön"):
            st.session_state["page"] = "test"
            st.rerun()
        return

    secilen_ders = current["ders"]
    secilen_konu = current["konu"]
    test_no = current["test_no"]
    test_sayisi = current["test_sayisi"]

    # ===== Sol üst geri butonu =====
    if st.button("🔙 Geri"):
        st.session_state["page"] = "test"
        st.rerun()

    # ===== Test tamamlandıysa =====
    if index >= len(secilen_test):
        st.success("Test tamamlandı!")

        if "sonuclar" not in st.session_state:
            st.session_state["sonuclar"] = {}
        sonuclar = st.session_state["sonuclar"]
        if secilen_ders not in sonuclar:
            sonuclar[secilen_ders] = {}
        if secilen_konu not in sonuclar[secilen_ders]:
            sonuclar[secilen_ders][secilen_konu] = {"dogru": 0, "yanlis": 0}

        # Cevapları topla
        cevap_keys = [k for k in st.session_state.keys() if k.startswith("cevap_")]
        dogru = 0
        yanlis = 0
        for k in cevap_keys:
            secilen_harf = st.session_state[k]
            soru_index = int(k.split("_")[1])
            if soru_index < len(secilen_test):
                soru = secilen_test[soru_index]
                if secilen_harf == soru["dogru_cevap"]:
                    dogru += 1
                else:
                    yanlis += 1

        # Önceki test sonuçlarını sıfırla
        onceki_test = sonuclar[secilen_ders][secilen_konu].get(f"test_{test_no}")
        if onceki_test:
            sonuclar[secilen_ders][secilen_konu]["dogru"] -= onceki_test.get("dogru", 0)
            sonuclar[secilen_ders][secilen_konu]["yanlis"] -= onceki_test.get("yanlis", 0)

        # Yeni sonuçları ekle
        sonuclar[secilen_ders][secilen_konu]["dogru"] += dogru
        sonuclar[secilen_ders][secilen_konu]["yanlis"] += yanlis
        sonuclar[secilen_ders][secilen_konu][f"test_{test_no}"] = {"dogru": dogru, "yanlis": yanlis}

        st.session_state["sonuclar"] = sonuclar
        kaydet_sonuclar_to_user(st.session_state.get("current_user"))

        st.markdown(f"✅ Doğru: {dogru}  |  ❌ Yanlış: {yanlis}")

        if st.button("Testi Bitir 🏁"):
            st.session_state["page"] = "test"
            st.rerun()
        return

    # ===== Soruyu Göster =====
    soru = secilen_test[index]
    st.markdown(f"<h2 style='font-size:20px;'>{secilen_ders} - {secilen_konu}</h2>", unsafe_allow_html=True)
    st.markdown(f"**Soru {index+1}/{len(secilen_test)}:**")   
    st.markdown(f"{soru['soru']}")

    # Eğer maddeler varsa liste halinde göster
    if "maddeler" in soru:
        for madde in soru["maddeler"]:
            # st.markdown(f"- {madde}")
             st.markdown(f"<div style='margin:2px 0'>{madde}</div>", unsafe_allow_html=True)

    secenekler = [f"{harf}) {metin}" for harf, metin in soru["secenekler"].items()]
    cevap_key = f"cevap_{index}"

    # Radyo butonu
    if cevap_key in st.session_state:
        secim = st.radio(
            label="",
            options=secenekler,
            index=[s.split(")")[0] for s in secenekler].index(st.session_state[cevap_key]),
            key=f"soru_radio_{index}"
        )
    else:
        secim = st.radio(
            label="",
            options=secenekler + [None],
            index=len(secenekler),
            format_func=lambda x: "" if x is None else x,
            key=f"soru_radio_{index}"
        )

    # Cevap kontrol ve kaydetme
    if cevap_key in st.session_state:
        secilen_harf = st.session_state[cevap_key]
        if secilen_harf == soru["dogru_cevap"]:
            st.success("✅ Doğru!")
        else:
            st.error(f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}) {soru['secenekler'][soru['dogru_cevap']]}")
        st.info(f"**Çözüm:** {soru['cozum']}")
    else:
        if st.button("🎯 Cevapla", key=f"cevapla_{index}"):
            if secim is None:
                st.warning("⚠️ Lütfen bir seçenek seçin!")
            else:
                secilen_harf = secim.split(")")[0]
                st.session_state[cevap_key] = secilen_harf
                st.rerun()

    # ===== Alt kısım: Önceki / Sonraki / Testi Bitir =====
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if index > 0 and st.button("⬅️ Önceki Soru"):
            current["index"] -= 1
            st.rerun()
    with col2:
        if index < len(secilen_test) - 1 and st.button("Sonraki Soru ➡️"):
            if cevap_key in st.session_state:
                current["index"] += 1
                st.rerun()
            else:
                st.warning("⚠️ Lütfen önce bu soruyu cevaplayın!")
    with col3:
        if index == len(secilen_test) - 1 and st.button("Testi Bitir 🏁"):
            if cevap_key in st.session_state:
                current["index"] += 1
                st.rerun()
            else:
                st.warning("⚠️ Lütfen önce bu soruyu cevaplayın!")

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
   # ===== Butonun stilini tanımlıyoruz =====
    st.markdown(
        """
        <style>
        /* Sidebar görünür olsun */
        div[data-testid="stSidebar"] {visibility: visible;}
        
        /* Butonu sol üst köşeye sabitle */
        .top-left {
            position: fixed;
            top: 15px;    /* Üstten boşluk */
            left: 10px;   /* Soldan boşluk */
            z-index: 9999; /* Diğer elementlerin üstünde olsun */
        }

        /* Butonun temel stil ayarları */
        .stButton>button {
            background-color: transparent;   /* Arka plan rengi */
            color: white;               /* Yazı rengi */
            border: none;               /* Kenarlık yok */
            border-radius: 12px;        /* Köşelerin yuvarlanması */
            padding: 8px 2px;          /* İç boşluk (üst/alt 8px, sağ/sol 14px) */
            font-size: 14px;            /* Yazı boyutu */
            font-weight: bold;          /* Yazıyı kalın yap */
        }

        /* Hover efekti */
        .stButton>button:hover {
            background-color: darkorange; /* Üzerine gelince arka plan rengi */
            color: white;                 /* Üzerine gelince yazı rengi */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Konteyner ile sabitle
    top_left = st.container()
    with top_left:
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("🏠 Ana Menüye Dön"):
                st.session_state["page"] = "ders"
                st.rerun()

    st.header("📊 Genel Rapor")
    sonuclar = st.session_state.get("sonuclar", {})

    if not sonuclar:
        st.info("Henüz herhangi bir test çözülmedi.")
    else:
        for ders, konular in sonuclar.items():
            with st.expander(f"📘 {ders}"):
                for konu, sonuc in konular.items():
                    if not isinstance(sonuc, dict):
                        continue

                    dogru = sonuc.get("dogru", 0)
                    yanlis = sonuc.get("yanlis", 0)
                    toplam = dogru + yanlis
                    oran = f"{dogru / toplam * 100:.0f}%" if toplam > 0 else "0%"

                    st.markdown(f"- **{konu}** → ✅ {dogru} | ❌ {yanlis} | Başarı: {oran}")

                    testler = {k: v for k, v in sonuc.items() if k.startswith("test_")}
                    if testler:
                        with st.expander(f"📑 {konu} Test Detayları"):
                            for test_no, t_sonuc in testler.items():
                                st.write(f"➡️ {test_no}: ✅ {t_sonuc['dogru']} | ❌ {t_sonuc['yanlis']}")

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Router
# ===============================
# Session başlatılırken aktif kullanıcıyı yükle
if "current_user" not in st.session_state:
    user = aktif_kullanici_yukle()  # dosyadan aktif kullanıcıyı al
    st.session_state["current_user"] = user
    if user:
        st.session_state["user"] = user
        kullanici_sonuclarini_yukle_to_session(user)
        st.session_state["page"] = "ders"  # sayfa yenilenince direkt ders sayfasına git

if "current_user" not in st.session_state:
    st.session_state["current_user"] = aktif_kullanici_yukle()
    if st.session_state["current_user"]:
        kullanici_sonuclarini_yukle_to_session(st.session_state["current_user"])

if "page" not in st.session_state:
    st.session_state["page"] = "login"

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













































