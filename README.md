# tesi_onde_millimetriche
Studio della localizzazione indoor attiva tramite uno o più access point.  
La repository contiene script per raccogliere automaticamente CSI e FTM da router Mikrotik e script che implementano varie tecniche di localizzazione.

## come prendere le misure con gli script
* collegarsi al router che fungerà da AP e avviare lo script /root/apUP.sh (se non viene fuori in output AP-ENABLED, ritentare)
* collegarsi al router che fungerà da client e avviare da powershell lo script "full_measurement_automation.ps1" (Prima di farlo bisogna mettere mano ai path presenti nello script in base al proprio computer)
