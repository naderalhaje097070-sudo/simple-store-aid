# Api Compatibility

No application API/RPC/Auth/state/authorization/financial contract changed. Pinned Miniflare official cf-fetch opt-out uses its existing fallbackCf, identical to the failed-network path; app has no request.cf consumer. Tests retain exact named500 and matchingSSR/Auth behavior.
