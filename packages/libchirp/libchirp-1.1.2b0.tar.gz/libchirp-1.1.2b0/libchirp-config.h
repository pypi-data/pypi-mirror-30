#ifndef ch_global_config_h
#define ch_global_config_h

// Version of chirp.
//
// .. code-block:: cpp
//
#define CH_VERSION "1.0.0-beta"

// Buffer-size when allocating communication buffers, can be overridden in
// :c:type:`ch_config_t`.
//
// .. code-block:: cpp

/* 64k */
#define CH_BUFFER_SIZE 65536

// Minimal buffersize we require when allocating communication buffers.
//
// .. code-block:: cpp

#define CH_MIN_BUFFER_SIZE 1024

// Encryption buffer size. Only change if it doesn't match with your TLS
// library.
//
// .. code-block:: cpp

/* 16k */
#define CH_ENC_BUFFER_SIZE 16384

// Preallocated buffer size for header. If the header is bigger memory will be
// allocated.
//
// .. code-block:: cpp

#define CH_BF_PREALLOC_HEADER 32

// Preallocated buffer size for data. If the data is bigger memory will be
// allocated.
//
// .. code-block:: cpp

#define CH_BF_PREALLOC_DATA 1024

// TCP keep-alive time.
//
// .. code-block:: cpp

#define CH_TCP_KEEPALIVE 60

// Hard limit for message size.  Can be overridden in :c:type:`ch_config_t`.
//
// .. code-block:: cpp

#define CH_MAX_MSG_SIZE 1024 * 1024 * 100 // 100M

// Build chirp without SSL code. The functions from encryption.h become no-ops.
//
// .. code-block:: cpp

/* #define CH_WITHOUT_TLS */

// Logging is done via a macro which is disabled by default. You can enable it
// here for debug purposes.
//
// .. code-block:: cpp

/* #define CH_ENABLE_LOGGING */

// Chirp asserts a lot of conditions. Asserting is done via a macro which is
// disabled by default. You can enable it here for debug purposes.
//
// .. code-block:: cpp

/* #define CH_ENABLE_ASSERTS */

// Log available ciphers. Used to debug connections failures.
//
// .. code-block:: cpp

/* #define CH_CN_PRINT_CIPHERS */

// Disable SIGINT and SIGTERM to close chirp. Used for compatibility with
// existing applications: When you use chirp in an existing application that
// uses SIGINT and SIGTERM signals and the handlers added by chirp somehow
// conflict. Can be overridden in :c:type:`ch_config_t`.
//
// .. code-block:: cpp

/* #define CH_DISABLE_SIGNALS */


#endif // ch_global_config_h
