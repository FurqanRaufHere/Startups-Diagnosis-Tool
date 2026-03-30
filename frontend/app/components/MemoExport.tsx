"use client";

type MemoExportProps = {
  startupName: string;
  memoText: string;
};

export default function MemoExport({ startupName, memoText }: MemoExportProps) {
  function downloadMemo() {
    if (!memoText) return;

    const blob = new Blob([memoText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${startupName || "startup"}-memo.txt`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <article className="memo card">
      <h2>Investment Memo</h2>
      <p>Export the generated memo as a text snapshot.</p>
      <button onClick={downloadMemo} disabled={!memoText}>
        Download Memo
      </button>
    </article>
  );
}
