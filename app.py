#import module
from flask import Flask, url_for, redirect, request, render_template
from mysql import connector

#menghubungkan ke database
db = connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'db_kasir'
)
if db.is_connected():
    print("[!] Database Terhubung [!]")

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
# function untuk menampilkan halaman index dan data yang diambil dari tabel nota
def index():
    # mengambil data dari tabel nota
    # variabel nota dan total dibuat jadi global agar bisa diakses fungsi hitung
    cur = db.cursor()
    cur.execute("SELECT * FROM nota")
    global nota
    nota = cur.fetchall()
    cur.close()

    # menjumlahkan harga total
    global total
    total = 0
    for i in nota:
        total = total + int(i[4])

    # menampilkan tabel nota dan total ke halaman index
    return render_template('index.html', notaindex = nota, totalindex = total)

@app.route('/process_add', methods = ['POST'])
# function untuk menjumlahkan total harga item * qty
def process_add():
    id = request.form['id_produk']
    qty = request.form['qty_produk']

    # mengambil harga produk dari tabel barang
    cur = db.cursor()
    cur.execute("SELECT * FROM barang where id=%s", (id,))
    item = cur.fetchone()
    cur.close()

    # menjumlahkan harga barang per jumlah (qty)
    nama = item[1]
    harga = item[2]
    total_item = int(qty) * int(harga)

    # data harga dan barang yang sudah dijumlahkan dimasukkan ke tabel nota.
    cur = db.cursor()
    cur.execute("INSERT INTO nota (id_produk, nama, qty, harga, total) VALUES (%s,%s,%s,%s,%s)", (id, nama, qty, harga, total_item))
    db.commit()
    return redirect(url_for('index'))

# fungsi hitung untuk menghitung kembalian.
@app.route('/hitung', methods = ['POST'])
def hitung():
    uang = int(request.form['bayar'])
    bayar = total
    kembali = uang-bayar
    return render_template('index.html', kembaliindex = kembali, totalindex=total, notaindex=nota )

# function untuk hapus isi tabel nota (reset)
@app.route('/reset')
def reset():
    cur = db.cursor()
    cur.execute("DELETE FROM nota")
    db.commit()
    return redirect(url_for('index'))

# function untuk masuk halaman admin
@app.route('/admin')
def adminpage():
    cur = db.cursor()
    cur.execute("SELECT * FROM barang")
    res = cur.fetchall()
    cur.close()
    return render_template('admin.html', hasil=res)

# function untuk masuk halaman tambah
@app.route('/tambah/')
def tambah_data():
    return render_template('tambah.html')

# function proses tambah barang
@app.route('/proses_tambah/', methods=['POST'])
def proses_tambah():
    nama = request.form['nama_barang']
    harga = int(request.form['harga_barang'])
    cur = db.cursor()
    cur.execute("INSERT INTO barang (id, nama_barang, harga_barang) VALUES (%s, %s, %s)", (None, nama, harga))
    db.commit()
    return redirect(url_for('adminpage'))

# function untuk masuk halaman ubah barang
@app.route('/ubah/<id>', methods=['GET'])
def ubah_data(id):
    cur = db.cursor()
    cur.execute('SELECT * FROM barang WHERE id=%s', (id,))
    res = cur.fetchall()
    cur.close()
    return render_template('ubah.html', hasil=res)

# function untuk proses ubah barang
@app.route('/proses_ubah/', methods=['POST'])
def proses_ubah():
    id_ori = request.form['id_ori']
    id = request.form['id']
    nama = request.form['nama']
    harga = request.form['harga']
    cur = db.cursor()
    sql = "UPDATE barang SET id=%s, nama_barang=%s, harga_barang=%s WHERE id=%s"
    value = (id, nama, harga, id_ori)
    cur.execute(sql, value)
    db.commit()
    return redirect(url_for('adminpage'))

# function untuk hapus barang
@app.route('/hapus/<id>', methods=['GET'])
def hapus_data(id):
    cur = db.cursor()
    cur.execute('DELETE FROM barang WHERE id=%s', (id,))
    db.commit()
    return redirect(url_for('adminpage'))

if __name__ == '__main__':
    app.run()