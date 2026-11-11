"""
Penjadwalan Kegiatan Optimal (Activity Selection) - Metode BRUTE FORCE
======================================================================

Kasus 2 : Peminjaman satu auditorium kampus pada hari Sabtu. Ada 11 permohonan
          yang jadwalnya saling bertabrakan. Tujuannya menerima SEBANYAK MUNGKIN
          kegiatan tanpa tumpang tindih waktu.

Strategi brute force : coba SEMUA kemungkinan kombinasi kegiatan (semua subset,
                       2^n kombinasi), buang kombinasi yang ada kegiatan
                       bertabrakan, lalu ambil kombinasi dengan jumlah kegiatan
                       terbanyak. Kegiatan yang hanya bersentuhan (selesai 12:00,
                       mulai 12:00) dianggap TIDAK bentrok.

Kompleksitas         : O(2^n * n log n)  -> ada 2^n subset, tiap subset diurutkan
                       dan dicek bentrok. Tepat, tetapi hanya layak untuk n kecil.

Cara pakai
----------
    python activity_selection_bruteforce.py              # tampilkan semua tabel + hasil
    python activity_selection_bruteforce.py --benchmark  # + perbandingan waktu dgn greedy
    python -m unittest activity_selection_bruteforce     # jalankan unit test
"""

import sys
import time
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
# Algoritma brute force
# --------------------------------------------------------------------------
def subset_dari_mask(activities, mask):
    """Ubah bilangan biner menjadi subset. Bit ke-i menyala = kegiatan ke-i ikut."""
    return [activities[i] for i in range(len(activities)) if (mask >> i) & 1]


def tanpa_bentrok(subset):
    """True jika tidak ada dua kegiatan di subset yang tumpang tindih."""
    urut = sorted(subset, key=lambda a: to_min(a[2]))  # urut jam mulai
    for kiri, kanan in zip(urut, urut[1:]):
        if to_min(kiri[3]) > to_min(kanan[2]):  # kiri selesai SETELAH kanan mulai
            return False
    return True


def brute_force(activities):
    """
    Coba semua 2^n subset.

    Mengembalikan dict:
      total_subset  : banyak subset yang diperiksa (= 2^n)
      valid         : banyak subset tanpa bentrok
      maks          : jumlah kegiatan terbanyak yang bisa dijadwalkan
      optimal       : semua kombinasi (list kode) dengan jumlah = maks
      valid_per_ukuran : {ukuran: banyak subset valid berukuran itu}
    """
    n = len(activities)
    maks, optimal, valid = 0, [], 0
    per_ukuran = {}
    for mask in range(1 << n):  # 0 .. 2^n - 1
        subset = subset_dari_mask(activities, mask)
        if not tanpa_bentrok(subset):
            continue
        valid += 1
        ukuran = len(subset)
        per_ukuran[ukuran] = per_ukuran.get(ukuran, 0) + 1
        kode = [a[0] for a in subset]
        if ukuran > maks:
            maks, optimal = ukuran, [kode]
        elif ukuran == maks:
            optimal.append(kode)
    return {
        "total_subset": 1 << n,
        "valid": valid,
        "maks": maks,
        "optimal": optimal,
        "valid_per_ukuran": per_ukuran,
    }


def activity_selection_bf(activities):
    """Versi ringkas: satu solusi optimal (yang pertama ditemukan)."""
    hasil = brute_force(activities)
    return hasil["optimal"][0] if hasil["optimal"] else []


# --------------------------------------------------------------------------
# Pembanding (hanya untuk verifikasi dan benchmark, BUKAN bagian brute force)
# --------------------------------------------------------------------------
def greedy_pembanding(activities):
    """Greedy selesai-paling-awal, dipakai untuk membandingkan jumlah dan waktu."""
    hasil, akhir = [], -1
    for kode, _, mulai, selesai in sorted(activities, key=lambda a: to_min(a[3])):
        if to_min(mulai) >= akhir:
            hasil.append(kode)
            akhir = to_min(selesai)
    return hasil


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


