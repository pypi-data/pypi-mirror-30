import vlc
p = vlc.MediaPlayer('ALLIE_Falas_Offline/Problema de rede.mp3')
p.audio_set_volume(120)
p.play()
