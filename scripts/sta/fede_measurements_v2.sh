
if [ $# -ne 2 ]; then
    echo "Usage: $0 <device_name> <mac_address>"
    echo "Example: $0 Mikrotik '\x08\x55\x31\x70\xFF\x0A'"
    exit 1
fi

device_name=$1
mac_address=$2

echo "Starting with the csi measures..."
~/Experiments/csi300_v3.sh /tmp/csi_measurements_fede.txt "$device_name" "$mac_address"
echo "csi measures done!"

echo "Starting with the ftm measures..."
~/Experiments/ftm10.sh /tmp/ftm_measurements_fede.txt "$device_name" "$mac_address"
echo "ftm measures done!"

