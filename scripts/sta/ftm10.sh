#Execution example = ./ftm10.sh /tmp/tof_measurements.txt 'Mikrotik' '\x08\x55\x31\x70\xFF\x0A'

#ATTENTION!
#THIS IS A TEST CODE. SOME PARTS(like the error detection in dmesg) AREN'T BULLETPROOF.


directory="$1"

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
          echo "[ToF] We cannot connect after 10 seconds"                                      
          echo "Unreachable" > "$directory"
          exit
        fi                                                                                     
                                                                                               
        sleep 1                                                                                
    done                                                                                       
                                                                                               
    echo "[TFM] We are connected now"                                                          
} 

#-------------------------------------------------------------------------

#Empty the data file                                                                                   
echo "" > $1                                                                                       

#Update wpa supplicant                                                                                           
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
                                                                                               
    echo "now we try the " $i " measurement"
                                                                                               
    # Get ToF                                                                                  
    echo -n -e $3 | iw dev wlan0 vendor recv 0x001374 0x81 -                                   
                                                                                               
    # Save the measurement                                                                     
    output=$(echo $(dmesg | tail -n1))  #takes the last line of dmesg (the one with the measurements
    failCheck=$(dmesg | tail -n2 | head -n1) #takes the second last line of dmesg. This is the line that could contain the failing message

    outputL=$(echo $output | wc -c)
    failCheckL=$(echo $failCheck | wc -c)

    #checks if the measurement failed
    if [ $outputL -lt 110 ] && [ $failCheckL -lt 110 ]; then
        echo "[CSI] Invalid Measurements | Creating new connection"
        reconnect 
        continue
    fi
                                                                                               
    echo $output
    echo $output >> $1
    
        i=$((i+1))

    sleep 1
                                                                                               
    # Break when no connected                                                                  
    if [[ $connected -eq 0 ]]; then                                                            
      echo "[FTM] We got " $i "measurements"                                                   
      break                                                                                    
    fi                                                                                         
                                                                                               
    # Break after a certain number of measurements                                             
    if [[ $i -eq 10 ]]; then                                                                  
      echo "[FTM] We got 10 measurements"                                                     
      break                                                                                    
    fi                                                                                         
                                                                                               
done

