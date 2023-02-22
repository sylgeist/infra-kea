/* Copyright (c) 2017-2019 by Baptiste Jonglez
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#include <hooks/hooks.h>
#include <dhcpsrv/subnet.h>
#include <dhcpsrv/lease.h>
#include <dhcpsrv/cfgmgr.h>

#include <string>
#include <vector>

#include "runscript.h"
#include "common.h"

using namespace isc::dhcp;
using namespace isc::data;
using namespace isc::hooks;

extern "C" {

/* These are helpers that extract relevant information from Kea data
 * structures and store them in environment variables. */
void extract_bool(std::vector<std::string>& env, const std::string variable, bool value) {
    env.push_back(variable + "=" + std::string(value ? "1" : "0"));
}

void extract_lease4(std::vector<std::string>& env, const Lease4Ptr lease) {
    env.push_back("KEA_LEASE4_HOSTNAME=" + lease->hostname_);
    env.push_back("KEA_LEASE4_ADDRESS=" + lease->addr_.toText());
    if (lease->hwaddr_) {
        env.push_back("KEA_LEASE4_HWADDR=" + lease->hwaddr_->toText(false));
    } else {
        env.push_back("KEA_LEASE4_HWADDR=");
    }
}

/* Utility function to test whether we are working with a BMC network
 * Dependent on the Kea generator script adding "user-context" entries to
 * the subnets imported from Netbox. When correctly performed each subnet
 * will have something like:
 *
 *         "user-context": {
 *         "role": "bgp-controller"
 *         }
 *
 * in each subnet section to key off of in the hook. */
bool isOobNetwork(const ConstSubnet4Ptr subnet) {
    if (subnet) {
      ConstElementPtr user_context = subnet->getContext();
      if (user_context && (user_context->getType() == Element::map)) {
        ConstElementPtr role_element = user_context->get("role");
        if (role_element && (role_element->getType() == Element::string)) {
          std::string role = role_element->stringValue(); 
          if (role.compare("oob-access") == 0) { return true; }
        }
      }
    }

    return false; 
}
 
/* IPv4 leases4_committed hook point */ 
int leases4_committed(CalloutHandle& handle) {
    Lease4CollectionPtr leases4;

    handle.getArgument("leases4", leases4);

    if (script_enabled && leases4) { 
        // Per the docs, Kea may batch multiple leases into the hook call (hence the "Lease4Collection")
        for (size_t i = 0; i < leases4->size(); ++i) {
            std::vector<std::string> env;
            bool bmc_network;

            // The lease commit hook doesn't provide a Subnet pointer so we have to go get it ourselves
            CfgMgr& cfg_mgr = CfgMgr::instance();
            ConstSubnet4Ptr subnet = cfg_mgr.getCurrentCfg()->getCfgSubnets4()->getBySubnetId(leases4->at(i)->subnet_id_);

            // In some odd cases Kea may not find the subnet which makes 
            // all this work pointless and we should exit out
            if (subnet) {
                bmc_network = isOobNetwork(subnet);
            }
            if (!bmc_network) { return (0); }

            // If we've made it this far we are ready to call the Shipyard update utility
            extract_lease4(env, leases4->at(i));
            env.push_back("REGION=" + region_name);
            env.push_back("SHIPYARD_URL=" + shipyard_url);

            // Enable debug setting in child proc environment
            extract_bool(env, "DO_GRPC_DEBUG", script_debug);
            int ret = run_script("leases4_committed", env);
        }
    }
    return (0);
}

} // end extern "C"
