from django.test import SimpleTestCase
from django.urls import reverse


class DashboardTest(SimpleTestCase):
    def test_dashboard_hanya_menampilkan_fokus_prediksi(self):
        response = self.client.get(reverse('portal:beranda'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prediksi Performa Akademik Mahasiswa')
        self.assertContains(response, 'Regresi Linear')
        self.assertNotContains(response, 'Pencarian BFS')
        self.assertNotContains(response, 'Algoritma Genetika')


class PrediksiTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from .ml.latih_model import MODEL, latih
        if not MODEL.exists():
            latih()

    RAJIN = {'Hours_Studied': 35, 'Attendance': 98, 'Previous_Scores': 90,
             'Tutoring_Sessions': 4}
    MALAS = {'Hours_Studied': 3, 'Attendance': 62, 'Previous_Scores': 55,
             'Tutoring_Sessions': 0}

    def test_prediksi_masuk_akal(self):
        from .services import prediksi
        rajin = prediksi.prediksi(self.RAJIN)
        malas = prediksi.prediksi(self.MALAS)
        self.assertGreater(rajin, malas)
        self.assertTrue(0 <= malas <= rajin <= 100)

    def test_urutan_fitur_sama_dengan_model(self):
        from .ml.latih_model import FITUR
        from .services import prediksi
        self.assertEqual(list(prediksi.muat_model().feature_names_in_), FITUR)

    def test_pembersihan_data(self):
        from .ml.latih_model import TARGET, muat_data
        df = muat_data()
        self.assertEqual(len(df), 6606)
        self.assertLessEqual(df[TARGET].max(), 100)

    def test_batas_form_sama_dengan_rentang_data(self):
        from .forms import PrediksiForm
        from .services import prediksi
        rentang = prediksi.muat_metrik()['rentang']
        form = PrediksiForm()
        for nama, (minimum, maksimum) in rentang.items():
            self.assertEqual(form.fields[nama].min_value, minimum, nama)
            self.assertEqual(form.fields[nama].max_value, maksimum, nama)

    def test_halaman_prediksi_menampilkan_hasil(self):
        response = self.client.get(reverse('portal:prediksi'), {
            'Hours_Studied': 20, 'Attendance': 85, 'Previous_Scores': 75,
            'Tutoring_Sessions': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prediksi nilai ujian')
        self.assertContains(response, 'Predikat')

    def test_input_di_luar_rentang_ditolak(self):
        response = self.client.get(reverse('portal:prediksi'), {
            'Hours_Studied': 99, 'Attendance': 85, 'Previous_Scores': 75,
            'Tutoring_Sessions': 1})
        self.assertNotContains(response, 'Predikat')

    def test_grafik_menampilkan_kelompok_data(self):
        from .services import prediksi
        grafik = prediksi.data_grafik()
        self.assertEqual(len(grafik), 6)
        self.assertTrue(all(item['n'] > 0 for item in grafik))


class AITest(SimpleTestCase):
    def setUp(self):
        from .services import ai
        ai._waktu_panggilan.clear()
        from .ml.latih_model import MODEL, latih
        if not MODEL.exists():
            latih()

    def test_prompt_prediksi_memuat_input_dan_dataset(self):
        from unittest import mock
        with mock.patch('portal.services.ai.tanya', return_value='Penjelasan uji') as panggil:
            response = self.client.post(reverse('portal:ai_jelaskan'), {
                'Hours_Studied': '25', 'Attendance': '90',
                'Previous_Scores': '80', 'Tutoring_Sessions': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'teks': 'Penjelasan uji'})
        prompt = panggil.call_args.args[0]
        self.assertIn('25 jam/minggu', prompt)
        self.assertIn('Student Performance Factors', prompt)

    def test_input_tidak_valid_tidak_memanggil_groq(self):
        from unittest import mock
        with mock.patch('portal.services.ai.tanya') as panggil:
            response = self.client.post(reverse('portal:ai_jelaskan'), {
                'Hours_Studied': '99', 'Attendance': '90',
                'Previous_Scores': '80', 'Tutoring_Sessions': '2'})
        self.assertEqual(response.status_code, 400)
        panggil.assert_not_called()

    def test_endpoint_hanya_post(self):
        response = self.client.get(reverse('portal:ai_jelaskan'))
        self.assertEqual(response.status_code, 405)

    def test_kunci_tidak_bocor_ke_halaman(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {'GROQ_API_KEY': 'KUNCI_RAHASIA_UJI'}):
            response = self.client.get(reverse('portal:beranda'))
        self.assertNotContains(response, 'KUNCI_RAHASIA_UJI')

    def test_tanpa_kunci_ditolak_dengan_pesan_jelas(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('GROQ_API_KEY', None)
            response = self.client.post(reverse('portal:ai_jelaskan'), {
                'Hours_Studied': '25', 'Attendance': '90',
                'Previous_Scores': '80', 'Tutoring_Sessions': '2'})
        self.assertEqual(response.status_code, 503)
        self.assertIn('GROQ_API_KEY', response.json()['galat'])
