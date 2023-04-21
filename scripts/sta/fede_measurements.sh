echo "Starting with the csi measures..."
~/Experiments/csi300_v3.sh /tmp/csi_measurements_fede.txt 'Mikrotik' '\x08\x55\x31\x70\xFF\x0A'
echo "csi measures done!"

echo "Starting with the ftm measures..."
~/Experiments/ftm10.sh /tmp/ftm_measurements_fede.txt 'Mikrotik' '\x08\x55\x31\x70\xFF\x0A'
echo "ftm measures done!"
