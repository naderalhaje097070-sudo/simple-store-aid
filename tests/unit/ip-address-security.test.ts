import { expect, test } from "bun:test";
import { Address4, Address6 } from "ip-address";

test("patched IP parser retains IPv4, IPv6 and zone contracts", () => {
  expect(new Address4("192.0.2.1").correctForm()).toBe("192.0.2.1");
  expect(new Address6("2001:db8::1").correctForm()).toBe("2001:db8::1");
  expect(new Address6("fe80::1%eth0").zone).toBe("%eth0");
  expect(Address6.isValid("not-an-address")).toBe(false);
});

test("zone-heavy malformed inputs are rejected across all line terminators", () => {
  for (const end of ["\n", "\r", "\u2028", "\u2029"]) {
    expect(Address6.isValid("%".repeat(100_000) + end)).toBe(false);
  }
}, 3_000);
