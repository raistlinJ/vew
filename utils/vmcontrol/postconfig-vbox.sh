#!/usr/bin/env bash
# Post-configure a newly imported development VM.

NAME=$(basename $0)

# These vars may be overridden by envionment variables of the same name but
# with a preceeding "DEV_"
USER=${DEV_USER:-"somedev"}
PASS=${DEV_PASS:-"somedev"}
VM=${DEV_VM:-"localdev"}

function _error () {
    local EXIT MSG

    EXIT=$1 ; MSG=${2:-"${NAME}: Unknown Error"}
    if [[ $EXIT -eq 0 ]] ; then
        echo -e $MSG
    else
        echo -e $MSG 1>&2
        exit $EXIT
    fi
}

##
# Run a command in the named VirtualBox machine. Command must be a
# single-quote-able string suitable to be passed to sh -c
# E.g.:
#
#   local app_base="/home/somedev/src/repo"
#   vboxcmd 'cd '${app_base}' && ./setup -a' \
#       || _error 1 "Failed running setup."
#   vboxcmd 'cd '${app_base}' && source ./activate && blah somefunc' \
#       || _error 1 "Failed running somefunc."
#
#   # Update vbox ini with hostname
#   for conf in \
#       "conf1" \
#       "conf2" \
#       "conf3"
#   do
#       vboxcmd 'sed -i.bak '\''/'${conf}'/ s;http://localhost;http://'${hostname}';'\'' '${app_ini}
#   done
#
function vboxcmd() {
    local cmd=${1}
    [[ -n "${cmd}" ]] || _error 1 "No command given"

    # Note: pass --verbose to this command to see the real exit code
    VBoxManage guestcontrol ${VM} \
        exec --username ${USER} --password ${PASS} \
        --image '/bin/bash' \
        --wait-exit --wait-stdout --wait-stderr \
        -- -l -c "${cmd}" \
        || _error 1 "\n\nError running command: ${cmd}"
}

##
# Configure the VM with static networking.
function config_networking() {
    local hostname=${1} \
        address=${2} \
        netmask="255.255.255.0" \
        network="192.168.0.14" \
        broadcast="192.168.0.1" \
        gateway="192.168.0.1" \
        nameservers="8.8.8.8 8.8.4.4"

    [[ -n "${1}" ]] || _error 1 "config_networking requires a hostname argument"
    [[ -n "${2}" ]] || _error 1 "config_networking requires an address argument"

    vboxcmd "sudo tee /etc/network/interfaces > /dev/null <<HEREDOC
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address ${address}
    netmask ${netmask}
    network ${network}
    broadcast ${broadcast}
    gateway ${gateway}
    dns-nameservers ${nameservers}
HEREDOC"

    echo -e "Static networking is now configured.
    1.  Shutdown your VM.
    2.  Switch networking to Bridged.
    3.  Celebrate good times."
}

##
# Configure the Apache vhosts for the three sites with the given hostname
function config_apache() {
    local hostname=${1}
    [[ -n "${1}" ]] || _error 1 "config_apache requires a hostname argument"

    for site in site1 site2 site3; do
        host="${site}.${hostname}"
        conf="/etc/apache2/sites-available/${site}"
        vboxcmd 'sudo sed -i.bak -re '\''/^\s+ServerName/ s/[a-z.]+$/'${host}'/g'\'' '${conf}
    done
}

# Prompts the user for a hostname (e.g., blah.dev.example.com) and then
# attempts to look that hostname up to both verify and to obtain the IP for
# that hostname, then configures the VM by running the functions above.
function main() {
    local usage="Usage: ${NAME} <hostname>\n
    For example: ${NAME} blah.dev.example.com
    "

    if [[ $# -lt 1 ]] || [[ $1 == "--help" ]] || [[ $1 == "-h" ]] ; then
        echo -e ${usage}
        exit
    fi

    local hostname=${1}
    local address=$(dig +short a ${hostname}.)

    [[ -n "${address}" ]] || _error 1 "Could not verify hostname '${hostname}'"

    config_networking ${hostname} ${address}
    config_apache ${hostname}
}

main $*