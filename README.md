
# SSVEP Tabanlı Görsel Uyaran Sistemi

Bu proje, EEG tabanlı Beyin-Bilgisayar Arayüzü (Brain-Computer Interface – BCI) çalışmalarında kullanılmak üzere Python ve PsychoPy ile geliştirilen bir SSVEP (Steady-State Visual Evoked Potential) görsel uyaran prototipidir.

## Projenin Amacı

Farklı frekanslarda titreşen görsel hedefler oluşturarak, ilerleyen aşamalarda EEG sinyalleri üzerinden kullanıcının odaklandığı hedefin belirlenmesini sağlamak.

İlk geliştirme aşamasında görsel uyaranların frekans doğruluğu ve ekran yenileme zamanlaması test edilmektedir.

## Mevcut Özellikler

- 4 hedefli SSVEP görsel uyaran arayüzü
- 8, 8.5, 9 ve 9.5 Hz hedef frekansları
- Göz konforu için azaltılmış parlaklık kontrastı
- Ekran yenileme süresi ve kare gecikmesi ölçümü
- FFT ile yazılımsal frekans analizi
- CSV formatında deney sonuçlarının kaydedilmesi

## Kullanılan Teknolojiler

- Python
- PsychoPy
- NumPy
- FFT (Fast Fourier Transform)

## Test Ortamı

- İşletim sistemi: macOS 15.6.1
- İşlemci mimarisi: Apple Silicon (ARM64)
- Ekran yenileme hızı: Sabit 60 Hz

## İlk Test Sonuçları

60 Hz ekran üzerinde gerçekleştirilen ilk testlerde:

- Medyan ekran yenileme hızı yaklaşık 60 Hz olarak ölçülmüştür.
- Belirgin kare gecikmesi tespit edilmemiştir.
- Dört hedefin yazılımsal FFT analizinde beklenen frekanslar elde edilmiştir.

Bu sonuçlar yazılım tabanlı ölçümlerdir. Ekranın fiziksel ışık çıkışı henüz fotodiyot ile doğrulanmamıştır.

## Gelecek Geliştirmeler

- 8 ve 16 hedefli SSVEP arayüzleri
- Windows üzerinde 119.982 Hz ekran testleri
- Brain Products EEG cihazından veri alınması
- Gerçek zamanlı EEG sinyal işleme
- CCA ve FBCCA algoritmalarıyla hedef sınıflandırma
- EEG tabanlı oyun kontrolü

## Proje Durumu

**Sürüm: v0.1.0 — Görsel Uyaran Prototipi**

Henüz gerçek EEG verisi kullanılmamaktadır. Sistem, görsel uyaran üretimi ve yazılımsal zamanlama doğrulaması aşamasındadır.

## Güvenlik

Titreşen görsel uyaranlar göz yorgunluğuna veya ışığa duyarlı bireylerde olumsuz reaksiyonlara neden olabilir. Rahatsızlık durumunda test durdurulmalıdır. İnsan katılımcılarla yapılacak deneylerde uygun güvenlik ve etik prosedürler uygulanmalıdır.
