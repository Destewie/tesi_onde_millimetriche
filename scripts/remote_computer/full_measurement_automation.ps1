$host_ = "192.168.1.201"
$user_ = "root"
$pass_ = ""
$command = "./Experiments/fede_measurements.sh" #TODO: modifica fede measurements in modo che prenda in input il numero identificativo del router a cui ci si sta connettendo
$remote_folder_path = "/tmp"
$local_folder_path = "C:\Users\feder\Documents\tesi_onde_millimetriche\MikroTik-mD-Track\Example_data" #TODO: generalizza
$mdTrack_filename = "Example"
$music_filename = "Example_MUSIC"
$filename_csi = "csi_measurements_fede.txt"
$filename_ftm = "ftm_measurements_fede.txt"
$path_matlab_file = "C:\Users\feder\Documents\tesi_onde_millimetriche\MikroTik-mD-Track\Example.m" #TODO: generalizza

# ----------------------------------------------------- SSH START

# Import the Posh SSH module
Import-Module -Name Posh-SSH

#create a pscredential object to avoid writing it down manually
#$credential = New-Object System.Management.Automation.PSCredential ($user_, $pass_) #doesn't work!!

Try{
	# Create an SSH session
	$session = New-SSHSession -ComputerName $host_ -credential "root" #-credential $credential
}
Catch{
    # Handle the SSH exception #don't know why this doesn't work
    Write-Error "Failed to establish SSH connection: $($_.Exception.Message)"
	Exit
}

if(!$session) {
	Write-Output "Failed to establish a SSH connection"
	Exit
}


# Execute a command on the remote server
$result = Invoke-SSHCommand -SessionId $session.SessionId -ShowStandardOutputStream -Command $command

# Display the results
$result.Output


# Close the SSH session
Remove-SSHSession -SessionId $session.SessionId


## ----------------------------------------------------- DIRECTORY MANAGEMENT

#crea una cartella dentro a $local_folder_path per contenere i file delle misure. Se esiste già crea una sottocartella
# Definire la data nel formato yyyy-mm-dd
$dateString = Get-Date -Format "yyyy-MM-dd"


# Definire il nome della nuova cartella
$newBigFolderName = $dateString + '_measurements'
$finalPath = ''

# Verificare se la cartella esiste già
if (!(Test-Path "$local_folder_path\$newBigFolderName")) {
	
    # Creo la cartella main
	New-Item -ItemType Directory -Path "$local_folder_path\$newBigFolderName"
	
	#Creo già la prima cartella per la verisione
	$newVersionFolderName = "v1"
	$finalPath = "$local_folder_path\$newBigFolderName\$newVersionFolderName"

} else {
	# La cartella big esiste già, quindi cerchiamo il primo vx libero 
    $versionNumber = 1
    do {
        $newVersionFolderName = "v$versionNumber"
        $versionNumber++
    } until (!(Test-Path "$local_folder_path\$newBigFolderName\$newVersionFolderName"))
	
	$finalPath = "$local_folder_path\$newBigFolderName\$newVersionFolderName"
}

#Create the folder in which you are going to put all the new measurements
New-Item -ItemType Directory -Path $finalPath


## ----------------------------------------------------- SCP

# Let's copy the measurement files
scp.exe ($user_+'@'+$host_+':'+$remote_folder_path+'/'+$filename_csi) $finalPath 
scp.exe ($user_+'@'+$host_+':'+$remote_folder_path+'/'+$filename_ftm) $finalPath 


$csi_file_path = "$finalPath\$filename_csi"
$ftm_file_path = "$finalPath\$filename_ftm"


## ----------------------------------------------------- MATLAB

cd "C:\Users\feder\Documents\tesi_onde_millimetriche\MikroTik-mD-Track" #TODO: rendi una variabile

# Start matlab script
matlab -batch "$mdTrack_filename $csi_file_path $ftm_file_path $finalPath"
#matlab -batch "$music_filename $csi_file_path $ftm_file_path $finalPath"

cd "C:\Users\feder\Documents\tesi_onde_millimetriche\scripts\remote_computer" #TODO: rendi una variabile
