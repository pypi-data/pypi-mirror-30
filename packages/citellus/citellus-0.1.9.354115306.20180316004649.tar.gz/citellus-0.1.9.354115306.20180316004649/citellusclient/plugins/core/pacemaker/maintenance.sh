#!/bin/bash

# Copyright (C) 2018   Robin Černín (rcernin@redhat.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# long_name: Pacemaker in maintenance mode
# description: Checks for maintenance enabled in cluster
# priority: 800

# Load common functions
[[ -f "${CITELLUS_BASE}/common-functions.sh" ]] && . "${CITELLUS_BASE}/common-functions.sh"

MAINTENANCEENABLED=$"maintenance is enabled"

# we can run this against fs snapshot or live system

if [[ "x$CITELLUS_LIVE" = "x1" ]];  then
    pacemaker_status=$(systemctl is-active pacemaker || :)
    if [[ "$pacemaker_status" = "active" ]]; then
        if pcs config | grep -q "maintenance-mode:.*true"; then
            echo "$MAINTENANCEENABLED" >&2
            exit ${RC_FAILED}
        else
            exit ${RC_OKAY}
        fi
    else
        echo "pacemaker is not running on this node" >&2
        exit ${RC_SKIPPED}
    fi
elif [[ "x$CITELLUS_LIVE" = "x0" ]];  then
    if is_active "pacemaker"; then
        for CLUSTER_DIRECTORY in "pacemaker" "cluster"; do
            if [[ -d "${CITELLUS_ROOT}/sos_commands/${CLUSTER_DIRECTORY}" ]]; then
                PCS_DIRECTORY="${CITELLUS_ROOT}/sos_commands/${CLUSTER_DIRECTORY}"
            fi
        done
        is_required_file "${PCS_DIRECTORY}/pcs_config"
        if is_lineinfile "maintenance-mode:.*true" "${PCS_DIRECTORY}/pcs_config"; then
            echo "$MAINTENANCEENABLED" >&2
            exit ${RC_FAILED}
        else
            exit ${RC_OKAY}
        fi
    else
        echo "pacemaker is not running on this node" >&2
        exit ${RC_SKIPPED}
    fi
fi
