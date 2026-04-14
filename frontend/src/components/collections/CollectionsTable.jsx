import { Badge, Button } from "../ui/Primitives";
import { TrashIcon } from "../ui/Icons";

const COL_HEADERS = ["Name", "Vector DB", "Vectors", "Dimensions", "Distance", "Docs", "Status", ""];

const STATUS_VARIANT = { green: "green", yellow: "amber", grey: "default", red: "red", unknown: "default" };
function statusVariant(s) {
  const lower = (s ?? "").toLowerCase();
  if (lower === "green" || lower === "ok" || lower === "ready") return "green";
  if (lower === "yellow") return "amber";
  if (lower === "red" || lower === "error") return "red";
  return "default";
}

export function CollectionsTable({ collections, onDelete }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-[rgba(255,255,255,0.04)]">
            {COL_HEADERS.map((h) => (
              <th
                key={h}
                className="text-left text-[10px] font-medium text-[#4d5669] uppercase tracking-widest px-4 py-3 whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {collections.map((col, i) => (
            <CollectionRow key={col.name ?? i} col={col} onDelete={() => onDelete(col.name)} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CollectionRow({ col, onDelete }) {
  return (
    <tr className="border-b border-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.02)] group transition-colors">
      <td className="px-4 py-3 text-[13px] font-semibold text-[#e8eaf0]">
        {col.name}
      </td>
      <td className="px-4 py-3">
        <Badge variant="blue">{col.db}</Badge>
      </td>
      <td className="px-4 py-3 text-[13px] font-mono text-[#e8eaf0]">
        {(col.chunks ?? 0).toLocaleString()}
      </td>
      <td className="px-4 py-3 text-[13px] font-mono text-[#8892a4]">
        {col.dim ? `${col.dim}d` : "—"}
      </td>
      <td className="px-4 py-3">
        <Badge variant="amber">{col.distance || "—"}</Badge>
      </td>
      <td className="px-4 py-3 text-[13px] font-mono text-[#8892a4]">
        {col.docs ?? "—"}
      </td>
      <td className="px-4 py-3">
        <Badge variant={statusVariant(col.status)}>{col.status || "unknown"}</Badge>
      </td>
      <td className="px-4 py-3 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="danger" size="xs" icon={<TrashIcon />} onClick={onDelete}>
          Delete
        </Button>
      </td>
    </tr>
  );
}
