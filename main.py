# ===============================
# Konu Seçim Ekranı
# ===============================
def konu_secim_page(secilen_ders):
    clear_output()
    mesaj = widgets.Label(f"📖 {secilen_ders} dersi için konu seçin:")
    ogeler = []

    for konu in soru_bankasi[secilen_ders].keys():
        def konu_secim_clicked(b):
            test_secim_page(secilen_ders, b.konu_adi)
        b = widgets.Button(description=konu)
        b.konu_adi = konu
        b.on_click(konu_secim_clicked)
        ogeler.append(b)

        # İlerleme çubuğu
        toplam_soru = len(soru_bankasi[secilen_ders][konu])
        cozulen = 0
        if secilen_ders in sonuclar and konu in sonuclar[secilen_ders]:
            cozulen = sonuclar[secilen_ders][konu]["dogru"] + sonuclar[secilen_ders][konu]["yanlis"]
        ilerleme = widgets.IntProgress(value=cozulen, min=0, max=max(1, toplam_soru),
                                       description=f"%{int((cozulen/max(1, toplam_soru))*100)}",
                                       bar_style='success' if cozulen==toplam_soru and toplam_soru>0 else '')
        ogeler.append(ilerleme)

    geri_butonu = widgets.Button(description="Geri", button_style='warning')
    geri_butonu.on_click(lambda b: ders_secim_page())
    ogeler.append(geri_butonu)

    display(widgets.VBox([mesaj]+ogeler, layout=widgets.Layout(align_items='flex-start')))

# ===============================
# Test Seçim Ekranı
# ===============================
def test_secim_page(secilen_ders, secilen_konu):
    clear_output()
    tum_sorular = soru_bankasi[secilen_ders][secilen_konu]
    if not tum_sorular:
        mesaj = widgets.Label("Bu konu için henüz soru eklenmemiş.")
        geri_butonu = widgets.Button(description="Geri", button_style='warning')
        geri_butonu.on_click(lambda b: konu_secim_page(secilen_ders))
        display(widgets.VBox([mesaj, geri_butonu]))
        return

    soru_grubu_sayisi = 5
    test_sayisi = math.ceil(len(tum_sorular)/soru_grubu_sayisi)
    mesaj = widgets.Label("Lütfen bir test seçin:")
    butonlar = []

    for i in range(test_sayisi):
        baslangic = i*soru_grubu_sayisi
        bitis = min((i+1)*soru_grubu_sayisi, len(tum_sorular))
        b = widgets.Button(description=f"Test {i+1}: Soru {baslangic+1}-{bitis}")
        b.test_no = i+1

        def test_clicked(btn, i=i):
            baslangic = i*soru_grubu_sayisi
            bitis = min((i+1)*soru_grubu_sayisi, len(tum_sorular))
            secilen_test = tum_sorular[baslangic:bitis]
            if secilen_ders not in sonuclar:
                sonuclar[secilen_ders] = {}
            if secilen_konu not in sonuclar[secilen_ders]:
                sonuclar[secilen_ders][secilen_konu] = {"dogru":0,"yanlis":0}
            soru_goster_page(secilen_test, 0, secilen_ders, secilen_konu, i+1, test_sayisi)

        b.on_click(test_clicked)

        # Çözülen testleri renklendir
        if (secilen_ders in sonuclar and
            secilen_konu in sonuclar[secilen_ders] and
            f"test_{i+1}" in sonuclar[secilen_ders][secilen_konu]):
            test_sonuc = sonuclar[secilen_ders][secilen_konu][f"test_{i+1}"]
            dogru = test_sonuc["dogru"]
            yanlis = test_sonuc["yanlis"]
            oran = dogru/(dogru+yanlis) if dogru+yanlis>0 else 0
            if oran>=0.6: b.button_style='success'
            else: b.button_style='danger'

        butonlar.append(b)

    geri_butonu = widgets.Button(description="Geri", button_style='warning')
    geri_butonu.on_click(lambda b: konu_secim_page(secilen_ders))

    display(widgets.VBox([mesaj]+butonlar+[geri_butonu], layout=widgets.Layout(align_items='flex-start')))

