from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import PrediksiForm
from .services import ai as ai_layanan
from .services import prediksi as prediksi_layanan


def beranda(request):
    """Dashboard ringkas yang hanya menampilkan proyek Prediksi ML."""
    try:
        metrik = prediksi_layanan.muat_metrik()
        siap = prediksi_layanan.MODEL.exists()
    except prediksi_layanan.ModelBelumAda:
        metrik, siap = None, False
    return render(request, 'portal/beranda.html', {
        'metrik': metrik,
        'model_siap': siap,
        'ai_aktif': ai_layanan.tersedia(),
    })


def prediksi_nilai(request):
    """Halaman Prediksi ML: form input -> model -> hasil + grafik."""
    konteks = {'form': PrediksiForm(request.GET or None)}
    try:
        metrik = prediksi_layanan.muat_metrik()
        prediksi_layanan.muat_model()
    except prediksi_layanan.ModelBelumAda:
        konteks['model_belum_ada'] = True
        return render(request, 'portal/prediksi.html', konteks)

    konteks['metrik'] = metrik
    konteks['koef'] = [
        {'nama': n, 'tanda': '+' if k >= 0 else '−', 'abs': abs(k)}
        for n, k in metrik['koefisien'].items()
    ]
    jam_belajar = None
    form = konteks['form']
    if request.GET and form.is_valid():
        data = form.cleaned_data
        nilai = prediksi_layanan.prediksi(data)
        konteks['nilai'] = nilai
        konteks['predikat'] = prediksi_layanan.predikat(nilai)
        jam_belajar = data['Hours_Studied']
        konteks['ai_params'] = dict(data, halaman='prediksi')
        konteks['ai_aktif'] = ai_layanan.tersedia()
    konteks['grafik'] = prediksi_layanan.data_grafik(jam_belajar)
    return render(request, 'portal/prediksi.html', konteks)


@require_POST
def ai_jelaskan(request):
    """Jelaskan hasil prediksi dan grafik menggunakan data tervalidasi."""
    form = PrediksiForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'galat': 'Input tidak valid.'}, status=400)
    try:
        metrik = prediksi_layanan.muat_metrik()
        data = form.cleaned_data
        nilai = prediksi_layanan.prediksi(data)
    except prediksi_layanan.ModelBelumAda:
        return JsonResponse({'galat': 'Model belum dilatih.'}, status=400)

    pesan = ai_layanan.prompt_prediksi(
        data, nilai, prediksi_layanan.predikat(nilai), metrik,
        prediksi_layanan.data_grafik(data['Hours_Studied']),
    )
    try:
        return JsonResponse({'teks': ai_layanan.tanya(pesan)})
    except ai_layanan.AIError as error:
        return JsonResponse({'galat': str(error)}, status=503)