def jadwal_str(kodes, info):
    """K3 08:30-09:30, K4 10:00-12:00, ... (urut jam mulai)."""
    urut = sorted(kodes, key=lambda k: to_min(info[k][2]))
    return "; ".join(f"{k} {info[k][2]}-{info[k][3]}" for k in urut)


def tampilkan_semua(activities=DATA):
    info = {a[0]: a for a in activities}
    n = len(activities)

    # 1. Tabel kasus
    cetak_tabel(
        "TABEL 1. DATA PERMOHONAN (urut berdasarkan kode)",
        ["Kode", "Kegiatan", "Mulai", "Selesai", "Durasi"],
        [[k, nm, m, s, durasi_str(to_min(s) - to_min(m))] for k, nm, m, s in activities],
    )

    hasil = brute_force(activities)

    # 2. Ringkasan pencarian
    cetak_tabel(
        "TABEL 2. RINGKASAN PENCARIAN BRUTE FORCE",
        ["Keterangan", "Nilai"],
        [
            ["Jumlah kegiatan (n)", n],
            ["Subset yang diperiksa (2^n)", f"2^{n} = {hasil['total_subset']}"],
            ["Subset tanpa bentrok (valid)", hasil["valid"]],
            ["Subset ditolak (ada bentrok)", hasil["total_subset"] - hasil["valid"]],
            ["Jumlah kegiatan terbanyak", hasil["maks"]],
            ["Banyak solusi optimal", len(hasil["optimal"])],
        ],
    )

    # 3. Subset per ukuran
    from math import comb
    cetak_tabel(
        "TABEL 3. SUBSET PER UKURAN (dari semua kombinasi, berapa yang tanpa bentrok)",
        ["Jumlah kegiatan", "Semua kombinasi C(n,k)", "Tanpa bentrok", "Keterangan"],
        [[k, comb(n, k), hasil["valid_per_ukuran"].get(k, 0),
          "<- TERBANYAK" if k == hasil["maks"] else ""] for k in range(0, hasil["maks"] + 2)],
    )

    # 4. Semua solusi optimal
    greedy = greedy_pembanding(activities)
    cetak_tabel(
        f"TABEL 4. SEMUA SOLUSI OPTIMAL ({hasil['maks']} kegiatan)",
        ["No", "Kegiatan", "Jadwal", "Sama dgn greedy?"],
        [[i, ", ".join(sorted(s, key=lambda k: to_min(info[k][2]))), jadwal_str(s, info),
          "ya" if sorted(s) == sorted(greedy) else ""] for i, s in enumerate(hasil["optimal"], 1)],
    )

    pertama = hasil["optimal"][0]
    ditolak = [a[0] for a in activities if a[0] not in pertama]
    print(f"\nSolusi optimal pertama : {', '.join(pertama)}")
    print(f"Jumlah maksimum        : {hasil['maks']} kegiatan dari {n} permohonan")
    print(f"Ditolak                : {len(ditolak)} kegiatan -> {', '.join(ditolak)}")
    print(f"Pembanding greedy      : {len(greedy)} kegiatan -> {', '.join(greedy)} "
          f"({'sama' if len(greedy) == hasil['maks'] else 'BERBEDA'} dengan brute force)")


def benchmark():
    """Bandingkan waktu brute force dan greedy untuk n yang makin besar."""
    import random
    rng = random.Random(42)
    baris = []
    for n in (8, 10, 12, 14, 16):
        acts = []
        for i in range(n):
            mulai = rng.randrange(8 * 60, 16 * 60, 30)
            selesai = mulai + rng.choice([30, 60, 90, 120, 180])
            acts.append((f"K{i + 1}", "x", f"{mulai // 60:02d}:{mulai % 60:02d}",
                         f"{selesai // 60:02d}:{selesai % 60:02d}"))
        t0 = time.perf_counter(); bf = brute_force(acts); t1 = time.perf_counter()
        g = greedy_pembanding(acts); t2 = time.perf_counter()
        baris.append([n, 2 ** n, f"{(t1 - t0) * 1000:.1f} ms", f"{(t2 - t1) * 1000:.3f} ms",
                      bf["maks"], len(g)])
    cetak_tabel(
        "TABEL 5. BENCHMARK: BRUTE FORCE vs GREEDY (data acak)",
        ["n", "Subset (2^n)", "Waktu brute force", "Waktu greedy", "Maks (BF)", "Hasil greedy"],
        baris,
    )
    print("Brute force membesar sekitar dua kali lipat setiap n bertambah 1; greedy hampir tidak terasa.")


