// Compare the committed projection's Row with actual pinned-CLI generated types.
const fs = require("node:fs");
const assert = require("node:assert/strict");
const ts = require("typescript");
function viewRow(file) {
  const source = ts.createSourceFile(
    file,
    fs.readFileSync(file, "utf8"),
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TS,
  );
  assert.equal(source.parseDiagnostics.length, 0, "Type source must parse");
  let node = source.statements.find(
    (n) => ts.isTypeAliasDeclaration(n) && n.name.text === "Database",
  ).type;
  for (const key of ["public", "Views", "day_close_profit_report", "Row"]) {
    assert.ok(ts.isTypeLiteralNode(node), "Expected type literal");
    const field = node.members.find(
      (n) =>
        ts.isPropertySignature(n) && n.name.getText(source).replace(/^['"]|['"]$/g, "") === key,
    );
    assert.ok(field, "Missing report type member: " + key);
    node = field.type;
  }
  return Object.fromEntries(
    node.members
      .map((n) => [
        n.name.getText(source).replace(/^['"]|['"]$/g, ""),
        n.type.getText(source).replace(/\s/g, ""),
      ])
      .sort(([a], [b]) => a.localeCompare(b)),
  );
}
if (require.main === module) {
  assert.equal(process.argv.length, 4, "Pass generated type file and receipt path");
  const actual = viewRow(process.argv[2]);
  assert.deepEqual(
    actual,
    viewRow("src/integrations/supabase/types.ts"),
    "Actual generated view Row differs from committed reader contract",
  );
  fs.writeFileSync(
    process.argv[3],
    JSON.stringify({
      source_sha: process.env.EXPECTED_SOURCE,
      actual_generated_report_row: actual,
      report_row_matches: true,
    }) + "\n",
  );
  console.log("C5_PROFIT_ACTUAL_GENERATED_VIEW_ROW_MATCH");
}
module.exports = { viewRow };
