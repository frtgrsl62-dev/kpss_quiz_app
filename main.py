import streamlit as st
import time
import json
import os
import math
from soru_bankasi import soru_bankasi  # Soru bankası ayrı dosyada
from ders_konu_notlari import ders_konu_notlari
from deneme_sinavlari import deneme_sinavlari

# ===============================
# Dosya yolları
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
# Kullanıcı yükle / kaydet
# ===============================
def kullanicilari_yukle():
    if not os.path.exists(DOSYA):
        with open(DOSYA, "w", encoding="utf-8") as f:
            f.write("{}")
    with open(DOSYA, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def kullanicilari_kaydet(kullanicilar_data):
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(kullanicilar_data, f, ensure_ascii=False, indent=2)

# ===============================
# Sonuçları kullanıcıya kaydet
# ===============================
def kaydet_sonuclar_to_user(user, sonuclar):
    if not user:
        return
    kullanicilar = kullanicilari_yukle()
    if user not in kullanicilar:
        # Misafir veya sabit kullanıcılar için kaydetme yapma
        if user not in sabit_kullanicilar:
            return
        # Eğer sabit kullanıcı ise ve henüz yoksa oluştur
        kullanicilar[user] = sabit_kullanicilar[user]

    # 'sonuclar' anahtarı yoksa oluştur
    if 'sonuclar' not in kullanicilar[user]:
        kullanicilar[user]['sonuclar'] = {}
        
    kullanicilar[user]["sonuclar"] = sonuclar
    kullanicilari_kaydet(kullanicilar)

def kullanici_sonuclarini_yukle_to_session(user):
    kullanicilar = kullanicilari_yukle()
    # Hem normal hem de sabit kullanıcılarda sonuçları kontrol et
    if user in kullanicilar and "sonuclar" in kullanicilar[user]:
        st.session_state["sonuclar"] = kullanicilar[user]["sonuclar"]
    elif user in sabit_kullanicilar and "sonuclar" in sabit_kullanicilar[user]:
         st.session_state["sonuclar"] = sabit_kullanicilar[user]["sonuclar"]
    else:
        st.session_state["sonuclar"] = {}

# ===============================
# Login Sayfası
# ===============================
def login_page():
    st.markdown("<h1 style='text-align: center; color: orange;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h1 style='color: ;'>Giriş Ekranı</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        k_adi = st.text_input("Kullanıcı Adı", key="login_user")
        sifre = st.text_input("Şifre", type="password", key="login_pass")
        giris_btn = st.form_submit_button("🟢 Giriş Yap 🟢")
        kayit_btn = st.form_submit_button("🔹 Kayıt Ol 🔹")

    if giris_btn:
        kullanicilar = kullanicilari_yukle()
        if (k_adi in sabit_kullanicilar and sabit_kullanicilar[k_adi]["sifre"] == sifre) or \
           (k_adi in kullanicilar and kullanicilar.get(k_adi, {}).get("sifre") == sifre):
            st.session_state["current_user"] = k_adi
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
    st.markdown("<h1 style='text-align: center; color: orange; font-size:36px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h1 style='color: ;'>Kayıt Ol</h1>", unsafe_allow_html=True)
    with st.form("kayit_form"):
        isim = st.text_input("İsim Soyisim", key="register_name")
        k_adi = st.text_input("Kullanıcı Adı", key="register_user")
        sifre = st.text_input("Şifre", type="password", key="register_pass")
        sifre_tekrar = st.text_input("Şifre Tekrar", type="password", key="register_pass2")
        kaydet_btn = st.form_submit_button("Kaydet ✅")
        geri_btn = st.form_submit_button("↩️ Geri Dön")

    if kaydet_btn:
        kullanicilar = kullanicilari_yukle()
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
        kullanicilari_kaydet(kullanicilar)
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
    col1, col2 = st.columns([8, 2])
    with col2:
        user = st.session_state.get("current_user")
        if user:
            if st.button(f"👤 {user}"):
                st.session_state["page"] = "profil"
                st.rerun()
    st.markdown("<h1 style='font-size:38px;'>Ders Seçiniz</h1>", unsafe_allow_html=True)
    st.markdown("---")
    for ders in soru_bankasi.keys():
        if st.button(ders):
            st.session_state["ders"] = ders
            st.session_state["page"] = "konu"
            st.rerun()
    if st.button("📝 Deneme Sınavları"):
        st.session_state["page"] = "deneme"
        st.rerun()
    if st.button("Genel Raporu Gör 📊"):
        st.session_state["page"] = "rapor"
        st.rerun()
    st.markdown("---")

    if st.button("🔻 Çıkış Yap 🔻"):
        # --- DÜZELTME 1: SAYFA YENİLEYİNCE ÇIKIŞ YAPMA SORUNU ---
        # Tüm session_state'i silmek yerine sadece ilgili anahtarları siliyoruz.
        # Bu sayede sayfa yenilendiğinde oturum kaybolmaz.
        user = st.session_state.get("current_user")
        sonuclar = st.session_state.get("sonuclar", {})
        if user:
            kaydet_sonuclar_to_user(user, sonuclar)
        
        # Sadece bu oturuma ait bilgileri temizle
        st.session_state.pop("current_user", None)
        st.session_state.pop("sonuclar", None)
        st.session_state.pop("ders", None)
        st.session_state.pop("konu", None)
        st.session_state.pop("current_test", None)

        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)


# ===============================
# Konu Seçim Sayfası (Dairesel yüzde gösterimi)
# ===============================
from ders_konu_notlari import ders_konu_notlari

def konu_secim_page(ders):

    # Geri butonu
    if st.button("🏠 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()
    
    st.markdown(
        f"<h2 style='font-size:30px;'>{ders} - Konu Seçimi</h2>",
        unsafe_allow_html=True
    )

    # 📚 Ders Notu butonu
    ders_notu_link = ders_konu_notlari.get(ders, {}).get("__ders_notu__", "")
    if ders_notu_link:
        st.markdown(
          f"<a href='{ders_notu_link}' target='_blank'><button style='background-color: transparent; color: ; padding:8px; border: 1px solid #007BFF; border-radius:8px; cursor:pointer;'>📚 Ders Notları</button></a>",      
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

        # Yüzdeyi hesapla
        yuzde = int(cozulmus_test_sayisi / toplam_test_sayisi * 100) if toplam_test_sayisi > 0 else 0

        col1, col2, col3 = st.columns([1, 8, 2])
        with col1:
            # Dairesel progress
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

 #       with col3:
 #           # Konu linki varsa Not butonu
 #           konu_link = ders_konu_notlari.get(ders, {}).get(konu, "")
 #           if konu_link:
 #              st.markdown(
 #                  f"<a href='{konu_link}' target='_blank' style='text-decoration:none; color:#007BFF;'>📕 pdf</a>",
 #                  unsafe_allow_html=True
 #               )  

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Test Seçim Sayfası
# ===============================
from ders_konu_notlari import ders_konu_notlari

def test_secim_page(secilen_ders, secilen_konu):
    # Geri butonu sol üst
    if st.button("🔙 Geri"):
        st.session_state["page"] = "konu"
        st.rerun()
    
    st.markdown(
        f"<h2 style='font-size:25px;'>{secilen_ders} - {secilen_konu} </h2>",
        unsafe_allow_html=True
    )

    # 📕 Konu Notu butonu
    konu_link = ders_konu_notlari.get(secilen_ders, {}).get(secilen_konu, "")
    if konu_link:  # Link varsa göster
        st.markdown(
            f"<a href='{konu_link}' target='_blank'><button style='background-color: transparent; color: ; padding:6px; border: 1px solid #007BFF; border-radius:8px; cursor:pointer;'>📕 Konu Notu</button></a>",
            unsafe_allow_html=True
        )
    else:  # Link yoksa bilgi ver
        st.info("Bu konu için henüz not eklenmemiştir.")

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

            # önceki cevapları temizle
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

    st.markdown("---")  # alt çizgi
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)



# ===============================
# Soru Gösterim Sayfası
# ===============================
def soru_goster_page():
    current = st.session_state.get("current_test")
    # current_test yoksa veya boşsa, test seçim sayfasına geri dön
    if not current:
        st.warning("Lütfen bir test seçin.")
        st.session_state["page"] = "test"
        st.rerun()
        return

    secilen_test = current.get("test", [])
    index = current.get("index", 0)

    if not secilen_test or index < 0 or index > len(secilen_test):
        st.error("❌ Geçersiz test verisi!")
        if st.button("🔙 Geri Dön"):
            if current.get("ders") == "📝 Deneme Sınavı":
                st.session_state["page"] = "deneme"
            else:
                st.session_state["page"] = "test"
            st.rerun()
        return

    secilen_ders = current["ders"]
    secilen_konu = current["konu"]
    test_no = current["test_no"]
    
    if st.button("🔙 Geri"):
        if secilen_ders == "📝 Deneme Sınavı":
            st.session_state["page"] = "deneme"
        else:
            st.session_state["page"] = "test"
        st.rerun()

    if index >= len(secilen_test):
        st.success("Test tamamlandı!")

        if "sonuclar" not in st.session_state:
            st.session_state["sonuclar"] = {}
        sonuclar = st.session_state.get("sonuclar", {})

        if secilen_ders not in sonuclar:
            sonuclar[secilen_ders] = {}
        if secilen_konu not in sonuclar[secilen_ders]:
            sonuclar[secilen_ders][secilen_konu] = {}

        cevap_keys = [k for k in st.session_state.keys() if k.startswith("cevap_")]
        dogru = 0
        yanlis = 0
        for k in cevap_keys:
            secilen_harf = st.session_state[k]
            soru_index_str = k.split("_")[1]
            if soru_index_str.isdigit():
                soru_index = int(soru_index_str)
                if soru_index < len(secilen_test):
                    soru = secilen_test[soru_index]
                    if secilen_harf == soru["dogru_cevap"]:
                        dogru += 1
                    else:
                        yanlis += 1

        # Deneme sınavları için genel doğru/yanlış toplamı tutmaya gerek yok, sadece test sonucunu kaydet
        if secilen_ders != "📝 Deneme Sınavı":
            onceki_test = sonuclar[secilen_ders][secilen_konu].get(f"test_{test_no}")
            if onceki_test:
                sonuclar[secilen_ders][secilen_konu]["dogru"] = sonuclar[secilen_ders][secilen_konu].get("dogru", 0) - onceki_test.get("dogru", 0)
                sonuclar[secilen_ders][secilen_konu]["yanlis"] = sonuclar[secilen_ders][secilen_konu].get("yanlis", 0) - onceki_test.get("yanlis", 0)
            
            sonuclar[secilen_ders][secilen_konu]["dogru"] = sonuclar[secilen_ders][secilen_konu].get("dogru", 0) + dogru
            sonuclar[secilen_ders][secilen_konu]["yanlis"] = sonuclar[secilen_ders][secilen_konu].get("yanlis", 0) + yanlis

        sonuclar[secilen_ders][secilen_konu][f"test_{test_no}"] = {"dogru": dogru, "yanlis": yanlis}
        
        st.session_state["sonuclar"] = sonuclar
        
        # --- DÜZELTME 2: TypeError HATASI ---
        # kaydet_sonuclar_to_user fonksiyonuna eksik olan 'sonuclar' parametresini ekliyoruz.
        kaydet_sonuclar_to_user(st.session_state.get("current_user"), sonuclar)

        st.markdown(f"✅ Doğru: {dogru}  |  ❌ Yanlış: {yanlis}")

        if st.button("Testi Bitir 🏁"):
            if secilen_ders == "📝 Deneme Sınavı":
                st.session_state["page"] = "deneme"
            else:
                st.session_state["page"] = "test"
            st.rerun()
        return

    soru = secilen_test[index]
    st.markdown(f"<h2 style='font-size:20px;'>{secilen_ders} - {secilen_konu}</h2>", unsafe_allow_html=True)
    st.markdown(f"**Soru {index+1}/{len(secilen_test)}:**")
    st.markdown(f"{soru['soru']}")

    if "maddeler" in soru:
        for madde in soru["maddeler"]:
            st.markdown(f"<div style='margin:2px 0'>{madde}</div>", unsafe_allow_html=True)

    secenekler = [f"{harf}) {metin}" for harf, metin in soru["secenekler"].items()]
    cevap_key = f"cevap_{index}"

    secim = st.radio(
        label="Seçenekler",
        options=secenekler,
        key=f"soru_radio_{index}",
        index=None # Başlangıçta hiçbir seçenek seçili olmasın
    )

    # İlerleme butonları için yer tutucular
    col1, col2, col3 = st.columns([1, 1, 1])

    # Eğer cevap daha önce verilmişse, sonucu göster ve ilerlemeye izin ver
    if cevap_key in st.session_state:
        secilen_harf = st.session_state[cevap_key]
        if secilen_harf == soru["dogru_cevap"]:
            st.success("✅ Doğru!")
        else:
            st.error(f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}) {soru['secenekler'][soru['dogru_cevap']]}")
        st.info(f"**Çözüm:** {soru['cozum']}")
        
        # Cevap verildikten sonra sonraki soruya geçme butonu
        with col2:
            if index < len(secilen_test) - 1:
                if st.button("Sonraki Soru ➡️"):
                    current["index"] += 1
                    st.rerun()
        with col3:
             if index == len(secilen_test) - 1:
                if st.button("Testi Bitir 🏁"):
                    current["index"] += 1
                    st.rerun()

    # Cevap henüz verilmemişse, "Cevapla" butonunu göster
    else:
        if st.button("🎯 Cevapla", key=f"cevapla_{index}"):
            if secim is None:
                st.warning("⚠️ Lütfen bir seçenek seçin!")
            else:
                secilen_harf = secim.split(")")[0]
                st.session_state[cevap_key] = secilen_harf
                st.rerun()
    
    # Önceki soru butonu her zaman görünür olsun
    with col1:
        if index > 0:
            if st.button("⬅️ Önceki Soru"):
                current["index"] -= 1
                st.rerun()

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)


