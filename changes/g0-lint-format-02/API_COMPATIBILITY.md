# Compatibility

No interface/type/import/provider/API/RPC contract or Hook dependencies changed. Prettier3.8.3 with existing printWidth100/semi/doublequote/trailingCommaall configuration only. Babel7.29.7 source/type AST and TypeScript5.9.3 emitted runtime AST are compared. JSX strings are cooked with TypeScript, adjacent literal text coalesced only on intrinsic host elements; custom/fragment child segmentation stays distinct. This preserves visible/meaningful text, not emitted bytes or native DOM text-node segmentation.
