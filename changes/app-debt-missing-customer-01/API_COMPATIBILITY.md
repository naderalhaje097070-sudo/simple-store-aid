# Compatibility

useCustomers signature/result and all shared data/mutation contracts unchanged. Local AppScreenContext adds a required boolean derived from ReturnType<typeof useCustomers>[isLoading] and populated directly from the existing hook call. It is presentation state only. Present-customer setter/navigation order unchanged. Missing-customer UI intentionally changes from throw/false-zero to unavailable or loading status, preserved amounts, disabled invalid actions and Back. Query pending/error state is not inferred from array length, and no deletion diagnosis is made.
