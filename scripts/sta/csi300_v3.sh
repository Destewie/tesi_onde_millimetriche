# Execution example = ./csi300.sh /tmp/csi_measurements.txt 'Mikrotik 101' '\xC4\xAD\x34\xA7\xAD\x5C'

reconnect() {
    connected=0

    # Reset the interface
    ip link set dev wlan0 down
    ip link set dev wlan0 up

    # Reset the supplicant
    killall wpa_supplicant

    wpa_supplicant -D nl80211  -i wlan0 -c /etc/wpa_supplicant.conf -B

    j=0
    while true ; do  # Loop until connected
    
        connected=$(cat /sys/kernel/debug/ieee80211/phy0/wil6210/stations | grep connected | wc -l)
                                             
        if [[ $connected -eq 1 ]]; then
          break
        fi

        j=$((j+1))

        # Break after a certain number of measurements
        if [[ $j -eq 10 ]]; then
          echo "[AoA] We cannot connect after 10 seconds"
          echo "Unreachable" > /tmp/aoa_measurements.txt
          exit
        fi

        sleep 1
    done

    echo "[CSI] We are connected now"
}

# Empty the data file
echo "" > $1

echo "network={
    ssid=\"$2\"
    key_mgmt=NONE
}" > /etc/wpa_supplicant.conf

cat /etc/wpa_supplicant.conf

reconnect
# This will help to check if we cannot connect
connected=0

# A counter
i=0

while true ; do  # Loop until interval has elapsed.
    connected=$(cat /sys/kernel/debug/ieee80211/phy0/wil6210/stations | grep connected | wc -l)
    

    # Get AoA
    echo -n -e $3 | iw dev wlan0 vendor recv 0x001374 0x93 -

    # Save the measurement
    output=$(echo $(dmesg | tail -n1))
    echo $output
    outputL=$(echo $output | wc -c)

    if [[ $outputL -lt 90 ]]; then
	echo "[CSI] Invalid Measurements | Creating new connection"
        reconnect 
	continue
    fi

    echo $output >> $1

    i=$((i+1))

    # Break when no connected
    if [[ $connected -eq 0 ]]; then
      echo "[CSI] We got " $i "measurements" 
      break
    fi

    # Break after a certain number of measurements
    if [[ $i -eq 300 ]]; then
      echo "[CSI] We got 300 measurements"
      break
    fi

done
