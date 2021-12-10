for f in $(ls "$LOCALAPPDATA\\Temp\\Roblox\\http" -S1); do
    r="$LOCALAPPDATA\\Temp\\Roblox\\http\\$f"
    w="C:\\Users\\Username\\Documents\\ROBLOX\\$f"
    if [[ -f $w ]]; then continue; fi
    l=$(cat $r | tr -d '\0' | nl -pw 1 | grep ": " -avm 1)
    if [[ -z $l ]]; then continue; fi
    tail $r -n +$(echo $l | cut -sd ' ' -f 1) > $w
done