import wave


def save_wave(audio_data, filename,
              sample_rate=16000, sample_width=2, channels=1):
    wave_file = wave.open(filename, 'wb')
    wave_file.setframerate(sample_rate)
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(sample_width)
    wave_file.writeframes(audio_data.tostring())
    wave_file.close()
