#!/bin/bash
BAD_PCI="275|434"
BAD_TAC="5135"
LOG_FILE="follower_audit/blacklist_hits.log"
mkdir -p follower_audit
echo -e "\e[1;32m[*] SENTINEL V4 ACTIVE: PROXIMITY SIREN ARMED\e[0m"
while true; do
    cell=$(termux-telephony-cellinfo)
    pci=$(echo "$cell" | jq -r '.[0].pci // "0"')
    tac=$(echo "$cell" | jq -r '.[0].tac // "0"')
    rssi=$(echo "$cell" | jq -r '.[0].rssi // "-120"')
    if [[ "$pci" =~ $BAD_PCI ]] && [[ "$tac" == "$BAD_TAC" ]]; then
        echo "$(date) | TARGET_MATCH | PCI:$pci | RSSI:$rssi" >> "$LOG_FILE"
        termux-vibrate -d 500
        if [ "$rssi" -gt -46 ]; then
            echo -e "\e[1;5;31m[!!!] EXTREME PROXIMITY: TARGET IS ON TOP OF YOU [!!!]\e[0m"
            termux-tts-speak "Target proximity alert. Signal strength critical."
        fi
    fi
    sleep 3
done
