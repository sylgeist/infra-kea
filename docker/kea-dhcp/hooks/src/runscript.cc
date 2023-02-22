/* Copyright (c) 2017-2019 by Baptiste Jonglez
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>

#include <string>
#include <vector>
#include <cerrno>

#include "logger.h"
#include "common.h"

extern "C" {

int run_script(std::string arg0, std::vector<std::string> env)
{
    /* Convert the vector containing environment variables to the format
     * expected by execle(). */
    char const* envp[env.size() + 1];
    for (int i = 0; i < env.size(); ++i) {
        envp[i] = env[i].c_str();
    }
    envp[env.size()] = (char const*) NULL;

    /* fork() & execle() */
    int ret;
    pid_t pid;
    pid = fork();
    if (pid == -1) {
        LOG_ERROR(runscript_logger, RUNSCRIPT_FORK_FAILED).arg(strerror(errno));
        return -1;
    }
    if (pid == 0) {
        /* Child process */
        ret = execle(script_path.c_str(), script_name.c_str(), arg0.c_str(), (char *)NULL, envp);
        /* execle never returns when everything went well, so we necessarily encountered an error. */
        LOG_ERROR(runscript_logger, RUNSCRIPT_EXEC_FAILED).arg(strerror(errno));
        /* This only exits the child, not Kea itself. */
        exit(EXIT_FAILURE);
    } else {
        /* By default, assume everything worked well */
        return 0;
    }
}

} // end extern "C"
