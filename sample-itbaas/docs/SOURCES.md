# Sumber & catatan verifikasi

Tanggal akses: 2026-11-06.

## Situs resmi
- `https://itbaas.id/` — WordPress, konten utama 2026, Yoast sitemap. Dipakai sebagai canonical untuk KB.
- `https://itbaas.ac.id/` — mirror/domain resmi; dipakai untuk slug yang tidak ada di `.id` (`s2-manajemen`, `beasiswa-2`) dan untuk cross-check.
- `https://pmb.itbaas.ac.id/` — siAkad/SEVIMA front PMB; halaman jalur seleksi, program studi, pengumuman, informasi, user-guide disimpan di `pages/`.
- `https://id.wikipedia.org/wiki/Institut_Teknologi_Bisnis_AAS_Indonesia` — referensi pihak ketiga; dipakai untuk sejarah/Pimpinan, bukan sumber legal final.

## Endpoint yang dipakai
- Yoast sitemap: `/sitemap.xml`, `/post-sitemap.xml`, `/page-sitemap.xml`, `/category-sitemap.xml`, `/post_tag-sitemap.xml`, `/author-sitemap.xml`
- WP REST API: `/wp-json/wp/v2/{posts,pages,categories,tags,users,media}` (`per_page=100`, paginated; media hanya metadata)
- `itbaas.id` counts: posts 352, pages 40, categories 25, tags 992, media 541
- `itbaas.ac.id` counts: posts 189, pages 33, categories 7, tags 248, media 292
- overlap posts 159 slug; 30 hanya di `.ac.id`, 193 hanya di `.id`

## Legal/akreditasi yang perlu dicek manual
- PDDIKTI: `https://pddikti.kemdikbud.go.id/data_pt/QTg3NkQ1NzctMDdDMi00MjMzLTk5QkMtODY3QTg0Q0U5ODcx` (tidak bisa diakses saat build; transport error)
- BAN-PT Bianglala: `https://www.banpt.or.id/bianglala/bianglala.php`
- LAM-PT (untuk prodi terapan/kesehatan/ekonomi): cek sesuai prodi
- LLDIKTI Wilayah VI: penggabungan Akbid Giri Satria Husada → ITB AAS (2024) disebut di post resmi

## Kampus 2
- `https://itbaas.id/asesmen-lapangan-program-studi-s1-akuntansi/` — resmi menyebut Kampus 2: Jl. Hamzah Raya, Dusun III, Gumpang, Kec. Kartasura, Kabupaten Sukoharjo.
- `https://itbaas.id/peletakan-batu-pertama-pembangunan-gedung-blk-komunitas-teknik-informatika/` dan `https://itbaas.ac.id/pembangunan-gedung-blk-komunitas-teknik-informatika/` — BLKK Yayasan Amaliyah Ilmi Surakarta/Kampus 2; cek arsip bila butuh detail konstruksi/lokasi.
- `https://itbaas.id/jalan-sehat-dalam-rangka-tasyakuran-keberhasilan-penyatuan-kampus-itb-aas-indonesia-dengan-akademi-kebidanan-giri-satria-husada-wonogiri/` — menjelaskan Kampus 2 dan konteks penyatuan Akbid Giri Satria Husada.

## UKM / kemahasiswaan
- `https://itbaas.id/unit-kegiatan-mahasiswa/` — daftar BEM/HIMA/UKM + Instagram; dipakai untuk `data/ukm.json`.
- `https://itbaas.id/unit-kegitan-mahasiswa-copy/` — penjelasan umum UKM; ada placeholder Lorem ipsum untuk KOPMA/KSPM, jadi deskripsi utama pakai halaman pertama.
- `https://itbaas.id/prestasi-mahasiswa/` dan `https://itbaas.id/category/prestasi/` — prestasi mahasiswa.

## Dokumen Unduh (link Google Drive, belum diunduh)
Lihat `data/downloads.csv`. Berisi logo, pedoman TA/KKN, aplikasi SPSS/MYOB/Mendeley/Accurate/E-SPT, sertifikat institusi dan prodi. Link Drive bisa berubah/permission; unduh manual bila perlu arsip lokal.

## Klaim yang harus diberi label "post website, verifikasi"
- S1 Informatika "Akreditasi Unggul" dan kurikulum AI 40%
- Biaya mulai Rp350–400 ribu/bulan; bebas biaya SKS/UTS/UAS
- KIP Kuliah uang saku Rp4,8 juta/tahun; gratis sampai lulus
- RPL Rp16–20 juta sampai lulus; cicilan 5 kali
- S2 Manajemen mulai Rp21 juta; diskon alumni 50%; dual degree M.M./MBA Thailand; 3 semester
- "Kampus terbaik", "terjangkau", "Solo Raya" — marketing

## Fakta stabil (silang beberapa sumber)
- Lokasi: Jl. Slamet Riyadi No. 361 Windan, Makamhaji, Kartasura, Sukoharjo 57161
- Telepon: (0271) 726156; WA: 0857-9920-5711 / 0889-8337-3916 (PMB)
- Email: itbaas.indonesia@gmail.com; info@itbaas.ac.id; pmb@itbaas.ac.id
- Pengelola: Yayasan Amaliyah Ilmi Surakarta
- SK Institut: Mendikbud No. 192/M/2020 (31 Jan 2020)
- SK BAN-PT PPJ: 700/SK/BAN-PT/Ak.Ppj/PT/X/2023 (3 Okt 2023)
- Sejarah: 1984 Bentara → 2007 AAS → 2014 STIE AAS → 2020 Institut → 2024 prodi baru/penggabungan Akbid

## Kontak verifikasi
Untuk data yang akan dipublish, minta konfirmasi tertulis/sertifikat ke: PMB `pmb@itbaas.ac.id`, WA `+62 857-9920-5711`, telp `(0271) 726156`.
