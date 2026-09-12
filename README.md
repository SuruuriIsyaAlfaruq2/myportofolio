Nama : Suruuri Isya Alfaruq

NPM : 2506548080

Kelas : PBP E


### Tugas 1

1. Saya menggunakan <Section> untuk membantu saya memisahkan topik yang ingin ditampilkan. Section saya terbagi menjadi 3 bagian, Section Profile, Skills, dan Educations
2. Tantangan saya yaitu ketika perlu menentukan tampilan responsive adalah menentukan seberapa lebar maksimal yang diterima oleh page mobile, saya harus menyesuaikan lebarnya dan memastikan elemen tetap di tengah meskipun berganti ke mobile. Dan juga pada bagian skills pada desktop saya menggunakan grid sejajar antara hardskills dan softskills, namun pada mobile tampilannya saya ubah menjadi grid 1-1 vertikal supaya tetap muat pada layar mobile.
3. Saya sebetulnya ingin membuat tampilan web di mana ketika elemen tersebut sedang tidak terlihat di layar tetapi ketika di scroll akan fade-in. saya menantikan penerapan fitur ini karena saya dengar membutuhkan javascript. Selain itu ketika penambahan konten seperti penmabahan skill di masa depan, jika static maish perlu edit di html.

Dalam pengerjaan Tugas 1 ini saya menggunakan Gemini AI untuk membantu saya brainstorming mengenai attribut yang sebaiknya digunakan pada css. Sebagai contoh pada garis timeline education, awalnya saya menggunakan div namun hasilnya berantakan, ekhirnya saya bertanya ke AI dan mendapatkan rekomendasi penggunaan Span sebagai ganti div. serta AI sebagai alat bantu penentuan attribut @media untuk tampilan mobile


### Tugas 2

1. Pengguna membuka website dengan URL -> Browser mengirimkan HTTP Request -> Request masuk ke urls.py pada folder project -> jika request menuju ke aplikasi, maka dari urls.py pada projek akan meneruskan request ke urls.py pada main -> pada urls.py pada main akan meneruskan request yang cocok ke views.py main -> dari views.py jika membutuhkan data dari models.py akan menuju models.py untuk mengambil data yang dibutuhkan -> kemudian views.py akan render template html yang sesuai juga meneruskan data yang sebelumnya diambil -> views.py kemudian akan mengembalikan halaman template html tadi ke browser pengguna 
2. Jika disatukan pada 1 file, maka jika ada banyak penambahan data akan mempersulit developer karena harus mengetik ulang 1-1 serta juga harus menghapus dengan resiko terhapus semua. namun jika dipisah pada models akan mempermudah penambahan maupun penghapusan data. Selain itu jika disimpan pada models dapat mencantumkan attribute rahasia yang tidak perlu ditampilkan di halaman web namun nantinya diperlukan untuk pengembangan aplikasi seperti adanya id. 
3. makemigrations adalah perintah untuk mengecek apakah adanya perubahan pada models.py. Jika ada perubahan maka akan menciptakan berkas migrasi yang berisi perubahan model yang belum diaplikasikan ke dalam basis data supaya nantinya dapat menjadi acuan dalam struktur data tabel pada database. Sedangkan migrate mengaplikasikan perubahan model yang tercantum dalam berkas migrasi ke basis data dengan menjalankan perintah sebelumnya. Contoh perubahan yang mengharuskan untuk menjalankan kedua perintah yaitu jika ada penambahan class pada models.py. Seperti yang saya lakukan, ketika saya membuat class Skills pada models.py dengan segala attributenya. saya perlu menjalankan kedua perintah supaya ada berkas migrasinya dan kemudian mengaplikasikannya ke database. Dengan itu saya dapat menambahkan data tentang skills pada databse tanpa perlu mengetik 1-1.


 