#!/usr/bin/env bash
source env/bin/activate
RCLONE="tools/rclone-v1.75.0-linux-amd64/rclone"

roots=(
    "cvc3:1471o4gcuNTUerIRm7QIj6nvCFwXWhwyk"
    "cvc4:1u5oo6FfzkXSObybW12teSH9u2nTPWQwC"
    "cvc5:1ekMGsormVsfO9NO3o9Us5-Q6cx1297HX"
    "cvc6:1RaF2p92Rirj5CwnVgqH3e2A0VHihr-Iv"
    "cvc7:1K3k8RXDAvcSD4vuuXbL_jWwXivphORb6"
    "cvc8:1yOdHYE3EFZimAslSZx99zIhdDZ3WSrJp"
    "cvc9:1bggk1ddkr5QyXQZS0sHUY-lbv9WuFaG6"
    "cvc10:1rg5Jpt0Reane34A97YehEfJGvOBr2X8S"
)

for item in "${roots[@]}"; do
    loc="${item%%:*}"
    fid="${item##*:}"
    
    output=$($RCLONE --config config/rclone.conf lsjson --max-depth 1 "Gdrive-yogesh,root_folder_id=${fid}:" | grep '"Name"' || true)
    echo "$loc - $fid"
    echo "$output"
    echo "---"
done
