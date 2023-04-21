#simple script to create the connection with the AP

    # Reset the interface                                                                          
    ip link set dev wlan0 down
    sleep 1
    ip link set dev wlan0 up                                                                       
                                                                                                   
    # Reset the supplicant                                                                         
    killall wpa_supplicant                                                                         

wpa_supplicant -D nl80211  -i wlan0 -c /etc/wpa_supplicant.conf -B
