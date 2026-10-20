# Dependency map

MongezzApp useCustomers query -> existing isLoading -> local AppScreenContext presentation flag -> DebtsScreen/DebtCustomerScreen. Shared AppCtx, useCustomers data contract, query key/options, mutations and domain finance selectors unchanged. DebtCustomerScreen uses existing openCustomerId for invoice identity even when the name record is absent. Existing TopBar/Money/EmptyState and invoice-detail navigation reused. No new libraries or provider contract.
