// File created from src/messages.mes

#include <cstddef>
#include <log/message_types.h>
#include <log/message_initializer.h>

extern const isc::log::MessageID RUNSCRIPT_EXEC_FAILED = "RUNSCRIPT_EXEC_FAILED";
extern const isc::log::MessageID RUNSCRIPT_FORK_FAILED = "RUNSCRIPT_FORK_FAILED";
extern const isc::log::MessageID RUNSCRIPT_MISSING_PARAM = "RUNSCRIPT_MISSING_PARAM";
extern const isc::log::MessageID RUNSCRIPT_MISTYPED_PARAM = "RUNSCRIPT_MISTYPED_PARAM";

namespace {

const char* values[] = {
    "RUNSCRIPT_EXEC_FAILED", "exec() failed, please check that the script exists and is executable. Error: %1",
    "RUNSCRIPT_FORK_FAILED", "fork() failed with error: %1",
    "RUNSCRIPT_MISSING_PARAM", "required parameter \"%1\" missing in configuration",
    "RUNSCRIPT_MISTYPED_PARAM", "parameter \"%1\" in configuration has wrong type",
    NULL
};

const isc::log::MessageInitializer initializer(values);

} // Anonymous namespace

