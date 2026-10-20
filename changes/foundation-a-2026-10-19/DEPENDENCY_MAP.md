# DEPENDENCY MAP

useInvoices/usePayments/useExpenses -> MongezzApp -> AppCtx -> home/debts/customer/courier/invoice/profit/collected/expense/day-close views and sheets. PDF/print require invoice+payment completeness. useTenant -> billing status; tenantTodayKey -> shared parent/day-close date. Quality -> scripts/lint-changed.sh. New regression entrypoints run in existing Quality/Integrated G0; existing G1 triggered by snapshot.
