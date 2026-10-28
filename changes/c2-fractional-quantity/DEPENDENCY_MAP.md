# Dependencies

AddProductSheet→parseQuantityText/isQuantity→current product hooks→products RLS/CHECK. Both existing SaleScreen/QuickSale carts→QuantityInput and common quantity step/sum→useCreateSale→legacy SQL RPC→product row lock/order item/stock update/payment.

Legacy SQL sale body is derived from accepted October20261010223557. Only v_qty typemod and raw quantity guard change. Existing return_courier_order/delete_order_with_restore_stock read the same numeric qty and add it back to numeric stock. Future C3canonical core must retain these guards when composing old49/50; C2does not claim that unresolved composition is fixed. Both frozen A/B manifests remain unchanged; C2's explicit source inventory records intentional current-source differences without weakening historical gates.
