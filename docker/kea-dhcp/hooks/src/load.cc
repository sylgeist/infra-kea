/* Copyright (c) 2017-2019 by Baptiste Jonglez
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#include <signal.h>
#include <hooks/hooks.h>

#include "logger.h"
#include "common.h"

using namespace isc::hooks;
using namespace isc::data;

/* Path of the script to be run in hooks, accessed by the other files of
 * this library. */
std::string script_path;
/* Name of the script (without the leading directory). */
std::string script_name;
/* Enable/disable script execution */
bool script_enabled;
/* Shipyard environment */
std::string shipyard_url;
/* DO region*/
std::string region_name;
/* Script debug */
bool script_debug;

extern "C" {

int load(LibraryHandle& handle) {
    ConstElementPtr script = handle.getParameter("script");
    if (!script) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISSING_PARAM).arg("script");
        return 1;
    }
    if (script->getType() != Element::string) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISTYPED_PARAM).arg("script");
        return 1;
    }
    script_path = script->stringValue();
    script_name = script_path.substr(script_path.find_last_of('/') + 1);

    ConstElementPtr enabled = handle.getParameter("enabled");
    if (!enabled) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISSING_PARAM).arg("enabled");
        return 1;
    }
    if (enabled->getType() != Element::boolean) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISTYPED_PARAM).arg("enabled");
        return 1;
    }
    script_enabled = enabled->boolValue();

    ConstElementPtr shipyard = handle.getParameter("shipyard");
    if (!shipyard) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISSING_PARAM).arg("shipyard");
        return 1;
    }
    if (shipyard->getType() != Element::string) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISTYPED_PARAM).arg("shipyard");
        return 1;
    }
    shipyard_url = shipyard->stringValue();

    ConstElementPtr region = handle.getParameter("region");
    if (!region) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISSING_PARAM).arg("region");
        return 1;
    }
    if (region->getType() != Element::string) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISTYPED_PARAM).arg("region");
        return 1;
    }
    region_name = region->stringValue();

    ConstElementPtr debug = handle.getParameter("script_debug");
    if (!debug) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISSING_PARAM).arg("script_debug");
        return 1;
    }
    if (debug->getType() != Element::boolean) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_MISTYPED_PARAM).arg("script_debug");
        return 1;
    }
    script_debug = debug->boolValue();

    /* Install signal handler for non-wait case to avoid leaving  zombie processes around */ 
    signal(SIGCHLD, SIG_IGN);

    return 0;
}

} // end extern "C"
