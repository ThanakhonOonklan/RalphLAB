"use client";

import { Component, useCallback, useState, type ReactNode } from "react";
import type { Role } from "./agents/workflow";
import LabRoomCanvas from "./LabRoomCanvas";

class SceneBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    if (this.state.failed) {
      return <div role="alert" className="grid h-full place-content-center gap-3 text-center text-sm text-slate-700">
        <p>เปิดห้อง 3D ไม่สำเร็จ กรุณาตรวจว่าเบราว์เซอร์รองรับ WebGL</p>
        <button type="button" className="mx-auto rounded-md border bg-white px-4 py-2" onClick={() => window.location.reload()}>ลองอีกครั้ง</button>
      </div>;
    }
    return this.props.children;
  }
}

export default function LabView() {
  const [followed, setFollowed] = useState<Role | null>(null);
  const [ready, setReady] = useState(false);
  const handleReady = useCallback(() => setReady(true), []);
  const overview = useCallback(() => setFollowed(null), []);
  return <section aria-label="ห้องแล็บ 3D" className="relative min-h-0 overflow-hidden bg-slate-200">
    <SceneBoundary>
      <LabRoomCanvas onReady={handleReady} chatOpen={followed !== null} cameraAgent={followed} onAgentSelect={setFollowed} onStopFollowing={overview} />
      {!ready && <div role="status" className="pointer-events-none absolute inset-0 grid place-items-center text-sm text-slate-600">กำลังโหลดห้องแล็บ…</div>}
      {followed && <button type="button" onClick={overview} className="absolute left-3 top-3 rounded-full border bg-white px-4 py-2 text-sm text-slate-700 shadow-sm">ดูทั้งห้อง</button>}
    </SceneBoundary>
  </section>;
}
