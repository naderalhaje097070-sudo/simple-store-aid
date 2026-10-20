/* Diagnostics only: no DNS/request payloads or environment contents are logged. */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dlfcn.h>
#include <execinfo.h>
#include <fcntl.h>
#include <netdb.h>
#include <openssl/sha.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

static int (*original)(const char *, const char *, const struct addrinfo *, struct addrinfo **);
static pthread_once_t once = PTHREAD_ONCE_INIT;
static void initialize(void) {
  *(void **)(&original) = dlsym(RTLD_NEXT, "getaddrinfo");
  if (!original) _exit(125);
}
static const char *safe_name(const char *s) {
  static const char *known[] = {"localhost", "registry.npmjs.org", "api.cloudflare.com",
    "cloudflare.com", "www.cloudflare.com", "dash.cloudflare.com", "developers.cloudflare.com", NULL};
  for (int i=0; known[i]; i++) if (!strcmp(s,known[i])) return known[i];
  return "hashed_hostname";
}
static const char *safe_module(const char *s) {
  if (!s) return "unknown";
  const char *p = strrchr(s,'/'); p = p ? p+1 : s;
  if (!strcmp(p,"node") || !strcmp(p,"workerd") || !strcmp(p,"libc.so.6") ||
      !strcmp(p,"libuv.so.1") || !strcmp(p,"dns_trace.so")) return p;
  return "other_module";
}
int getaddrinfo(const char *node, const char *service, const struct addrinfo *hints, struct addrinfo **res) {
  pthread_once(&once,initialize);
  const char *target = getenv("G1_NATIVE_DNS_LOG");
  if (!target || !node) return original(node,service,hints,res);
  unsigned char digest[SHA256_DIGEST_LENGTH]; char hex[65];
  SHA256((const unsigned char *)node,strlen(node),digest);
  for (int i=0;i<32;i++) snprintf(hex+2*i,3,"%02x",digest[i]);
  struct timespec ts; clock_gettime(CLOCK_REALTIME,&ts);
  void *frames[8]; int n=backtrace(frames,8); Dl_info info;
  const char *caller="unknown"; unsigned long offset=0;
  if (n>1 && dladdr(frames[1],&info)) {
    caller=safe_module(info.dli_fname);
    offset=(unsigned long)frames[1]-(unsigned long)info.dli_fbase;
  }
  char line[512]; int len=snprintf(line,sizeof(line),
    "{\"type\":\"native_getaddrinfo\",\"pid\":%d,\"tid\":%ld,\"timestamp_ms\":%lld,\"hostname\":\"%s\",\"hostname_sha256\":\"%s\",\"module\":\"%s\",\"module_offset\":%lu}\n",
    getpid(),syscall(SYS_gettid),(long long)ts.tv_sec*1000+ts.tv_nsec/1000000,
    safe_name(node),hex,caller,offset);
  int fd=open(target,O_WRONLY|O_CREAT|O_APPEND|O_CLOEXEC,0600);
  if (fd<0 || len<=0 || len>=(int)sizeof(line) || write(fd,line,len)!=len) _exit(125);
  close(fd);
  return original(node,service,hints,res);
}
