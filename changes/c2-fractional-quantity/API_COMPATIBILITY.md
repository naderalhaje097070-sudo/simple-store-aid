# API

No RPC signature/result or generated TypeScript scalar shape changes: stock/qty remain JSON numbers and generated number types. Existing integer values remain accepted. New behavior: fractional stock persists exactly at the already supported two-decimal item precision; unsupported precision rejects instead of silent numeric/int coercion. Raw quantity guards precede any financial write. Old customer/courier rules remain unchanged until the separately planned C3/interface composition.

QuantityInput commits a validated draft on blur/Enter; rejected input restores the current value and shows a visible accessible error. New identical operations/idempotency behavior not changed. UI stock cap100000 remains its existing cap; server/database numeric bound follows current item precision. Weights/metres use the entered unit consistently; unit conversion is not introduced.
