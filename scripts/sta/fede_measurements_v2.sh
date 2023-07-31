
if [ $# -ne 2 ]; then
    echo "Usage: $0 <device_name> <mac_address>"
    echo "Example: $0 Mikrotik '\x08\x55\x31\x70\xFF\x0A'"
    exit 1
fi

#imposto l'SSID adeguato 
ssid="Mikrotik$2"


#se il secondo parametro è uguale a 9, allora l'SSID diventa Mikrotik9 e il MAC address diventa 08:55:31:70:FF:09
if [ $2 -eq 9 ]; then
    mac_address="\x08\x55\x31\x70\xFF\x09"
else


command="~/Experiments/csi300_v3.sh /tmp/csi_measurements_fede.txt $device_name '$mac_address'"
echo "Starting with the csi measures..."
eval "$command"
echo "csi measures done!"

command="~/Experiments/csi300_v3.sh /tmp/ftm_measurements_fede.txt $device_name '$mac_address'"
echo "Starting with the ftm measures..."
eval "$command"
echo "ftm measures done!"

