# Type sources

- AppCtx -> existing shared Product/Customer/Courier/Invoice/Expense/Payment and navigation/finance contracts; AppScreenContext refines addCustomerAsync/createSaleAsync/closeDayAsync directly from the actual use* hook mutateAsync types in src/lib/db.ts (unchanged).
- React Dispatch<SetStateAction<Customer[]>> types the existing no-op compatibility setter; LucideIcon types actual imported alert icons.
- PaymentDetails derives Omit<CreateSaleInput,items|total>; PaymentSheetProps reuses exact customer/courier/customer mutation context; status options use satisfies Invoice[status]. MoneyDetailsSheet totals use AppCtx[totals].
- Existing extracted screens receive same ctx object and values. No new runtime dependencies. Existing AppCtx loose fields and pre-existing unknown-as conversions remain out of scope, not certified eliminated.
