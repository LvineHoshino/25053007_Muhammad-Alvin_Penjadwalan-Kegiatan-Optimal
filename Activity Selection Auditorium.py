"""
Penjadwalan Kegiatan Optimal (Activity Selection) - Metode Greedy
=================================================================

Kasus 2 : Peminjaman satu auditorium kampus pada hari Sabtu. Ada 11 permohonan
        yang jadwalnya saling bertabrakan. Tujuannya menerima SEBANYAK MUNGKIN
        kegiatan tanpa tumpang tindih waktu.

Strategi greedy : urutkan kegiatan berdasarkan waktu SELESAI paling awal, lalu
                  pilih kegiatan jika jam mulainya >= jam selesai kegiatan
                  terakhir yang sudah dipilih. Kegiatan yang hanya bersentuhan
                  (selesai 12:00, mulai 12:00) dianggap TIDAK bentrok.

Kompleksitas    : O(n log n) karena pengurutan; pemilihannya sendiri O(n).


"""

import itertools
import unittest

# (kode, nama kegiatan, jam mulai, jam selesai)
DATA = [
    ("K1", "Seminar Nasional", "08:00", "13:00"),
    ("K2", "Workshop UI/UX", "09:00", "11:30"),
    ("K3", "Rapat BEM", "08:30", "09:30"),
    ("K4", "Pelatihan Excel", "10:00", "12:00"),
    ("K5", "Lomba Debat", "11:00", "13:00"),
    ("K6", "Bedah Buku", "12:00", "13:30"),
    ("K7", "Kelas Yoga", "13:00", "14:00"),
    ("K8", "Rapat Dosen", "13:30", "15:30"),
    ("K9", "Gladi Wisuda", "14:00", "16:00"),
    ("K10", "Pentas Seni", "15:30", "17:30"),
    ("K11", "Seminar Karier", "12:30", "14:30"),
]


# --------------------------------------------------------------------------
# Utilitas waktu
# --------------------------------------------------------------------------
def to_min(t):
    """'13:30' -> 810 (menit sejak 00:00)."""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def durasi_str(menit):
    """90 -> '1 jam 30 menit', 120 -> '2 jam'."""
    h, m = divmod(menit, 60)
    if h and m:
        return f"{h} jam {m} menit"
    return f"{h} jam" if h else f"{m} menit"


# --------------------------------------------------------------------------
# Algoritma
# --------------------------------------------------------------------------
def urut_selesai(activities):
    """Urut berdasarkan jam selesai; jika sama, yang mulai lebih awal dulu."""
    return sorted(activities, key=lambda a: (to_min(a[3]), to_min(a[2])))


def greedy_trace(activities):
    """
    Jalankan greedy dan kembalikan (terpilih, langkah).

    terpilih : daftar kode kegiatan yang diterima
    langkah  : daftar dict, satu per kegiatan, berisi bahan untuk tabel langkah
    """
    terpilih, langkah = [], []
    akhir_terakhir = None  # jam selesai kegiatan terakhir yang dipilih (menit)

    for urutan, (kode, nama, mulai, selesai) in enumerate(urut_selesai(activities), 1):
        if akhir_terakhir is None:
            lolos, cek = True, "kegiatan pertama"
        else:
            lolos = to_min(mulai) >= akhir_terakhir
            tanda = ">=" if lolos else "<"
            cek = f"{mulai} {tanda} {_hhmm(akhir_terakhir)}"

        langkah.append({
            "urutan": urutan, "kode": kode, "nama": nama,
            "mulai": mulai, "selesai": selesai,
            "akhir_terakhir": "-" if akhir_terakhir is None else _hhmm(akhir_terakhir),
            "cek": cek, "lolos": lolos,
        })
        if lolos:
            terpilih.append(kode)
            akhir_terakhir = to_min(selesai)

    return terpilih, langkah


def activity_selection(activities):
    """Versi ringkas: hanya mengembalikan kode kegiatan yang terpilih."""
    return greedy_trace(activities)[0]


def _hhmm(menit):
    return f"{menit // 60:02d}:{menit % 60:02d}"


# --------------------------------------------------------------------------
# Strategi pembanding (untuk menunjukkan kenapa 'selesai paling awal' benar)
# --------------------------------------------------------------------------
def _pilih_berurutan(ordered):
    hasil, akhir = [], -1
    for kode, _, mulai, selesai in ordered:
        if to_min(mulai) >= akhir:
            hasil.append(kode)
            akhir = to_min(selesai)
    return hasil


def by_durasi_terpendek(activities):
    return _pilih_berurutan(sorted(activities, key=lambda a: to_min(a[3]) - to_min(a[2])))


def by_mulai_paling_awal(activities):
    return _pilih_berurutan(sorted(activities, key=lambda a: to_min(a[2])))


def brute_force_maks(activities):
    """Jumlah maksimum kegiatan dengan mencoba semua subset (hanya untuk n kecil)."""
    for r in range(len(activities), 0, -1):
        for sub in itertools.combinations(activities, r):
            s = sorted(sub, key=lambda a: to_min(a[2]))
            if all(to_min(s[i][3]) <= to_min(s[i + 1][2]) for i in range(len(s) - 1)):
                return r
    return 0