# ===============================
# Soru Gösterim Ekranı
# ===============================
def soru_goster_page(secilen_test, index, secilen_ders, secilen_konu, test_no, test_sayisi):
    clear_output()
    if index >= len(secilen_test):
        # Test bitim ekranı
        dogru = sonuclar[secilen_ders][secilen_konu]["dogru"]
        yanlis = sonuclar[secilen_ders][secilen_konu]["yanlis"]
        sonuclar[secilen_ders][secilen_konu][f"test_{test_no}"] = {"dogru":dogru,"yanlis":yanlis}
        mesaj = widgets.HTML(f"<b>Test tamamlandı!</b><br>✅ Doğru: {dogru}<br>❌ Yanlış: {yanlis}")
        butonlar = []

        if test_no<test_sayisi:
            sonraki_test = widgets.Button(description="Sonraki Test")
            sonraki_test.on_click(lambda b: test_secim_page(secilen_ders,secilen_konu))
            butonlar.append(sonraki_test)

        ana_menu = widgets.Button(description="Ana Menü")
        ana_menu.on_click(lambda b: ders_secim_page())
        butonlar.append(ana_menu)

        rapor = widgets.Button(description="Genel Raporu Gör", button_style='success')
        rapor.on_click(lambda b: genel_rapor_page())
        butonlar.append(rapor)

        display(widgets.VBox([mesaj]+butonlar, layout=widgets.Layout(align_items='flex-start')))
        return

    soru = secilen_test[index]
    soru_label = widgets.HTML(f"<b>Soru {index+1}/{len(secilen_test)}:</b> {soru['soru']}")
    mesaj = widgets.Label("")
    cozum_label = widgets.HTML("")
    secenek_butonlar = []

    def secenek_clicked(b):
        if b.harf==soru['dogru_cevap']:
            mesaj.value="✅ Doğru!"
            sonuclar[secilen_ders][secilen_konu]["dogru"]+=1
        else:
            mesaj.value=f"❌ Yanlış! Doğru Cevap: {soru['dogru_cevap']}"
            sonuclar[secilen_ders][secilen_konu]["yanlis"]+=1
        cozum_label.value=f"<b>Çözüm:</b><br>{soru['cozum']}"
        sonraki_buton.layout.display='inline-flex'

    for harf, metin in soru['secenekler'].items():
        b = widgets.Button(description=f"{harf}) {metin}")
        b.harf=harf
        b.on_click(secenek_clicked)
        secenek_butonlar.append(b)

    geri_butonu = widgets.Button(description="Geri")
    geri_butonu.on_click(lambda b: test_secim_page(secilen_ders,secilen_konu))

    sonraki_buton = widgets.Button(description="Sonraki Soru", button_style='info')
    sonraki_buton.layout.display='none'
    sonraki_buton.on_click(lambda b: soru_goster_page(secilen_test,index+1,secilen_ders,secilen_konu,test_no,test_sayisi))

    display(widgets.VBox([soru_label]+secenek_butonlar+[geri_butonu,mensaje,cozum_label,sonraki_buton],
                         layout=widgets.Layout(align_items='flex-start')))

# ===============================
# Genel Rapor
# ===============================
def genel_rapor_page():
    clear_output()
    mesaj = widgets.HTML("<b>Genel Rapor</b><br><br>")
    icerik=""
    for ders, konular in sonuclar.items():
        icerik+=f"<b>{ders}</b><br>"
        for konu, sonuc in konular.items():
            if isinstance(sonuc, dict) and "dogru" in sonuc:
                toplam = sonuc.get("dogru",0)+sonuc.get("yanlis",0)
                oran = f"{int((sonuc.get('dogru',0)/max(1,toplam))*100)}%"
                icerik+=f"{konu}: ✅ {sonuc.get('dogru',0)} | ❌ {sonuc.get('yanlis',0)} | Başarı: {oran}<br>"

    ana_menu = widgets.Button(description="Ana Menü", button_style='warning')
    ana_menu.on_click(lambda b: ders_secim_page())
    display(widgets.VBox([mesaj,widgets.HTML(icerik),ana_menu],
                         layout=widgets.Layout(align_items='flex-start')))
