# Dependency map

Original lock: react-start1.167.50 -> start-server-core1.167.22 (affected). react-start's published patched1.168.60 requires react-router1.170.41 and start-server-core1.169.39 through its exact upstream graph. Use upstream version-specific dependencies, not equal version numbers for every TanStack package.

Lovable vite-tanstack-config2.9.1 declares react-start>=1.100.0, Vite>=5<9 and Nitro>=3.0.260603-beta. Keep it and unrelated root dependencies unchanged. Preserve Seroval overrides and bunfig supply-chain policy. Verify all resolved copies in generated lock and installed graph.

Source of version evidence: official npm registry manifests and https://github.com/TanStack/router/security/advisories/GHSA-qx66-fv34-fjm8 . Transitive packages can change only as required by the patched published graph; review generated diff.

## Final serializer correction

Keep the override mechanism and seroval-plugins policy; raise Seroval itself to exact1.6.7 in devDependencies, overrides and resolutions. The old ^1.5.6 policy retained1.5.6, violating the patched framework's published ^1.6.7 minimum and GHSA-p6vx-979v-rg4c boundary. Final graph and all installed affected copies are recorded in evidence.json. No unrelated root framework/Lovable upgrade.