# --------------------------------------------------------------------------
# Pencetak tabel teks (tanpa library tambahan)
# --------------------------------------------------------------------------
def cetak_tabel(judul, header, baris):
    baris = [[str(c) for c in r] for r in baris]
    lebar = [max(len(str(h)), *(len(r[i]) for r in baris)) for i, h in enumerate(header)]
    garis = "+-" + "-+-".join("-" * w for w in lebar) + "-+"

    def fmt(r):
        return "| " + " | ".join(c.ljust(lebar[i]) for i, c in enumerate(r)) + " |"

    print(f"\n{judul}")
    print(garis)
    print(fmt(header))
    print(garis)
    for r in baris:
        print(fmt(r))
    print(garis)


def tampilkan_semua(activities=DATA):
    info = {a[0]: a for a in activities}

    # 1. Tabel kasus
    cetak_tabel(
        "TABEL 1. DATA PERMOHONAN (urut berdasarkan kode)",
        ["Kode", "Kegiatan", "Mulai", "Selesai", "Durasi"],
        [[k, n, m, s, durasi_str(to_min(s) - to_min(m))] for k, n, m, s in activities],
    )

    # 2. Tabel langkah greedy
    terpilih, langkah = greedy_trace(activities)
    cetak_tabel(
        "TABEL 2. LANGKAH GREEDY (diurutkan berdasarkan jam selesai)",
        ["No", "Kode", "Kegiatan", "Mulai", "Selesai", "Akhir terakhir", "Cek mulai >= akhir", "Keputusan"],
        [[l["urutan"], l["kode"], l["nama"], l["mulai"], l["selesai"],
          l["akhir_terakhir"], l["cek"], "PILIH" if l["lolos"] else "TOLAK"] for l in langkah],
    )

    # 3. Jadwal akhir
    cetak_tabel(
        "TABEL 3. JADWAL AKHIR AUDITORIUM",
        ["No", "Kode", "Kegiatan", "Jam", "Durasi"],
        [[i, k, info[k][1], f"{info[k][2]} - {info[k][3]}",
          durasi_str(to_min(info[k][3]) - to_min(info[k][2]))]
         for i, k in enumerate(terpilih, 1)],
    )
    ditolak = [a[0] for a in activities if a[0] not in terpilih]
    print(f"\nDiterima : {len(terpilih)} kegiatan -> {', '.join(terpilih)}")
    print(f"Ditolak  : {len(ditolak)} kegiatan -> {', '.join(ditolak)}")

    # 4. Perbandingan strategi
    def total_menit(kodes):
        return sum(to_min(info[k][3]) - to_min(info[k][2]) for k in kodes)

    strategi = [
        ("Selesai paling awal (greedy)", terpilih),
        ("Durasi terpendek", by_durasi_terpendek(activities)),
        ("Mulai paling awal", by_mulai_paling_awal(activities)),
    ]
    optimal = brute_force_maks(activities)
    cetak_tabel(
        "TABEL 4. PERBANDINGAN STRATEGI",
        ["Strategi", "Terpilih", "Jumlah", "Jam terpakai", "Status"],
        [[nama, ", ".join(k), len(k), durasi_str(total_menit(k)),
          "OPTIMAL" if len(k) == optimal else f"kurang {optimal - len(k)}"]
         for nama, k in strategi],
    )
    print(f"\nJumlah maksimum sebanyak mungkin kegiatan yang dapat dilakukan tanpa tumpang tindih waktu: {optimal}")


# --------------------------------------------------------------------------
# Unit test
# --------------------------------------------------------------------------
class TestActivitySelection(unittest.TestCase):
    def test_kasus_auditorium(self):
        self.assertEqual(activity_selection(DATA), ["K3", "K4", "K6", "K8", "K10"])

    def test_optimal_menurut_brute_force(self):
        self.assertEqual(len(activity_selection(DATA)), brute_force_maks(DATA))

    def test_strategi_lain_tidak_optimal(self):
        self.assertEqual(by_durasi_terpendek(DATA), ["K3", "K7", "K9"])
        self.assertEqual(by_mulai_paling_awal(DATA), ["K1", "K7", "K9"])

    def test_data_k6(self):
        k6 = next(a for a in DATA if a[0] == "K6")
        self.assertEqual((k6[2], k6[3]), ("12:00", "13:30"))

    def test_tidak_ada_tumpang_tindih(self):
        info = {a[0]: a for a in DATA}
        pilih = sorted(activity_selection(DATA), key=lambda k: to_min(info[k][2]))
        for a, b in zip(pilih, pilih[1:]):
            self.assertLessEqual(to_min(info[a][3]), to_min(info[b][2]))

    def test_trace_konsisten_dengan_hasil(self):
        terpilih, langkah = greedy_trace(DATA)
        self.assertEqual(terpilih, [l["kode"] for l in langkah if l["lolos"]])
        self.assertEqual(len(langkah), len(DATA))

    def test_kasus_tepi(self):
        self.assertEqual(activity_selection([]), [])
        self.assertEqual(activity_selection([("A", "x", "08:00", "09:00")]), ["A"])
        # hanya bersentuhan -> keduanya boleh
        self.assertEqual(
            activity_selection([("A", "x", "08:00", "09:00"), ("B", "y", "09:00", "10:00")]),
            ["A", "B"],
        )
        # bertumpuk -> hanya satu (yang selesai lebih awal)
        self.assertEqual(
            activity_selection([("A", "x", "08:00", "10:00"), ("B", "y", "09:00", "11:00")]),
            ["A"],
        )

    def test_input_tidak_terurut_tetap_benar(self):
        self.assertEqual(activity_selection(list(reversed(DATA))), ["K3", "K4", "K6", "K8", "K10"])


if __name__ == "__main__":
    tampilkan_semua()