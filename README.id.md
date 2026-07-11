[English](README.md) | [Bahasa Indonesia](README.id.md)

# RAG Chatbot API

Chatbot berbasis Retrieval-Augmented Generation (RAG) yang dilayani melalui HTTP menggunakan FastAPI. Pengguna dapat mengunggah berkas PDF, lalu mengajukan pertanyaan mengenai isinya. Jawaban yang diberikan selalu didasarkan pada dokumen yang diunggah dan dilengkapi dengan rujukan sumber. Apabila informasi yang ditanyakan tidak terdapat dalam dokumen, chatbot akan menyatakannya secara jujur alih-alih mengarang jawaban.

## Fitur

- Mengunggah berkas PDF yang secara otomatis diekstraksi, dipecah menjadi potongan (chunk), diubah menjadi vektor, dan disimpan ke basis data.
- Mengajukan pertanyaan melalui endpoint `/chat` dan memperoleh jawaban yang didasarkan pada isi dokumen.
- Setiap jawaban menyertakan nama berkas sumber yang digunakan.
- Terdapat mekanisme pengaman (guardrail) yang mencegah model mengarang: jika jawaban tidak ditemukan dalam dokumen, model akan menyatakan bahwa informasi tersebut tidak tersedia.
- Setiap unggahan baru menggantikan dokumen sebelumnya, sehingga pertanyaan hanya mengacu pada PDF terkini.
- Berkas selain PDF akan ditolak disertai pesan kesalahan yang jelas.

## Teknologi yang Digunakan

- Model bahasa: Groq (Llama 3.3 70B)
- Embedding: sentence-transformers (`all-MiniLM-L6-v2`, berdimensi 384)
- Basis data vektor: ChromaDB (persisten)
- Pembacaan PDF: pypdf
- Antarmuka API: FastAPI dan Uvicorn
- Konfigurasi: python-dotenv

## Cara Kerja

Sistem ini memiliki dua alur utama.

Pada saat pengunggahan, berkas PDF dibaca menjadi teks, dipecah menjadi beberapa potongan yang saling bertumpang tindih, diubah menjadi vektor embedding, lalu disimpan ke dalam ChromaDB.

Pada saat percakapan, pertanyaan yang masuk diubah menjadi vektor dan dibandingkan dengan potongan-potongan yang tersimpan. Potongan yang paling relevan diambil, dirangkai menjadi sebuah prompt bersama instruksi pengaman, kemudian dikirim ke model bahasa Groq. Model mengembalikan jawaban yang didasarkan pada potongan tersebut, beserta daftar berkas sumber yang berhasil diambil.

## Struktur Proyek

### `api/`

**`main.py`** — Aplikasi FastAPI beserta seluruh endpoint HTTP. Berkas ini mendefinisikan bentuk permintaan dan respons (melalui model Pydantic) serta menghubungkan seluruh komponen RAG.

- `POST /chat` menerima `{"question": "..."}` dan mengembalikan `{"answer": "...", "sources": [...]}`.
- `POST /upload` menerima berkas PDF, lalu mengekstraksi, memecah, dan mengindeksnya. Berkas selain PDF ditolak dengan kode kesalahan 400, dan basis data dikosongkan terlebih dahulu agar hanya PDF terbaru yang dapat ditelusuri.
- `GET /` merupakan pemeriksaan kesehatan (health check) yang mengembalikan `{"status": "ok"}`.

### `core/` (mesin RAG)

**`loader.py`** — Membaca dokumen teks biasa (`.txt` dan `.md`) serta menyimpan nama berkas sumber agar rujukan dapat berfungsi di tahap berikutnya.

**`pdf_loader.py`** — Fungsi `extract_text_from_pdf(file_path)` membuka berkas PDF menggunakan pypdf, menelusuri setiap halaman, mengambil teksnya (melewati halaman kosong), dan menggabungkannya menjadi satu teks utuh.

**`chunker.py`** — Fungsi `chunk_text(text, chunk_size=500, overlap=50)` memecah dokumen panjang menjadi potongan-potongan yang saling bertumpang tindih. Tumpang tindih ini menjaga keterkaitan konteks antarpotongan sehingga tidak ada gagasan yang terpotong di tengah.

**`embedder.py`** — Mengubah teks menjadi vektor (embedding) menggunakan model sentence-transformers yang dimuat satu kali pada saat impor. Vektor berdimensi 384 inilah yang memungkinkan penelusuran secara semantik.

**`vectorstore.py`** — Pembungkus (wrapper) ChromaDB yang berperan sebagai memori sistem.

- `index_chunks(chunks, source)` mengubah potongan menjadi vektor dan menyimpannya beserta metadata sumber.
- `retrieve(query, top_k=3)` mengubah pertanyaan menjadi vektor dan mengembalikan potongan yang paling relevan beserta sumbernya.
- `reset_collection()` mengosongkan koleksi, digunakan sebelum setiap unggahan agar hanya dokumen terbaru yang dapat ditelusuri.

**`generator.py`** — Tahap penyusunan jawaban.

- `build_context(chunks)` merangkai potongan-potongan hasil penelusuran menjadi satu blok teks, dengan menandai setiap potongan menggunakan label sumbernya.
- `answer(query, top_k=3)` mengambil konteks, menyusun prompt beserta pengaman, memanggil model bahasa Groq, lalu mengembalikan jawaban beserta daftar sumber.

### Skrip Pengujian

Skrip berikut dijalankan langsung untuk keperluan verifikasi manual.

- **`test_key.py`** memastikan kunci API Groq berfungsi dan model memberikan respons.
- **`test_rag.py`** menguji alur penelusuran secara menyeluruh (mengindeks lalu mengambil kembali).
- **`test_generator.py`** menguji alur jawaban secara lengkap, termasuk pengaman pada pertanyaan yang jawabannya tidak terdapat dalam dokumen.
- **`test_pdf.py`** menguji fungsi `extract_text_from_pdf` secara mandiri terhadap sebuah berkas PDF.

### Konfigurasi

- **`requirements.txt`** — Daftar dependensi. Perbarui dengan perintah `pip freeze > requirements.txt`.
- **`.env`** — Menyimpan `GROQ_API_KEY`. Jangan pernah menyertakan berkas ini ke dalam repositori.
- **`.gitignore`** — Mengecualikan `venv/`, `.env`, `chroma_db/`, dan `data/`.

## Pemasangan (Lokal)

    git clone https://github.com/tndsny/rag-chatbot-api.git
    cd rag-chatbot-api

    python -m venv venv
    venv\Scripts\activate

    pip install -r requirements.txt

    echo GROQ_API_KEY=kunci_anda_di_sini > .env

    uvicorn api.main:app --reload

Selanjutnya, buka http://127.0.0.1:8000/docs untuk mengakses antarmuka Swagger yang interaktif.

## Cara Penggunaan

1. Unggah berkas PDF melalui `POST /upload`.
2. Ajukan pertanyaan melalui `POST /chat` dengan format `{"question": "pertanyaan Anda di sini"}`.
3. Anda akan menerima jawaban yang didasarkan pada dokumen beserta rujukannya. Pertanyaan di luar cakupan dokumen akan memperoleh penolakan yang sopan.

## Rencana Pengembangan

- Merotasi kunci API Groq
- Observability (pencatatan log terstruktur dan pelacakan permintaan)
- Evaluasi (pengukuran kualitas jawaban)
- Mode multidokumen (opsional)
- Penerapan (deploy) ke Hugging Face Spaces menggunakan Docker