type Props = {
  columns: string[];
  rows: unknown[][];
};

export default function ResultTable({ columns, rows }: Props) {
  if (rows.length === 0) {
    return <p className="text-gray-500 text-sm mt-4">Nenhum resultado.</p>;
  }

  return (
    <div className="overflow-x-auto rounded border border-gray-800 mt-4">
      <table className="w-full text-sm">
        <thead className="bg-gray-800 text-gray-400">
          <tr>
            {columns.map((col) => (
              <th key={col} className="text-left px-3 py-2 font-medium">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-gray-800 hover:bg-gray-900">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-2 font-mono whitespace-nowrap">
                  {cell === null ? <span className="text-gray-600">null</span> : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
