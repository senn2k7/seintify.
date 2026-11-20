from django import forms


class PrediksiForm(forms.Form):
    """Nama field mengikuti kolom fitur dataset; batas mengikuti data latih."""
    Hours_Studied = forms.IntegerField(
        label='Jam belajar per minggu', min_value=1, max_value=44, initial=20)
    Attendance = forms.IntegerField(
        label='Kehadiran kuliah (%)', min_value=60, max_value=100, initial=80)
    Previous_Scores = forms.IntegerField(
        label='Nilai sebelumnya (0-100)', min_value=50, max_value=100,
        initial=75)
    Tutoring_Sessions = forms.IntegerField(
        label='Sesi bimbingan per bulan', min_value=0, max_value=8, initial=1)