# --------------------------------------------------------------------------
# Unit test
# --------------------------------------------------------------------------
class TestBruteForce(unittest.TestCase):
    def test_jumlah_maksimum_kasus(self):
        self.assertEqual(brute_force(DATA)["maks"], 5)

    def test_semua_subset_diperiksa(self):
        self.assertEqual(brute_force(DATA)["total_subset"], 2 ** len(DATA))

    def test_solusi_greedy_termasuk_solusi_optimal(self):
        optimal = [sorted(s) for s in brute_force(DATA)["optimal"]]
        self.assertIn(sorted(["K3", "K4", "K6", "K8", "K10"]), optimal)

    def test_semua_solusi_optimal_tidak_bentrok_dan_berukuran_maks(self):
        info = {a[0]: a for a in DATA}
        hasil = brute_force(DATA)
        for sol in hasil["optimal"]:
            self.assertEqual(len(sol), hasil["maks"])
            self.assertTrue(tanpa_bentrok([info[k] for k in sol]))

    def test_tidak_ada_solusi_lebih_besar(self):
        hasil = brute_force(DATA)
        self.assertNotIn(hasil["maks"] + 1, hasil["valid_per_ukuran"])

    def test_data_k6(self):
        k6 = next(a for a in DATA if a[0] == "K6")
        self.assertEqual((k6[2], k6[3]), ("12:00", "13:30"))

    def test_tanpa_bentrok(self):
        a = ("A", "x", "08:00", "09:00")
        b = ("B", "y", "09:00", "10:00")  # hanya bersentuhan -> boleh
        c = ("C", "z", "08:30", "09:30")  # menumpuk dengan A dan B -> bentrok
        self.assertTrue(tanpa_bentrok([a, b]))
        self.assertFalse(tanpa_bentrok([a, c]))
        self.assertFalse(tanpa_bentrok([b, c]))
        self.assertTrue(tanpa_bentrok([]))
        self.assertTrue(tanpa_bentrok([a]))

    def test_kasus_tepi(self):
        self.assertEqual(activity_selection_bf([]), [])
        self.assertEqual(brute_force([])["maks"], 0)
        self.assertEqual(activity_selection_bf([("A", "x", "08:00", "09:00")]), ["A"])
        self.assertEqual(sorted(activity_selection_bf(
            [("A", "x", "08:00", "09:00"), ("B", "y", "09:00", "10:00")])), ["A", "B"])
        self.assertEqual(len(activity_selection_bf(
            [("A", "x", "08:00", "10:00"), ("B", "y", "09:00", "11:00")])), 1)

    def test_sama_dengan_greedy_pada_data_acak(self):
        import random
        rng = random.Random(1)
        for _ in range(200):
            n = rng.randint(1, 9)
            acts = []
            for i in range(n):
                mulai = rng.randrange(8 * 60, 16 * 60, 30)
                selesai = mulai + rng.choice([30, 60, 90, 120, 180])
                acts.append((f"K{i + 1}", "x", f"{mulai // 60:02d}:{mulai % 60:02d}",
                             f"{selesai // 60:02d}:{selesai % 60:02d}"))
            self.assertEqual(brute_force(acts)["maks"], len(greedy_pembanding(acts)))

    def test_input_tidak_terurut_tetap_benar(self):
        self.assertEqual(brute_force(list(reversed(DATA)))["maks"], 5)


if __name__ == "__main__":
    tampilkan_semua()
    if "--benchmark" in sys.argv:
        benchmark()