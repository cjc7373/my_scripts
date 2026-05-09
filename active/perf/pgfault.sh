#!/usr/bin/env bash

ROOT=/sys/fs/cgroup
show_stat=1
show_events=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-stat)   show_stat=0 ;;
        --no-events) show_events=0 ;;
        *) ROOT=$1 ;;
    esac
    shift
done

declare -A PREV_MAJ
declare -A PREV_REFAULT
declare -A PREV_FAULT
declare -A PREV_SCAN
declare -A PREV_STEAL
declare -A PREV_EV_LOW
declare -A PREV_EV_HIGH
declare -A PREV_EV_MAX
declare -A PREV_EV_OOM

first_run=1

while true; do
    echo "=== $(date) ==="
    echo

    while IFS= read -r cg; do

        statfile="$cg/memory.stat"
        evfile="$cg/memory.events"

        [[ -f "$statfile" ]] || continue

        maj=0
        ref=0
        fault=0
        scan=0
        steal=0

        while read -r k v; do
            case "$k" in
                pgmajfault)
                    maj=$v
                    ;;
                workingset_refault_file)
                    ref=$v
                    ;;
                pgfault)
                    fault=$v
                    ;;
                pgscan)
                    scan=$v
                    ;;
                pgsteal)
                    steal=$v
                    ;;
            esac
        done < "$statfile"

        ev_low=0
        ev_high=0
        ev_max=0
        ev_oom=0

        if [[ -f "$evfile" ]]; then
            while read -r k v; do
                case "$k" in
                    low)  ev_low=$v  ;;
                    high) ev_high=$v ;;
                    max)  ev_max=$v  ;;
                    oom)  ev_oom=$v  ;;
                esac
            done < "$evfile"
        fi

        prev_maj=${PREV_MAJ["$cg"]:-0}
        prev_ref=${PREV_REFAULT["$cg"]:-0}
        prev_fault=${PREV_FAULT["$cg"]:-0}
        prev_scan=${PREV_SCAN["$cg"]:-0}
        prev_steal=${PREV_STEAL["$cg"]:-0}
        prev_ev_low=${PREV_EV_LOW["$cg"]:-0}
        prev_ev_high=${PREV_EV_HIGH["$cg"]:-0}
        prev_ev_max=${PREV_EV_MAX["$cg"]:-0}
        prev_ev_oom=${PREV_EV_OOM["$cg"]:-0}

        dmaj=$((maj - prev_maj))
        dref=$((ref - prev_ref))
        dfault=$((fault - prev_fault))
        dscan=$((scan - prev_scan))
        dsteal=$((steal - prev_steal))
        dev_low=$((ev_low - prev_ev_low))
        dev_high=$((ev_high - prev_ev_high))
        dev_max=$((ev_max - prev_ev_max))
        dev_oom=$((ev_oom - prev_ev_oom))

        PREV_MAJ["$cg"]=$maj
        PREV_REFAULT["$cg"]=$ref
        PREV_FAULT["$cg"]=$fault
        PREV_SCAN["$cg"]=$scan
        PREV_STEAL["$cg"]=$steal
        PREV_EV_LOW["$cg"]=$ev_low
        PREV_EV_HIGH["$cg"]=$ev_high
        PREV_EV_MAX["$cg"]=$ev_max
        PREV_EV_OOM["$cg"]=$ev_oom

        (( first_run )) && continue

        # 没变化跳过
        _skip=1
        if (( show_stat )) && (( dfault || dmaj || dref || dscan || dsteal )); then
            _skip=0
        fi
        if (( show_events )) && (( dev_low || dev_high || dev_max || dev_oom )); then
            _skip=0
        fi
        (( _skip )) && continue

        rel="${cg#$ROOT}"
        rel="${rel#/}"

        depth=$(grep -o "/" <<< "$rel" | wc -l)

        indent=""
        for ((i=0; i<depth; i++)); do
            indent+="│   "
        done

        name=$(basename "$cg")

        printf "%s├── %s\n" "$indent" "$name"
        if (( show_stat )); then
            printf "%s│   fault=%-8d maj=%-8d refault=%-8d scan=%-8d steal=%-8d\n" \
                "$indent" "$dfault" "$dmaj" "$dref" "$dscan" "$dsteal"
        fi
        if (( show_events )); then
            printf "%s│   ev_low=%-6d ev_high=%-6d ev_max=%-6d ev_oom=%-6d\n" \
                "$indent" "$dev_low" "$dev_high" "$dev_max" "$dev_oom"
        fi

    done < <(find "$ROOT" -type d | sort)

    first_run=0

    sleep 1
done