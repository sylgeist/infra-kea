#include <iostream>
#include <memory>
#include <string>
#include <fstream>
#include <sstream>

#include <grpcpp/grpcpp.h>
#include <google/protobuf/util/time_util.h>
#include "shipyard.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using shipyardapi::ShipyardAPI;
using shipyardapi::BMCDiscoveryRequest;
using shipyardapi::BMCDiscoveryResponse;
using shipyardapi::BMC;

int main(int argc, char** argv) {
  const std::string cafile = "/usr/local/share/ca-certificates/CA.pem";
  const std::string privfile = "/usr/local/share/mtls/kea-client.key";
  const std::string pubfile = "/usr/local/share/mtls/kea-client.crt";
  const std::string log_file = "/var/log/shipyard_update.log";
  bool do_grpc_debug = false;

  // Pull in the env vars set up by Kea for sending to Shipyard
  const std::string env_hwaddr = std::getenv("KEA_LEASE4_HWADDR") ? std::getenv("KEA_LEASE4_HWADDR") : "";
  const std::string env_ipaddr = std::getenv("KEA_LEASE4_ADDRESS") ? std::getenv("KEA_LEASE4_ADDRESS") : "";
  const std::string env_shipyard = std::getenv("SHIPYARD_URL") ? std::getenv("SHIPYARD_URL") : "";
  const std::string env_hostname = std::getenv("KEA_LEASE4_HOSTNAME") ? std::getenv("KEA_LEASE4_HOSTNAME") : "";
  const std::string env_region = std::getenv("REGION") ? std::getenv("REGION") : "";
  const std::string env_debug = std::getenv("DO_GRPC_DEBUG") ? std::getenv("DO_GRPC_DEBUG") : "0";

  // Open up the log file for output since we are in a container
  std::ofstream log(log_file, std::ios::out | std::ios::app);
  if (!log.is_open()) {
    std::cerr << "Error: Could not open logfile: " << log_file << std::endl;
    return 1;
  }

  // Check if debug/verbose output is requested
  if (env_debug.compare("1") == 0) {
    do_grpc_debug = true;
  }

  if (env_hwaddr.empty() || env_ipaddr.empty() || env_hostname.empty() || env_shipyard.empty() || env_region.empty()) {
    log << "Error: Required ENV variables not set. Check Kea hook configuration" <<
    " MAC: " << env_hwaddr <<
    " IP: " << env_ipaddr <<
    " Hostname: " << env_hostname <<
    " Shipyard: " << env_shipyard <<
    " Region: "<< env_region <<  std::endl;
    return 1;
  }

  // CA is dynamically read in at execution time for freshness :)
  std::stringstream cabuffer, privkeybuffer, pubkeybuffer;
  std::ifstream cacert(cafile);
  std::ifstream privkey(privfile);
  std::ifstream pubkey(pubfile);
  if (cacert) {
    cabuffer << cacert.rdbuf();
    cacert.close();
  } else {
    log << "Error: CA file not found: " << cafile << std::endl;
    return 1;
  }
  if (privkey) {
    privkeybuffer << privkey.rdbuf();
    privkey.close();
  } else {
    log << "Error: mTLS private key file not found: " << privfile << std::endl;
    return 1;
  }
  if (pubkey) {
    pubkeybuffer << pubkey.rdbuf();
    pubkey.close();
  } else {
    log << "Error: mTLS client cert file not found: " << pubfile << std::endl;
    return 1;
  }

  grpc::SslCredentialsOptions ssl_opts;
  ssl_opts.pem_root_certs = cabuffer.str();
  ssl_opts.pem_cert_chain = pubkeybuffer.str();
  ssl_opts.pem_private_key = privkeybuffer.str();

  auto channel_creds = grpc::SslCredentials(ssl_opts);
  auto channel = grpc::CreateChannel(env_shipyard, channel_creds);
  auto stub = shipyardapi::ShipyardAPI::NewStub(channel);

  // Set up content for the Shipyard request and reply
  ClientContext context;
  BMCDiscoveryRequest request;
  BMCDiscoveryResponse reply;

  // In the future we may send the client hostname but for now
  // it causes too much confusion on the Shipyard side to parse out
  // useful information.
  //
  // request.set_hostname(env_hostname);
  request.set_mac_address(env_hwaddr);
  request.set_ip_address(env_ipaddr);
  request.set_region(env_region);

  Status status = stub->BMCDiscovery(&context, request, &reply);

  if (status.ok()) {
    if (do_grpc_debug) {
      log << "BMC Updated: Serial: " << reply.bmc().system_serial() <<
      " Kea Hostname: " << env_hostname <<
      " REGION: " << env_region <<
      " MAC: " << reply.bmc().mac_address() <<
      " IP: " << reply.bmc().ip_address() <<
      " Last Updated: " << reply.bmc().timestamp() <<
      " SHIPYARD: " << env_shipyard << std::endl;
    }
  } else {
    log << "BMC update failed: " << status.error_code() << ": " << status.error_message() <<
    " Kea Hostname: " << env_hostname <<
    " MAC: " << env_hwaddr <<
    " IP: " << env_ipaddr <<
    " REGION: " << env_region <<
    " SHIPYARD: " << env_shipyard << std::endl;
    return 1;
  }

  return 0;
}
