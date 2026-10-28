import { useState } from "react";
import { createRoot } from "react-dom/client";
import { QuantityInput } from "@/features/shared/QuantityInput";
import { AddProductSheet } from "@/features/inventory/AddProductSheet";

function Fixture() {
  const [quantity, setQuantity] = useState(1);
  const [saved, setSaved] = useState("");
  if (location.hash === "#product") {
    return (
      <>
        <AddProductSheet onClose={() => {}} onSave={(value) => setSaved(JSON.stringify(value))} />
        <output id="saved">{saved}</output>
      </>
    );
  }
  return (
    <>
      <QuantityInput
        value={quantity}
        onCommit={(value) => {
          if (value > 2) return false;
          setQuantity(value);
          return true;
        }}
      />
      <output id="quantity">{quantity}</output>
      <button>خارج الحقل</button>
    </>
  );
}
createRoot(document.getElementById("root")!).render(<Fixture />);