# ... (genel_rapor_page, profil_page, deneme_secim_page fonksiyonlarınızda değişiklik yapmanıza gerek yok)
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
            top: 15px;    /* Üstten boşluk */
            left: 10px;   /* Soldan boşluk */
            z-index: 9999; /* Diğer elementlerin üstünde olsun */
        }

        /* Butonun temel stil ayarları */
        .stButton>button {
            background-color: transparent;   /* Arka plan rengi */
            color: ;               /* Yazı rengi */
            border: none;               /* Kenarlık yok */
            border-radius: 12px;        /* Köşelerin yuvarlanması */
            padding: 2px 1px;          /* İç boşluk (üst/alt 8px, sağ/sol 14px) */
            font-size: 14px;            /* Yazı boyutu */
            font-weight: bold;          /* Yazıyı kalın yap */
        }

        /* Hover efekti */
        .stButton>button:hover {
            background-color: ; /* Üzerine gelince arka plan rengi  darkorange  */
            color: white;                 /* Üzerine gelince yazı rengi */
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
            with st.expander(f" {ders}"):    #📕📙📚📘📗#
                for konu, sonuc in konular.items():
                    if not isinstance(sonuc, dict):
                        continue

                    dogru = sonuc.get("dogru", 0)
                    yanlis = sonuc.get("yanlis", 0)
                    toplam = dogru + yanlis
                    oran = f"{dogru / toplam * 100:.0f}%" if toplam > 0 else "0%"

                    st.markdown(f"- **{konu}** → ✅ {dogru} | ❌ {yanlis} | Başarı: {oran}")

    st.markdown("---")
    st.markdown("<h1 style='text-align: center; color: orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)

def profil_page():
    user = st.session_state.get("current_user")
    kullanicilar = kullanicilari_yukle()
    if not user or (user not in kullanicilar and user not in sabit_kullanicilar):
        st.warning("❌ Kullanıcı bilgisi bulunamadı!")
        st.session_state["page"] = "login"
        st.rerun()
        return

    if st.button("🔙 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

    st.markdown("<h2>👤 Kullanıcı Bilgileri</h2>", unsafe_allow_html=True)

    # Sabit veya normal kullanıcı bilgilerini al
    bilgiler = kullanicilar.get(user) or sabit_kullanicilar.get(user)
    isim = bilgiler.get("isim", "")
    k_adi = user
    sifre = bilgiler.get("sifre", "")

    st.write(f"**İsim Soyisim:** {isim}")
    st.write(f"**Kullanıcı Adı:** {k_adi}")
    st.write(f"**Şifre:** {'*' * len(sifre)}")

    # Sadece kayıtlı kullanıcılar şifre değiştirebilir
    if user in kullanicilar:
        with st.expander("🔑 Şifre Değiştir"):
            eski = st.text_input("Eski Şifre", type="password", key="old_pass")
            yeni = st.text_input("Yeni Şifre", type="password", key="new_pass")
            yeni2 = st.text_input("Yeni Şifre (Tekrar)", type="password", key="new_pass2")
            if st.button("Şifreyi Güncelle"):
                if eski != sifre:
                    st.error("❌ Eski şifre yanlış!")
                elif not yeni or not yeni2:
                    st.error("❌ Yeni şifre alanları boş olamaz!")
                elif yeni != yeni2:
                    st.error("❌ Yeni şifreler uyuşmuyor!")
                else:
                    kullanicilar[user]["sifre"] = yeni
                    kullanicilari_kaydet(kullanicilar)
                    st.success("✅ Şifre başarıyla güncellendi!")

    st.markdown("---")
    st.markdown("<h1 style='text-align:center; color:orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>", unsafe_allow_html=True)

def deneme_secim_page():
    if st.button("🔙 Geri"):
        st.session_state["page"] = "ders"
        st.rerun()

    st.markdown("<h2>📝 Deneme Sınavları</h2>", unsafe_allow_html=True)

    sonuclar = st.session_state.get("sonuclar", {})

    for deneme_adi, alt_basliklar in deneme_sinavlari.items():
        with st.expander(f"📘 {deneme_adi}"):
            for alt_baslik, sorular in alt_basliklar.items():
                soru_sayisi = len(sorular)
                ders_key = "📝 Deneme Sınavı"
                konu_key = f"{deneme_adi} - {alt_baslik}"
                
                # Test sonucunu daha güvenilir bir şekilde al
                test_sonuc = sonuclar.get(ders_key, {}).get(konu_key, {}).get("test_1")

                if test_sonuc:
                    dogru_sayi = test_sonuc.get("dogru", 0)
                    oran = dogru_sayi / soru_sayisi if soru_sayisi > 0 else 0
                    simge = "✅" if oran >= 0.6 else "❌"
                    label = f"{alt_baslik} ({soru_sayisi} soru) {simge} ({dogru_sayi}/{soru_sayisi})"
                else:
                    label = f"{alt_baslik} ({soru_sayisi} soru) ⏺"

                if st.button(label, key=f"deneme_{deneme_adi}_{alt_baslik}"):

                    cevap_keys = [k for k in list(st.session_state.keys()) if k.startswith("cevap_")]
                    for k in cevap_keys:
                        del st.session_state[k]

                    st.session_state["current_test"] = {
                        "test": sorular,
                        "index": 0,
                        "ders": ders_key,
                        "konu": konu_key,
                        "test_no": 1,
                        "test_sayisi": 1
                    }
                    st.session_state["page"] = "soru"
                    st.rerun()

    st.markdown("---")
    st.markdown(
        "<h1 style='text-align:center; color:orange; font-size:15px;'>KPSS SORU ÇÖZÜM PLATFORMU</h1>",
        unsafe_allow_html=True
    )

# ===============================
# Router
# ===============================
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# Giriş yapılmadıysa ve kayıt sayfasında değilse, her zaman girişe yönlendir
if "current_user" not in st.session_state and st.session_state.page != "kayit":
    st.session_state.page = "login"

# Sayfa yönlendirmeleri
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "kayit":
    kayit_page()
elif st.session_state.page == "ders":
    ders_secim_page()
elif st.session_state.page == "konu":
    konu_secim_page(st.session_state.get("ders", ""))
elif st.session_state.page == "test":
    test_secim_page(st.session_state.get("ders", ""), st.session_state.get("konu", ""))
elif st.session_state.page == "soru":
    soru_goster_page()
elif st.session_state.page == "rapor":
    genel_rapor_page()
elif st.session_state.page == "profil":
    profil_page()
elif st.session_state.page == "deneme":
    deneme_secim_page()


