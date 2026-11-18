"""CPU-only hints for choosing a reference recording."""
import numpy as np


def inspect_reference(audio, rate, seconds):
    frame = max(1, round(rate * .04))
    count = len(audio) // frame
    if not count:
        return 0, {'speech_like_seconds': 0, 'scan_seconds': 0, 'hints': ['too_short'], 'recommend': False}
    blocks = np.asarray(audio[:count * frame], dtype='float32').reshape(count, frame)
    levels = np.sqrt(np.mean(blocks ** 2, axis=1))
    upper = max(float(np.percentile(levels, 90)), 1e-8)
    peak_fraction = np.mean(np.abs(blocks) > .98, axis=1)
    active = levels > max(.0015, .12 * upper)

    # Short pitch-period correlation helps rank spoken-sounding regions.
    # The same signals can occur in music, so these are listening hints.
    samples = blocks[:, ::4].astype('float64')
    samples -= samples.mean(axis=1, keepdims=True)
    spectrum = np.fft.rfft(samples, n=1024, axis=1)
    correl = np.fft.irfft(np.abs(spectrum) ** 2, axis=1)
    decimated = rate / 4
    lower, upper_lag = round(decimated / 420), round(decimated / 75)
    search = correl[:, lower:upper_lag + 1] / np.maximum(correl[:, :1], 1e-12)
    strengths = np.max(search, axis=1)
    lags = lower + np.argmax(search >= np.maximum(.43, strengths[:, None] * .88), axis=1)
    speech_like = active & (strengths >= .43)
    pitch = decimated / lags
    energy_split = max(1, round(1800 * 1024 / decimated))
    power = np.abs(spectrum) ** 2
    brightness = power[:, energy_split:].sum(axis=1) / np.maximum(power.sum(axis=1), 1e-12)

    width = min(count, max(1, round(seconds * rate / frame)))
    activity = active.astype('float64') * .35 + speech_like * .65
    score = activity - 7 * peak_fraction
    totals = np.cumsum(np.r_[0.0, score])
    first = int(np.argmax(totals[width:] - totals[:-width]))
    selected = slice(first, first + width)
    speech_seconds = float(speech_like[selected].sum() * frame / rate)
    hints = []
    if speech_seconds < min(5.0, seconds * .35):
        hints.append('too_short')
    if np.mean(peak_fraction[selected]) > .003:
        hints.append('clipping')
    if np.percentile(levels, 20) > upper * .20 and active.mean() > .82:
        hints.append('bed')

    # Compare sustained pitch and spectral changes in separated speech runs.
    edges = np.flatnonzero(np.diff(np.r_[False, active, False]))
    profiles = []
    for begin, end in zip(edges[::2], edges[1::2]):
        indices = np.flatnonzero(speech_like[begin:end]) + begin
        if len(indices) >= 12:
            profiles.append((float(np.median(pitch[indices])), float(np.median(brightness[indices]))))
    if len(profiles) >= 2:
        low = min(profiles)
        high = max(profiles)
        if high[0] > low[0] * 1.55 and abs(high[1] - low[1]) >= .055:
            hints.append('timbre_change')
    return first * frame / rate, {
        'speech_like_seconds': round(speech_seconds, 1), 'scan_seconds': round(len(audio) / rate, 1),
        'hints': hints, 'recommend': speech_seconds >= 1.5,
    }

