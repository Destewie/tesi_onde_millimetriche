#just as a reminder, the router in the lab downstairs has SSID=Mikrotik and MACaddr='\x08\x55\x31\x70\xFF\x0A'


echo "Starting with the csi measures..."
~/Experiments/csi300_v3.sh /tmp/csi_measurements_fede.txt 'Mikrotik12' '\x08\x55\x31\x9B\x09\x29'
echo "csi measures done!"

echo "Starting with the ftm measures..."
~/Experiments/ftm10.sh /tmp/ftm_measurements_fede.txt 'Mikrotik12' '\x08\x55\x31\x9B\x05\x29'
echo "ftm measures done!"
