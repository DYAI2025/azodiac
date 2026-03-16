'use client';

import { useState, useCallback } from 'react';
import FusionRingScene from './components/fusion-ring-scene';
import BirthInputPanel from './components/birth-input-panel';
import type { FusionRingProfile } from './components/fusion-ring-profile';

export default function Home() {
  const [profile, setProfile] = useState<FusionRingProfile | undefined>();

  const handleProfileChange = useCallback((p: FusionRingProfile) => {
    setProfile(p);
  }, []);

  return (
    <main className="relative w-screen h-screen bg-black">
      <FusionRingScene initialProfile={profile} />
      <BirthInputPanel onProfileChange={handleProfileChange} />
    </main>
  );
}
