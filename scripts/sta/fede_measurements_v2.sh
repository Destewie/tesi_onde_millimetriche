
if [ $# -ne 1 ]; then
    echo "Usage: $0 <id del router a cui vuoi connetterti>"
    echo "Example: $0 12"
    exit 1
fi

ssid="Mikrotik$1"

router_found=false

if [ "$1" -eq "9" ]
then
    mac_address="\x08\x55\x31\x9B\x09\xF4"
        router_found=true
fi
if [ "$1" -eq "10" ]
then
    mac_address="\x08\x55\x31\x9B\x0A\x1B"
        router_found=true
fi
if [ "$1" -eq "11" ]
then
    mac_address="\x08\x55\x31\x9B\x0A\x1D"
        router_found=true
fi
if [ "$1" -eq "12" ]
then
    mac_address="\x08\x55\x31\x9B\x05\x29"
        router_found=true
fi
if [ "$1" -eq "13" ]
then
    mac_address="\x08\x55\x31\x9B\x04\xAC"
        router_found=true
fi

if ! $router_found
then
        echo "Non ho trovato un match per il numero che hai inserito"
        exit 0
fi

command="~/Experiments/csi300_v3.sh /tmp/csi_measurements_fede.txt $ssid '$mac_address'"
echo $command
echo "Starting with the csi measures..."
eval "$command"
echo "csi measures done!"

command="~/Experiments/ftm10.sh /tmp/ftm_measurements_fede.txt $ssid '$mac_address'"
echo $command
echo "Starting with the ftm measures..."
eval "$command"
echo "ftm measures done!"


