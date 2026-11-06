#!/usr/bin/env python3
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = [
  {"q":"Ada UKM apa saja di ITB AAS?","a":"Halaman UKM mencantumkan BEM, HIMA, UKMI, Devendra Maaspala (pencinta alam), Radio AAS FM, Butaas (bulu tangkis), AASCOUSTIC (musik), Futsal ITBAAS, KOPMA ITBAAS (koperasi), dan KSPM GI (pasar modal/investasi). Detail & Instagram ada di data/ukm.json.","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
  {"q":"Apa itu UKM?","a":"UKM adalah organisasi kemahasiswaan di lingkungan kampus untuk mengembangkan minat, bakat, dan kepribadian di luar akademik: olahraga, seni, kerohanian, kewirausahaan, penalaran, jurnalistik, sosial/lingkungan.","source":"https://itbaas.id/unit-kegitan-mahasiswa-copy/"},
  {"q":"Apa untungnya ikut UKM?","a":"Melatih kepemimpinan, komunikasi, kerja tim, pengelolaan waktu, memperluas jejaring, dan jadi nilai tambah saat cari kerja. Kegiatannya bisa berupa pelatihan, lomba, pentas seni, seminar, sosial, dan pengabdian masyarakat.","source":"https://itbaas.id/unit-kegitan-mahasiswa-copy/"},
  {"q":"BEM dan HIMA itu UKM?","a":"Tidak persis. BEM adalah lembaga eksekutif mahasiswa tingkat perguruan tinggi; HIMA adalah organisasi per jurusan/prodi. Keduanya ditampilkan di halaman yang sama dengan UKM. UKM murni lebih ke minat/bakat (olahraga, musik, alam, investasi, dll.).","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
  {"q":"Cara gabung UKM di ITB AAS?","a":"Biasanya lewat PPKMB/Expo UKM atau hubungi langsung UKM lewat Instagram resminya / admin kampus. Data KB tidak memuat formulir, biaya, atau jadwal rekrutmen—jangan mengarang; konfirmasi ke pengurus UKM atau WA kampus +62 857-9920-5711.","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
  {"q":"Ada UKM investasi/pasar modal?","a":"Ada: KSPM GI ITB AAS Indonesia, fokus edukasi dan pelatihan pasar modal/investasi, terkait Galeri Investasi. Instagram: @kspmgi_itbaas.","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
  {"q":"Ada UKM untuk yang suka outdoor/alam?","a":"Ada: Mahasiswa Pencinta Alam (Devendra Maaspala), fokus kepedulian lingkungan dan kegiatan alam bebas. Instagram: @maaspala_itbaas.","source":"https://itbaas.id/unit-kegiatan-mahasiswa/"},
]
with open(ROOT/'data/faq.jsonl','a',encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False)+'\n')
print('appended', len(rows))
