# Compatibility

Type-only refinements bind to existing hook input/result contracts. Context values, state, service calls and payloads unchanged. Discarded Set ternary becomes if/else preserving condition and single chosen branch before returning Set. Unknown caught value message read uses strict nullish test and Reflect.get(Object(err),message,err), preserving receiver semantics including primitives/accessors/proxies. Unused day-close catch binding removed.

Strict customer array typing exposes possible find(undefined). Explicit undefined guard preserves existing TypeError class before setter/navigation; message is clarified to Debt customer is unavailable. This deliberately does not fix the existing missing-customer behavior. A separate task must decide loading/missing/deleted-customer UX and contract; no hidden non-null assertion or fallback customer.
